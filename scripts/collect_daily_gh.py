#!/usr/bin/env python3
"""Lightweight daily collection for GitHub Actions.

Fetches Reddit data, scans for keywords, and merges results into the
existing JSON files in the repo. Does NOT require the 22GB SQLite database.

Flow:
  1. Fetch about.json + new.json for each subreddit
  2. Calculate snapshot metrics
  3. Scan posts for keyword matches
  4. Merge new snapshots into data/snapshots.json
  5. Update data/subreddits.json with latest metadata
  6. Merge keyword counts into data/keyword_trends.json
  7. Copy updated JSON to web/data/

Usage:
    python scripts/collect_daily_gh.py
"""

import json
import logging
import re
import shutil
import sys
import time
from collections import defaultdict
from datetime import date, datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import load_communities, load_keywords, load_keyword_communities
from src.reddit_client import RedditClient, RedditError, SubredditNotFound, SubredditForbidden
from src.utils.rate_limiter import RateLimiter

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent.parent / "data"
WEB_DATA_DIR = Path(__file__).parent.parent / "web" / "data"

TODAY = date.today().isoformat()


# ── Reddit fetching ──

def fetch_subreddit(client: RedditClient, subreddit: str) -> dict | None:
    """Fetch about + new listings for a subreddit. Returns snapshot dict or None."""
    try:
        about = client.get_about(subreddit)  # Returns data dict directly
    except (SubredditNotFound, SubredditForbidden) as e:
        logger.warning("r/%s: %s", subreddit, e)
        return None
    except RedditError as e:
        logger.warning("r/%s: fetch error: %s", subreddit, e)
        return None

    try:
        children = client.get_new(subreddit, limit=100)  # Returns children list directly
    except RedditError as e:
        logger.warning("r/%s: listing error: %s", subreddit, e)
        children = []

    # Calculate metrics
    posts = [c.get("data", {}) for c in children]
    now_utc = datetime.now(timezone.utc).timestamp()
    cutoff = now_utc - 86400
    posts_today = sum(1 for p in posts if (p.get("created_utc") or 0) >= cutoff)

    comment_counts = [p["num_comments"] for p in posts if p.get("num_comments") is not None]
    score_values = [p["score"] for p in posts if p.get("score") is not None]
    authors = {p["author"] for p in posts if p.get("author") and p["author"] != "[deleted]"}

    snapshot = {
        "subreddit": subreddit,
        "snapshot_date": TODAY,
        "data_source": "json_endpoint",
        "subscribers": about.get("subscribers"),
        "active_users": about.get("active_user_count"),
        "visitors_7d": about.get("visitors_7d"),
        "contributions_7d": about.get("contributions_7d"),
        "posts_today": posts_today,
        "avg_comments_per_post": round(sum(comment_counts) / len(comment_counts), 2) if comment_counts else None,
        "avg_score_per_post": round(sum(score_values) / len(score_values), 2) if score_values else None,
        "unique_authors": len(authors),
    }

    return {"snapshot": snapshot, "posts": posts, "children": children}


# ── Keyword scanning ──

def build_keyword_patterns(categories: list[dict]) -> list[tuple[str, str, re.Pattern]]:
    """Build compiled regex patterns from keyword categories."""
    patterns = []
    for cat in categories:
        name = cat["name"]
        for term in cat["terms"]:
            # Strip comments
            clean = term.split("#")[0].strip().strip('"').strip("'")
            if not clean:
                continue
            if " " in clean:
                # Multi-word phrase: match as substring
                pat = re.compile(re.escape(clean), re.IGNORECASE)
            else:
                # Single word: match with word boundaries
                pat = re.compile(r'\b' + re.escape(clean) + r'\b', re.IGNORECASE)
            patterns.append((name, clean, pat))
    return patterns


def scan_posts_for_keywords(posts: list[dict], patterns: list[tuple]) -> dict[str, set[str]]:
    """Scan posts against keyword patterns. Returns {category: set of post IDs that matched}."""
    hits: dict[str, set[str]] = defaultdict(set)
    for post in posts:
        text = " ".join(filter(None, [post.get("title", ""), post.get("selftext", "")]))
        if not text:
            continue
        post_id = post.get("id", "")
        for cat_name, term, pattern in patterns:
            if pattern.search(text):
                hits[cat_name].add(post_id)
    return hits


# ── JSON merging ──

def merge_snapshots(new_snapshots: list[dict]) -> None:
    """Merge new snapshot entries into snapshots.json."""
    path = DATA_DIR / "snapshots.json"
    existing = json.loads(path.read_text()) if path.exists() else []

    # Remove any existing entries for today's date (idempotent re-runs)
    existing_subs_today = {
        (e["subreddit"], e["snapshot_date"])
        for e in existing
        if e["snapshot_date"] == TODAY
    }

    # Only add snapshots not already present
    added = 0
    for snap in new_snapshots:
        key = (snap["subreddit"], snap["snapshot_date"])
        if key not in existing_subs_today:
            existing.append(snap)
            added += 1

    # Sort for consistency
    existing.sort(key=lambda x: (x["snapshot_date"], x["subreddit"]))
    path.write_text(json.dumps(existing, indent=2))
    logger.info("snapshots.json: %d new entries added (%d total)", added, len(existing))


def update_subreddits(new_snapshots: list[dict], communities: list[dict]) -> None:
    """Update subreddits.json with latest snapshot metadata."""
    path = DATA_DIR / "subreddits.json"

    # Build lookup from communities config
    config_map = {c["subreddit"]: c for c in communities}

    entries = []
    for snap in new_snapshots:
        sub = snap["subreddit"]
        conf = config_map.get(sub, {})
        entries.append({
            "subreddit": sub,
            "snapshot_date": snap["snapshot_date"],
            "subscribers": snap["subscribers"],
            "active_users": snap["active_users"],
            "posts_today": snap["posts_today"],
            "avg_comments_per_post": snap["avg_comments_per_post"],
            "avg_score_per_post": snap["avg_score_per_post"],
            "unique_authors": snap["unique_authors"],
            "category": conf.get("category", ""),
            "tier": conf.get("tier", 0),
            "display_name": conf.get("display_name", sub),
        })

    entries.sort(key=lambda x: x["subreddit"])
    path.write_text(json.dumps(entries, indent=2))
    logger.info("subreddits.json: updated with %d entries", len(entries))


def merge_keyword_trends(keyword_hits: dict[str, int], total_posts: int) -> None:
    """Merge today's keyword counts into keyword_trends.json."""
    path = DATA_DIR / "keyword_trends.json"
    existing = json.loads(path.read_text()) if path.exists() else {}

    for category, count in keyword_hits.items():
        if category not in existing:
            existing[category] = []

        entries = existing[category]

        # Remove today's entry if exists (idempotent)
        entries = [e for e in entries if e["date"] != TODAY]

        # Calculate 7-day average using last 6 entries + today
        recent = [e["count"] for e in entries[-6:]] + [count]
        avg = round(sum(recent) / len(recent), 2)

        entries.append({
            "date": TODAY,
            "count": count,
            "count_7d_avg": avg,
        })
        existing[category] = entries

    # Update total posts
    if "_total_posts" not in existing:
        existing["_total_posts"] = []
    tp_entries = [e for e in existing["_total_posts"] if e["date"] != TODAY]
    tp_entries.append({"date": TODAY, "count": total_posts})
    existing["_total_posts"] = tp_entries

    path.write_text(json.dumps(existing, indent=2))
    logger.info("keyword_trends.json: merged %d category counts for %s", len(keyword_hits), TODAY)


def copy_to_web():
    """Copy data/*.json to web/data/ for Vercel."""
    WEB_DATA_DIR.mkdir(parents=True, exist_ok=True)
    for name in ("snapshots.json", "subreddits.json", "keywords.json", "keyword_trends.json"):
        src = DATA_DIR / name
        if src.exists():
            shutil.copy2(src, WEB_DATA_DIR / name)
    logger.info("Copied JSON to web/data/")


# ── Main ──

def main():
    communities = load_communities()
    logger.info("Loaded %d active communities", len(communities))

    client = RedditClient(rate_limiter=RateLimiter(min_interval=6.0))

    # Keyword setup
    keyword_categories = load_keywords()
    patterns = build_keyword_patterns(keyword_categories)
    keyword_subs = {c["subreddit"] for c in load_keyword_communities()}
    logger.info("Loaded %d keyword patterns, %d keyword-eligible subs", len(patterns), len(keyword_subs))

    # Collect
    new_snapshots = []
    all_keyword_hits: dict[str, set[str]] = defaultdict(set)
    total_posts_today = 0
    errors = []

    for community in communities:
        subreddit = community["subreddit"]
        logger.info("Collecting r/%s", subreddit)

        result = fetch_subreddit(client, subreddit)
        if result is None:
            errors.append(subreddit)
            continue

        new_snapshots.append(result["snapshot"])

        # Keyword scan (T1-T3 only)
        if subreddit in keyword_subs and result["posts"]:
            hits = scan_posts_for_keywords(result["posts"], patterns)
            for cat, post_ids in hits.items():
                all_keyword_hits[cat] |= post_ids
            total_posts_today += len(result["posts"])

            hit_summary = {cat: len(ids) for cat, ids in hits.items() if ids}
            if hit_summary:
                logger.info("  r/%s: keyword hits: %s", subreddit, hit_summary)

    # Merge into JSON
    logger.info("Merging %d snapshots into JSON...", len(new_snapshots))
    merge_snapshots(new_snapshots)
    update_subreddits(new_snapshots, communities)

    # Keyword trends
    keyword_counts = {cat: len(ids) for cat, ids in all_keyword_hits.items()}
    if keyword_counts:
        merge_keyword_trends(keyword_counts, total_posts_today)

    # Copy to web/
    copy_to_web()

    # Summary
    logger.info(
        "Done. %d/%d subreddits collected, %d errors.",
        len(new_snapshots), len(communities), len(errors),
    )
    if errors:
        logger.warning("Failed: %s", ", ".join(errors))

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
