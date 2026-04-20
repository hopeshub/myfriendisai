#!/usr/bin/env python3
"""Tag posts in tracker.db against keyword categories from config/keywords.yaml.

Creates a post_keyword_tags table with per-post, per-category matches.
Idempotent: skips posts already tagged. Logs progress every 1000 posts.

Usage:
    python scripts/tag_keywords.py
    python scripts/tag_keywords.py --subreddit replika   # single subreddit
    python scripts/tag_keywords.py --since 2024-01-01    # only posts from date
"""

import argparse
import logging
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.db.schema import initialize as init_db
from src.config import load_keywords, load_keyword_communities
from src.keyword_matching import build_patterns, match_text

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS post_keyword_tags (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id     TEXT    NOT NULL,
    subreddit   TEXT    NOT NULL,
    category    TEXT    NOT NULL,
    matched_term TEXT   NOT NULL,
    post_date   DATE    NOT NULL,
    source      TEXT    NOT NULL DEFAULT 'post',
    UNIQUE(post_id, category, matched_term, source)
);
"""

CREATE_INDEX = """
CREATE INDEX IF NOT EXISTS idx_pkt_subreddit_date
    ON post_keyword_tags(subreddit, post_date);
CREATE INDEX IF NOT EXISTS idx_pkt_category_date
    ON post_keyword_tags(category, post_date);
"""


# build_patterns and match_text imported from src.keyword_matching


def main():
    parser = argparse.ArgumentParser(description="Tag posts with keyword categories")
    parser.add_argument("--subreddit", help="Only tag posts from this subreddit")
    parser.add_argument("--since", help="Only tag posts on or after YYYY-MM-DD")
    args = parser.parse_args()

    conn = init_db()

    # Create table and indexes
    conn.executescript(CREATE_TABLE + CREATE_INDEX)
    conn.commit()

    # Load keyword categories
    keyword_categories = load_keywords()
    patterns = build_patterns(keyword_categories)
    logger.info("Loaded %d patterns across %d categories", len(patterns), len(keyword_categories))

    # Find already-tagged post IDs so we can skip them
    logger.info("Loading already-tagged post IDs...")
    tagged_ids = set(
        r[0] for r in conn.execute("SELECT DISTINCT post_id FROM post_keyword_tags").fetchall()
    )
    logger.info("  %d posts already tagged, will skip", len(tagged_ids))

    # Only tag posts from T1-T3 keyword-eligible subreddits
    keyword_subs = [c["subreddit"] for c in load_keyword_communities()]
    logger.info("Keyword-eligible subreddits (T1-T3): %d", len(keyword_subs))

    # Build post query
    placeholders = ",".join("?" for _ in keyword_subs)
    select_cols = "SELECT id, subreddit, title, selftext, date(created_utc, 'unixepoch') AS post_date"
    where_clause = f"FROM posts WHERE subreddit IN ({placeholders})"
    params: list = list(keyword_subs)
    if args.subreddit:
        where_clause = "FROM posts WHERE subreddit = ?"
        params = [args.subreddit]
    if args.since:
        where_clause += " AND date(created_utc, 'unixepoch') >= ?"
        params.append(args.since)
    query = f"{select_cols} {where_clause} ORDER BY post_date ASC"

    total_posts = conn.execute(
        f"SELECT COUNT(*) {where_clause}",
        params,
    ).fetchone()[0]
    logger.info("Posts to scan: %d", total_posts)

    cursor = conn.execute(query, params)

    processed = 0
    skipped = 0
    tagged = 0
    batch: list[tuple] = []
    BATCH_SIZE = 500
    start = time.time()

    for post_id, subreddit, title, selftext, post_date in cursor:
        processed += 1

        if post_id in tagged_ids:
            skipped += 1
        else:
            text = " ".join(filter(None, [title, selftext]))
            matches = match_text(text, patterns)
            for category, matched_term in matches:
                batch.append((post_id, subreddit, category, matched_term, post_date))
                tagged += 1

        if len(batch) >= BATCH_SIZE:
            conn.executemany(
                "INSERT OR IGNORE INTO post_keyword_tags "
                "(post_id, subreddit, category, matched_term, post_date) "
                "VALUES (?, ?, ?, ?, ?)",
                batch,
            )
            conn.commit()
            batch.clear()

        if processed % 1000 == 0:
            elapsed = time.time() - start
            rate = processed / elapsed
            remaining = (total_posts - processed) / rate if rate > 0 else 0
            logger.info(
                "  %d/%d posts scanned | %d tag rows | %.0f posts/sec | ~%.0fm remaining",
                processed, total_posts, tagged, rate, remaining / 60,
            )

    # Flush remaining batch
    if batch:
        conn.executemany(
            "INSERT OR IGNORE INTO post_keyword_tags "
            "(post_id, subreddit, category, matched_term, post_date) "
            "VALUES (?, ?, ?, ?, ?)",
            batch,
        )
        conn.commit()

    conn.close()

    elapsed = time.time() - start
    logger.info("=" * 60)
    logger.info("Done in %.1fm", elapsed / 60)
    logger.info("  Posts scanned:  %d", processed - skipped)
    logger.info("  Posts skipped:  %d (already tagged)", skipped)
    logger.info("  Tag rows added: %d", tagged)
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
