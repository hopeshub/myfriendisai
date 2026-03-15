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
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.db.schema import get_connection, initialize as init_db
from src.config import load_keywords, load_keyword_communities

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
    UNIQUE(post_id, category, matched_term)
);
"""

CREATE_INDEX = """
CREATE INDEX IF NOT EXISTS idx_pkt_subreddit_date
    ON post_keyword_tags(subreddit, post_date);
CREATE INDEX IF NOT EXISTS idx_pkt_category_date
    ON post_keyword_tags(category, post_date);
"""


def build_patterns(keyword_categories: list[dict]) -> list[tuple[str, str, re.Pattern]]:
    """Return list of (category_name, term, compiled_pattern) for all terms."""
    patterns = []
    for cat in keyword_categories:
        category = cat["name"]
        for term in cat.get("terms", []):
            # Word-boundary match, case-insensitive
            # For multi-word phrases, just do substring match (no boundary issues)
            escaped = re.escape(term)
            if " " in term:
                pat = re.compile(escaped, re.IGNORECASE)
            else:
                pat = re.compile(r"\b" + escaped + r"\b", re.IGNORECASE)
            patterns.append((category, term, pat))
    return patterns


def tag_post(text: str, patterns: list[tuple[str, str, re.Pattern]]) -> list[tuple[str, str]]:
    """Return list of (category, matched_term) for all matches in text."""
    if not text:
        return []
    seen = set()
    matches = []
    for category, term, pat in patterns:
        key = (category, term)
        if key not in seen and pat.search(text):
            matches.append(key)
            seen.add(key)
    return matches


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
    query = f"SELECT id, subreddit, title, selftext, collected_date FROM posts WHERE subreddit IN ({placeholders})"
    params: list = list(keyword_subs)
    if args.subreddit:
        query = "SELECT id, subreddit, title, selftext, collected_date FROM posts WHERE subreddit = ?"
        params = [args.subreddit]
    if args.since:
        query += " AND collected_date >= ?"
        params.append(args.since)
    query += " ORDER BY collected_date ASC"

    total_posts = conn.execute(
        query.replace("SELECT id, subreddit, title, selftext, collected_date", "SELECT COUNT(*)"),
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
            matches = tag_post(text, patterns)
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
