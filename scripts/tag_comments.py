#!/usr/bin/env python3
"""Tag comments with keyword categories and propagate hits to post-level tags.

Runs keyword matching against all untagged comments in the comments table,
writes hits to comment_keyword_hits, then propagates unique (post_id, category,
matched_term) combinations up to post_keyword_tags with source='comment'.

Usage:
    python scripts/tag_comments.py
"""

import logging
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.db.schema import initialize as init_db
from src.config import load_keyword_communities
from src.keyword_matching import build_patterns, match_text

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def tag_comments(conn=None):
    """Run keyword matching against all untagged comments.

    Returns dict with tagging stats.
    """
    _conn = conn or init_db()

    patterns = build_patterns()
    logger.info("Loaded %d keyword patterns", len(patterns))

    # Only tag comments from keyword-eligible subreddits (T1-T3)
    keyword_subs = [c["subreddit"] for c in load_keyword_communities()]
    placeholders = ",".join("?" for _ in keyword_subs)

    # Load already-tagged comment IDs
    tagged_ids = set(
        r[0] for r in _conn.execute(
            "SELECT DISTINCT comment_id FROM comment_keyword_hits"
        ).fetchall()
    )
    logger.info("Already-tagged comments: %d", len(tagged_ids))

    # Fetch all untagged comments from eligible subreddits
    cursor = _conn.execute(
        f"""
        SELECT id, post_id, subreddit, body, created_utc
        FROM comments
        WHERE subreddit IN ({placeholders})
        ORDER BY created_utc ASC
        """,
        keyword_subs,
    )

    processed = 0
    comments_with_hits = 0
    total_hits = 0
    by_category = defaultdict(lambda: {"hits": 0, "comments": set()})
    batch = []
    BATCH_SIZE = 500
    start = time.time()

    for comment_id, post_id, subreddit, body, created_utc in cursor:
        processed += 1

        if comment_id in tagged_ids:
            continue

        matches = match_text(body, patterns)
        if matches:
            comments_with_hits += 1
            # Derive post_date from comment's created_utc
            post_date = datetime.fromtimestamp(
                created_utc, tz=timezone.utc
            ).strftime("%Y-%m-%d") if created_utc else None

            for category, matched_term in matches:
                batch.append((
                    comment_id, post_id, subreddit,
                    category, matched_term, post_date,
                ))
                total_hits += 1
                by_category[category]["hits"] += 1
                by_category[category]["comments"].add(comment_id)

        if len(batch) >= BATCH_SIZE:
            _conn.executemany(
                "INSERT OR IGNORE INTO comment_keyword_hits "
                "(comment_id, post_id, subreddit, category, matched_term, post_date) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                batch,
            )
            _conn.commit()
            batch.clear()

    # Flush remaining
    if batch:
        _conn.executemany(
            "INSERT OR IGNORE INTO comment_keyword_hits "
            "(comment_id, post_id, subreddit, category, matched_term, post_date) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            batch,
        )
        _conn.commit()

    elapsed = time.time() - start

    logger.info("=" * 60)
    logger.info("Comment tagging complete:")
    logger.info("  Comments scanned: %d", processed)
    logger.info("  Comments with keyword hits: %d", comments_with_hits)
    logger.info("  Total keyword hits (comment_keyword_hits rows): %d", total_hits)
    logger.info("")
    logger.info("  By category:")
    for cat in sorted(by_category):
        info = by_category[cat]
        logger.info(
            "    %-20s %d hits across %d comments",
            cat + ":", info["hits"], len(info["comments"]),
        )
    logger.info("  Tagging took %.1fs", elapsed)
    logger.info("=" * 60)

    if conn is None:
        _conn.close()

    return {
        "comments_scanned": processed,
        "comments_with_hits": comments_with_hits,
        "total_hits": total_hits,
        "by_category": {
            cat: {"hits": info["hits"], "comments": len(info["comments"])}
            for cat, info in by_category.items()
        },
    }


def propagate_to_posts(conn=None):
    """Propagate comment-sourced keyword hits up to post_keyword_tags.

    For each distinct (post_id, category, matched_term) in comment_keyword_hits,
    inserts a row in post_keyword_tags with source='comment' if one doesn't
    already exist.

    Returns dict with propagation stats.
    """
    _conn = conn or init_db()

    # Get all distinct comment-level hits with the post's date
    # Use the post's collected_date (not the comment's date) for post_date,
    # since the post is the unit of analysis for trend lines
    rows = _conn.execute(
        """
        SELECT DISTINCT ckh.post_id, ckh.category, ckh.matched_term,
               c.subreddit, p.collected_date
        FROM comment_keyword_hits ckh
        JOIN comments c ON c.id = ckh.comment_id
        JOIN posts p ON p.id = ckh.post_id
        """
    ).fetchall()

    logger.info("Distinct (post, category, term) from comment hits: %d", len(rows))

    # Insert into post_keyword_tags with source='comment'
    inserted = 0
    batch = []
    for post_id, category, matched_term, subreddit, post_date in rows:
        batch.append((post_id, subreddit, category, matched_term, post_date, "comment"))

    if batch:
        cursor = _conn.executemany(
            "INSERT OR IGNORE INTO post_keyword_tags "
            "(post_id, subreddit, category, matched_term, post_date, source) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            batch,
        )
        inserted = cursor.rowcount
        _conn.commit()

    # Count posts newly tagged (have comment-source but no post-source for same category)
    newly_tagged = _conn.execute(
        """
        SELECT COUNT(DISTINCT pkt1.post_id)
        FROM post_keyword_tags pkt1
        WHERE pkt1.source = 'comment'
          AND NOT EXISTS (
              SELECT 1 FROM post_keyword_tags pkt2
              WHERE pkt2.post_id = pkt1.post_id
                AND pkt2.category = pkt1.category
                AND pkt2.source = 'post'
          )
        """
    ).fetchone()[0]

    # Count posts with both sources for same category
    both_sources = _conn.execute(
        """
        SELECT COUNT(DISTINCT pkt1.post_id)
        FROM post_keyword_tags pkt1
        WHERE pkt1.source = 'comment'
          AND EXISTS (
              SELECT 1 FROM post_keyword_tags pkt2
              WHERE pkt2.post_id = pkt1.post_id
                AND pkt2.category = pkt1.category
                AND pkt2.source = 'post'
          )
        """
    ).fetchone()[0]

    logger.info("=" * 60)
    logger.info("Propagation complete:")
    logger.info("  New post-level tags added (source='comment'): %d", inserted)
    logger.info(
        "  Posts newly tagged via comments (had no post-source tag for this category): %d",
        newly_tagged,
    )
    logger.info(
        "  Posts with both post and comment tags for same category: %d",
        both_sources,
    )
    logger.info("=" * 60)

    if conn is None:
        _conn.close()

    return {
        "tags_inserted": inserted,
        "posts_newly_tagged": newly_tagged,
        "posts_both_sources": both_sources,
    }


def main():
    conn = init_db()

    tag_comments(conn=conn)
    propagate_to_posts(conn=conn)

    conn.close()


if __name__ == "__main__":
    main()
