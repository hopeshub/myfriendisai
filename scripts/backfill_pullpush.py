#!/usr/bin/env python3
"""Backfill posts from Arctic Shift API for all active subreddits.

PullPush.io has a data gap (no data after ~May 2025), so this script uses
Arctic Shift (arctic-shift.photon-reddit.com) which has current data.

Arctic Shift API constraints:
  - Max 100 results per request
  - Paginate by advancing the `after` parameter using the last post's created_utc
  - No documented rate limit, but we add a polite delay between requests

Default range: Jan 1 2023 to today.

Usage:
    python scripts/backfill_pullpush.py
    python scripts/backfill_pullpush.py --since 2024-01-01
    python scripts/backfill_pullpush.py --subreddit replika
"""

import argparse
import json
import logging
import sqlite3
import sys
import time
from datetime import date, datetime, timezone
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import load_communities
from src.db.schema import initialize as init_db
from src.db.operations import insert_posts

LOG_FILE = Path(__file__).parent.parent / "backfill.log"

# Log to both console and file
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(str(LOG_FILE), mode="a"),
    ],
)
logger = logging.getLogger(__name__)

API_BASE = "https://arctic-shift.photon-reddit.com/api/posts/search"
USER_AGENT = "ai-companion-tracker/1.0 (research project; backfill)"
BATCH_SIZE = 100
REQUEST_DELAY = 2.0  # seconds between requests


def fetch_posts(subreddit: str, after_epoch: int, before_epoch: int) -> list[dict]:
    """Fetch all posts for a subreddit in a time window, paginating automatically."""
    all_posts = []
    cursor = after_epoch
    retries = 0
    max_retries = 5

    while cursor < before_epoch:
        params = {
            "subreddit": subreddit,
            "after": cursor,
            "before": before_epoch,
            "limit": BATCH_SIZE,
            "sort": "asc",
        }

        try:
            resp = requests.get(
                API_BASE,
                params=params,
                headers={"User-Agent": USER_AGENT},
                timeout=30,
            )
        except requests.RequestException as e:
            retries += 1
            if retries > max_retries:
                logger.error("  r/%s: gave up after %d network errors", subreddit, max_retries)
                break
            logger.warning("  Network error fetching r/%s (retry %d): %s", subreddit, retries, e)
            time.sleep(5 * retries)
            continue

        if resp.status_code == 429:
            logger.warning("  Rate limited, backing off 60s...")
            time.sleep(60)
            continue

        if resp.status_code != 200:
            logger.warning("  HTTP %d for r/%s, skipping batch", resp.status_code, subreddit)
            break

        retries = 0  # reset on success
        data = resp.json()
        posts = data.get("data") or []

        if not posts:
            break

        all_posts.extend(posts)

        # Advance cursor past the last post's timestamp
        last_ts = posts[-1].get("created_utc", 0)
        if last_ts <= cursor:
            cursor += 1
        else:
            cursor = last_ts

        cursor_date = datetime.fromtimestamp(cursor).strftime("%Y-%m-%d")
        logger.info("    r/%s: fetched %d (total: %d, at: %s)",
                     subreddit, len(posts), len(all_posts), cursor_date)

        if len(posts) < BATCH_SIZE:
            break  # Last page

        time.sleep(REQUEST_DELAY)

    return all_posts


def parse_arctic_post(p: dict) -> dict:
    """Convert an Arctic Shift post dict to our DB schema format."""
    created_utc = p.get("created_utc")
    if created_utc:
        collected = datetime.fromtimestamp(created_utc, tz=timezone.utc).strftime("%Y-%m-%d")
    else:
        collected = date.today().isoformat()

    return {
        "id": p.get("id", ""),
        "subreddit": p.get("subreddit", ""),
        "title": p.get("title", ""),
        "author": p.get("author", ""),
        "created_utc": created_utc,
        "score": p.get("score"),
        "num_comments": p.get("num_comments"),
        "upvote_ratio": p.get("upvote_ratio"),
        "is_self": bool(p.get("is_self")),
        "selftext": p.get("selftext", ""),
        "url": p.get("url", ""),
        "collected_date": collected,
        "data_source": "arctic_shift",
        "raw_json": json.dumps(p),
    }


def backfill_subreddit(subreddit: str, after_epoch: int, before_epoch: int, conn: sqlite3.Connection) -> dict:
    """Backfill one subreddit. Returns summary dict."""
    after_date = datetime.fromtimestamp(after_epoch).strftime("%Y-%m-%d")
    before_date = datetime.fromtimestamp(before_epoch).strftime("%Y-%m-%d")
    logger.info("Backfilling r/%s (%s to %s)...", subreddit, after_date, before_date)

    raw_posts = fetch_posts(subreddit, after_epoch, before_epoch)

    if not raw_posts:
        logger.info("  r/%s: no posts found", subreddit)
        return {"subreddit": subreddit, "fetched": 0, "inserted": 0}

    parsed = [parse_arctic_post(p) for p in raw_posts]
    inserted = insert_posts(parsed, conn=conn)

    logger.info("  r/%s: %d fetched, %d new inserted",
                subreddit, len(parsed), inserted)

    return {"subreddit": subreddit, "fetched": len(parsed), "inserted": inserted}


def main():
    parser = argparse.ArgumentParser(description="Backfill posts from Arctic Shift API")
    parser.add_argument("--since", type=str, default="2023-01-01",
                        help="Start date YYYY-MM-DD (default: 2023-01-01)")
    parser.add_argument("--until", type=str, default=None,
                        help="End date YYYY-MM-DD (default: today)")
    parser.add_argument("--subreddit", type=str,
                        help="Backfill a single subreddit instead of all")
    args = parser.parse_args()

    after_epoch = int(datetime.strptime(args.since, "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp())
    if args.until:
        before_epoch = int(datetime.strptime(args.until, "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp())
    else:
        before_epoch = int(time.time())

    conn = init_db()

    if args.subreddit:
        subreddits = [args.subreddit]
    else:
        communities = load_communities()
        subreddits = [c["subreddit"] for c in communities]

    after_str = datetime.fromtimestamp(after_epoch).strftime("%Y-%m-%d")
    before_str = datetime.fromtimestamp(before_epoch).strftime("%Y-%m-%d")
    logger.info("=" * 60)
    logger.info("BACKFILL START: %d subreddit(s), %s to %s", len(subreddits), after_str, before_str)
    logger.info("Log file: %s", LOG_FILE)
    logger.info("=" * 60)

    results = []
    for i, sub in enumerate(subreddits, 1):
        logger.info("[%d/%d] Starting r/%s", i, len(subreddits), sub)
        result = backfill_subreddit(sub, after_epoch, before_epoch, conn)
        results.append(result)

    conn.close()

    # Summary
    total_fetched = sum(r["fetched"] for r in results)
    total_inserted = sum(r["inserted"] for r in results)
    empty = [r["subreddit"] for r in results if r["fetched"] == 0]

    logger.info("=" * 60)
    logger.info("BACKFILL COMPLETE")
    logger.info("  Total fetched:  %d posts", total_fetched)
    logger.info("  Total inserted: %d new posts", total_inserted)
    logger.info("  Subreddits:     %d/%d had data", len(subreddits) - len(empty), len(subreddits))

    if empty:
        logger.warning("  No posts found for: %s", ", ".join(empty))

    for r in sorted(results, key=lambda x: x["fetched"], reverse=True):
        logger.info("    r/%-25s  fetched=%5d  inserted=%5d", r["subreddit"], r["fetched"], r["inserted"])

    logger.info("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
