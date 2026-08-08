#!/usr/bin/env python3
"""Backfill posts (or comments) from the Arctic Shift API for active subreddits.

PullPush.io has a data gap (no data after ~May 2025), so this script uses
Arctic Shift (arctic-shift.photon-reddit.com) which has current data. The
file was originally named `backfill_pullpush.py`; renamed 2026-05-19.

Arctic Shift API constraints:
  - Max 100 results per request
  - Paginate by advancing the `after` parameter using the last item's created_utc
  - No documented rate limit, but we add a polite delay between requests

Default range: Jan 1 2023 to today.

Comments mode (--comments) fetches comments by *comment* creation time and
attaches them to posts already in the DB (orphans whose post we never
collected are dropped). It skips exclude_from_keywords subreddits, mirroring
the daily Reddit comment-collection scope.

Usage:
    python scripts/backfill_arctic.py
    python scripts/backfill_arctic.py --since 2024-01-01
    python scripts/backfill_arctic.py --subreddit replika
    python scripts/backfill_arctic.py --comments --since 2026-05-24
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
from src.db.operations import insert_posts, insert_comments
from scripts.collect_comments import BOT_AUTHORS, EXCLUDED_SUBREDDITS

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
COMMENTS_API_BASE = "https://arctic-shift.photon-reddit.com/api/comments/search"
USER_AGENT = "ai-companion-tracker/1.0 (research project; backfill)"
BATCH_SIZE = 100
REQUEST_DELAY = 2.0  # seconds between requests

# Statuses that mean "the server is busy, try again", not "your request is bad".
# Arctic Shift signals overload with HTTP 422 and the body
# {"data": null, "error": "Timeout. Maybe slow down a bit"} — confirmed by
# probe on 2026-08-07. It is NOT a validation error and NOT a pagination-depth
# limit: a cold single-sub walk reaches 8900+ items fine, while the daily run
# (40 subs back to back) trips it partway through the busiest subs.
RETRYABLE_STATUS = (422, 429, 500, 502, 503, 504)


def fetch_posts(subreddit: str, after_epoch: int, before_epoch: int,
                on_batch=None) -> "tuple[list[dict], bool]":
    """Fetch all posts for a subreddit in a time window, paginating automatically.

    Returns (posts, truncated). `truncated` is True when the window ended
    abnormally (non-200, exhausted retries) — callers must treat the window
    as incomplete rather than silently accepting partial data.

    If `on_batch` is provided, it's called with each new batch as it arrives —
    use this for incremental DB inserts so crashes don't lose work. on_batch
    failures propagate: an insert error is a DB problem, not a skippable blip.
    """
    return _fetch_window(API_BASE, subreddit, after_epoch, before_epoch, on_batch)


def fetch_comments(subreddit: str, after_epoch: int, before_epoch: int,
                   on_batch=None) -> "tuple[list[dict], bool]":
    """Fetch all comments *created* in a time window for a subreddit.

    Window is over comment creation time, not parent-post age: run daily and
    every comment is eventually captured no matter how old its post is.
    Same (items, truncated) contract as fetch_posts.
    """
    return _fetch_window(COMMENTS_API_BASE, subreddit, after_epoch, before_epoch, on_batch)


def _fetch_window(api_base: str, subreddit: str, after_epoch: int, before_epoch: int,
                  on_batch=None) -> "tuple[list[dict], bool]":
    all_posts = []
    cursor = after_epoch
    retries = 0
    max_retries = 5
    truncated = False

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
                api_base,
                params=params,
                headers={"User-Agent": USER_AGENT},
                timeout=30,
            )
        except requests.RequestException as e:
            retries += 1
            if retries > max_retries:
                logger.error("  r/%s: gave up after %d network errors — window TRUNCATED", subreddit, max_retries)
                truncated = True
                break
            logger.warning("  Network error fetching r/%s (retry %d): %s", subreddit, retries, e)
            time.sleep(5 * retries)
            continue

        # Retry transient overload instead of abandoning the window. Before
        # 2026-08-07 only 429 was retried and every other non-200 ended the
        # walk immediately, so a single 422 "slow down a bit" cost a whole
        # subreddit's day — r/ClaudeAI went 4 days with no comments that way.
        if resp.status_code in RETRYABLE_STATUS:
            retries += 1
            detail = resp.text[:120].replace("\n", " ")
            if retries > max_retries:
                logger.error("  r/%s: HTTP %d after %d retries — window TRUNCATED (%s)",
                             subreddit, resp.status_code, max_retries, detail)
                truncated = True
                break
            wait = 60 if resp.status_code == 429 else min(15 * retries, 90)
            logger.warning("  r/%s: HTTP %d — backing off %ds (retry %d/%d): %s",
                           subreddit, resp.status_code, wait, retries, max_retries, detail)
            time.sleep(wait)
            continue

        if resp.status_code != 200:
            logger.warning("  HTTP %d for r/%s — window TRUNCATED", resp.status_code, subreddit)
            truncated = True
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

        # Incremental insert so a crash doesn't lose all work
        if on_batch is not None:
            on_batch(posts)

        if len(posts) < BATCH_SIZE:
            break  # Last page

        time.sleep(REQUEST_DELAY)

    return all_posts, truncated


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


def parse_arctic_comment(c: dict) -> dict:
    """Convert an Arctic Shift comment dict to our comments-table schema.

    parent_id semantics mirror collect_comments._extract_parent_id: None when
    the parent is the post itself, bare comment id otherwise. True depth isn't
    recoverable from the archive's flat listing, so replies get depth=1
    (the column is stored but not used by any analysis).
    """
    link_id = c.get("link_id") or ""
    post_id = link_id[3:] if link_id.startswith("t3_") else link_id
    parent_raw = c.get("parent_id") or ""
    if parent_raw.startswith("t1_"):
        parent_id = parent_raw[3:]
        depth = 1
    else:
        parent_id = None
        depth = 0
    return {
        "id": c.get("id", ""),
        "post_id": post_id,
        "subreddit": c.get("subreddit", ""),
        "author": c.get("author"),
        "body": c.get("body", ""),
        "score": c.get("score", 0),
        "depth": depth,
        "parent_id": parent_id,
        "created_utc": int(c.get("created_utc") or 0),
        "permalink": c.get("permalink", ""),
    }


def filter_comments(raw: "list[dict]") -> "list[dict]":
    """Drop bot and deleted/removed comments — same rules as the Reddit path."""
    return [
        c for c in raw
        if c.get("author") not in BOT_AUTHORS
        and (c.get("body") or "") not in ("[deleted]", "[removed]")
    ]


def insert_comments_for_known_posts(parsed: "list[dict]", subreddit: str,
                                    conn: sqlite3.Connection) -> "tuple[int, int]":
    """Insert parsed comments whose parent post exists in the posts table.

    Comments on posts we never collected (removed before collection, or
    pre-corpus) are dropped, matching the Reddit path which only ever fetched
    comments for posts already in the DB. Returns (inserted, orphans_dropped).
    """
    for c in parsed:
        c["subreddit"] = subreddit  # force canonical casing, as for posts
    post_ids = list({c["post_id"] for c in parsed if c["post_id"]})
    known = set()
    CHUNK = 500
    for i in range(0, len(post_ids), CHUNK):
        chunk = post_ids[i:i + CHUNK]
        ph = ",".join("?" for _ in chunk)
        known.update(
            r[0] for r in conn.execute(
                f"SELECT id FROM posts WHERE id IN ({ph})", chunk
            ).fetchall()
        )
    keep = [c for c in parsed if c["post_id"] in known]
    inserted = insert_comments(keep, conn=conn)
    conn.commit()
    return inserted, len(parsed) - len(keep)


def backfill_comments_subreddit(subreddit: str, after_epoch: int, before_epoch: int,
                                conn: sqlite3.Connection) -> dict:
    """Backfill one subreddit's comments by comment-creation window."""
    after_date = datetime.fromtimestamp(after_epoch).strftime("%Y-%m-%d")
    before_date = datetime.fromtimestamp(before_epoch).strftime("%Y-%m-%d")
    logger.info("Backfilling COMMENTS for r/%s (%s to %s)...", subreddit, after_date, before_date)

    conn.execute("PRAGMA busy_timeout = 60000")

    total_fetched = 0
    total_inserted = 0
    total_orphans = 0

    def on_batch(batch: "list[dict]") -> None:
        nonlocal total_fetched, total_inserted, total_orphans
        parsed = [parse_arctic_comment(c) for c in filter_comments(batch)]
        inserted, orphans = insert_comments_for_known_posts(parsed, subreddit, conn)
        total_fetched += len(batch)
        total_inserted += inserted
        total_orphans += orphans

    _, truncated = fetch_comments(subreddit, after_epoch, before_epoch, on_batch=on_batch)

    if truncated:
        logger.warning("  r/%s: comment window TRUNCATED — re-run this window (%s to %s)",
                       subreddit, after_date, before_date)

    logger.info("  r/%s: %d comments fetched, %d new inserted, %d orphans dropped",
                subreddit, total_fetched, total_inserted, total_orphans)

    return {"subreddit": subreddit, "fetched": total_fetched, "inserted": total_inserted,
            "orphans": total_orphans, "truncated": truncated}


def backfill_subreddit(subreddit: str, after_epoch: int, before_epoch: int, conn: sqlite3.Connection) -> dict:
    """Backfill one subreddit. Returns summary dict.

    Inserts incrementally (every BATCH_SIZE posts) so crashes don't lose work.
    Sets busy_timeout on the connection so concurrent writers don't immediately fail.
    """
    after_date = datetime.fromtimestamp(after_epoch).strftime("%Y-%m-%d")
    before_date = datetime.fromtimestamp(before_epoch).strftime("%Y-%m-%d")
    logger.info("Backfilling r/%s (%s to %s)...", subreddit, after_date, before_date)

    # Ensure connection has a busy_timeout for concurrent-writer resilience
    conn.execute("PRAGMA busy_timeout = 60000")

    total_fetched = 0
    total_inserted = 0

    def on_batch(batch_posts: list[dict]) -> None:
        nonlocal total_fetched, total_inserted
        parsed = [parse_arctic_post(p) for p in batch_posts]
        # Arctic Shift can return non-canonical subreddit casing (e.g. "antiai");
        # case-sensitive IN(...) filters downstream silently drop such rows, so
        # force the canonical config name.
        for p in parsed:
            p["subreddit"] = subreddit
        inserted = insert_posts(parsed, conn=conn)
        conn.commit()
        total_fetched += len(parsed)
        total_inserted += inserted

    raw_posts, truncated = fetch_posts(subreddit, after_epoch, before_epoch, on_batch=on_batch)

    if truncated:
        logger.warning("  r/%s: window TRUNCATED — re-run this window (%s to %s)",
                       subreddit, after_date, before_date)

    if not raw_posts:
        logger.info("  r/%s: no posts found", subreddit)
        return {"subreddit": subreddit, "fetched": 0, "inserted": 0, "truncated": truncated}

    logger.info("  r/%s: %d fetched, %d new inserted",
                subreddit, total_fetched, total_inserted)

    return {"subreddit": subreddit, "fetched": total_fetched, "inserted": total_inserted, "truncated": truncated}


def _ensure_file_logging():
    """Attach the backfill.log handler explicitly.

    Importing scripts.collect_comments (for the shared bot/exclusion lists)
    runs its logging.basicConfig first, which turns this module's basicConfig
    into a no-op — without this, script runs log to console only.
    """
    root = logging.getLogger()
    if any(getattr(h, "baseFilename", "") == str(LOG_FILE) for h in root.handlers):
        return
    fh = logging.FileHandler(str(LOG_FILE), mode="a")
    fh.setFormatter(logging.Formatter(
        "%(asctime)s %(levelname)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S",
    ))
    root.addHandler(fh)


def main():
    _ensure_file_logging()
    parser = argparse.ArgumentParser(description="Backfill posts from Arctic Shift API")
    parser.add_argument("--since", type=str, default="2023-01-01",
                        help="Start date YYYY-MM-DD (default: 2023-01-01)")
    parser.add_argument("--until", type=str, default=None,
                        help="End date YYYY-MM-DD (default: today)")
    parser.add_argument("--subreddit", type=str,
                        help="Backfill a single subreddit instead of all")
    parser.add_argument("--comments", action="store_true",
                        help="Backfill comments (by comment creation time) instead of posts")
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
        if args.comments:
            # Mirror the daily comment-collection scope (T4 / NSFW-excluded
            # subs never get comments collected, so don't backfill them).
            subreddits = [s for s in subreddits if s not in EXCLUDED_SUBREDDITS]

    after_str = datetime.fromtimestamp(after_epoch).strftime("%Y-%m-%d")
    before_str = datetime.fromtimestamp(before_epoch).strftime("%Y-%m-%d")
    logger.info("=" * 60)
    logger.info("BACKFILL START (%s): %d subreddit(s), %s to %s",
                "comments" if args.comments else "posts", len(subreddits), after_str, before_str)
    logger.info("Log file: %s", LOG_FILE)
    logger.info("=" * 60)

    results = []
    for i, sub in enumerate(subreddits, 1):
        logger.info("[%d/%d] Starting r/%s", i, len(subreddits), sub)
        if args.comments:
            result = backfill_comments_subreddit(sub, after_epoch, before_epoch, conn)
        else:
            result = backfill_subreddit(sub, after_epoch, before_epoch, conn)
        results.append(result)

    conn.close()

    # Summary
    total_fetched = sum(r["fetched"] for r in results)
    total_inserted = sum(r["inserted"] for r in results)
    empty = [r["subreddit"] for r in results if r["fetched"] == 0]
    truncated_subs = [r["subreddit"] for r in results if r.get("truncated")]
    if truncated_subs:
        logger.warning("  TRUNCATED windows (re-run these): %s", ", ".join(truncated_subs))

    item_word = "comments" if args.comments else "posts"
    logger.info("=" * 60)
    logger.info("BACKFILL COMPLETE")
    logger.info("  Total fetched:  %d %s", total_fetched, item_word)
    logger.info("  Total inserted: %d new %s", total_inserted, item_word)
    logger.info("  Subreddits:     %d/%d had data", len(subreddits) - len(empty), len(subreddits))

    if empty:
        logger.warning("  No posts found for: %s", ", ".join(empty))

    for r in sorted(results, key=lambda x: x["fetched"], reverse=True):
        logger.info("    r/%-25s  fetched=%5d  inserted=%5d", r["subreddit"], r["fetched"], r["inserted"])

    logger.info("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
