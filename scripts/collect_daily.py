#!/usr/bin/env python3
"""Daily collection entry point.

Loads communities from config, collects Reddit data for each, stores in SQLite,
and exports frontend-ready JSON files.

Usage:
    python scripts/collect_daily.py
"""

import logging
import shutil
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
from src.keyword_scanner import scan_subreddit_keywords, store_keyword_counts, export_keywords_json

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

    # Keyword scanning
    from datetime import date as date_cls
    today = date_cls.today()
    logger.info("Scanning posts for keyword matches...")
    ok_subs = [r["subreddit"] for r in results if r["status"] == "ok"]
    for subreddit in ok_subs:
        kw_results = scan_subreddit_keywords(subreddit, today, conn=conn)
        store_keyword_counts(kw_results, conn=conn)
        hits = sum(r["count"] for r in kw_results)
        if hits > 0:
            cats = [f"{r['category']}={r['count']}" for r in kw_results if r["count"] > 0]
            logger.info("  r/%s: %d keyword hits (%s)", subreddit, hits, ", ".join(cats))
    logger.info("Keyword scanning complete")

    # Export frontend-ready JSON
    logger.info("Exporting JSON files...")
    snap_path = export_snapshots_json(conn=conn)
    sub_path = export_subreddits_json(conn=conn)
    kw_path = export_keywords_json(conn=conn)
    logger.info("Exported: %s, %s, %s", snap_path, sub_path, kw_path)

    # Copy JSON files into web/data/ for Vercel builds
    web_data_dir = Path(__file__).parent.parent / "web" / "data"
    web_data_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(snap_path, web_data_dir / "snapshots.json")
    shutil.copy2(sub_path, web_data_dir / "subreddits.json")
    shutil.copy2(kw_path, web_data_dir / "keywords.json")
    logger.info("Copied JSON to web/data/ for frontend")

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
