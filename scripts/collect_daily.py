#!/usr/bin/env python3
"""Daily collection entry point.

Loads communities from config, collects Reddit data for each, stores in SQLite,
and exports frontend-ready JSON files.

Usage:
    python scripts/collect_daily.py
"""

import logging
import sys
from pathlib import Path

# Allow running from the project root
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import load_communities
from src.reddit_client import RedditClient
from src.utils.rate_limiter import RateLimiter
from src.db.schema import initialize as init_db
from src.db.operations import export_snapshots_json, export_subreddits_json, sync_subreddit_config
from src.collector import collect_subreddit

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def main():
    communities = load_communities()
    logger.info("Loaded %d active communities from config", len(communities))

    conn = init_db()
    sync_subreddit_config(communities, conn=conn)
    client = RedditClient(rate_limiter=RateLimiter(min_interval=6.0))

    results = []
    for community in communities:
        subreddit = community["subreddit"]
        result = collect_subreddit(subreddit=subreddit, client=client, conn=conn)
        results.append(result)

    # Export frontend-ready JSON
    logger.info("Exporting JSON files...")
    snap_path = export_snapshots_json(conn=conn)
    sub_path = export_subreddits_json(conn=conn)
    logger.info("Exported: %s, %s", snap_path, sub_path)

    conn.close()

    # Summary
    ok = [r for r in results if r["status"] == "ok"]
    errors = [r for r in results if r["status"] not in ("ok",)]
    total_posts = sum(r["posts_inserted"] for r in ok)

    logger.info(
        "Done. %d/%d subreddits collected, %d new posts stored.",
        len(ok), len(communities), total_posts,
    )

    if errors:
        logger.warning("%d subreddit(s) had issues:", len(errors))
        for r in errors:
            logger.warning("  r/%s: [%s] %s", r["subreddit"], r["status"], r["error"])

    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
