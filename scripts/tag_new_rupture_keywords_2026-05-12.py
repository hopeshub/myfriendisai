#!/usr/bin/env python3
"""One-off retag: tag T1-T3 posts against the 8 NEW Rupture keywords from v8.1.

Runs alongside the existing post_keyword_tags table (UNIQUE constraint dedups).
Does NOT touch existing tags. Uses production keyword_matching semantics
(re.escape word-boundary, literal space — see README §Implementation bugs for
the multi-word \\s+ vs literal-space discrepancy with the validation pipeline;
acceptable here because the discrepancy means production tags are a strict
subset of validation matches and precision is therefore not degraded).

Usage:
    python scripts/tag_new_rupture_keywords_2026-05-12.py [--dry-run]

After this script runs, run:
    python scripts/export_json.py
    python scripts/export_keyword_details.py
to regenerate the frontend data.
"""

import argparse
import logging
import sqlite3
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from src.config import load_keyword_communities
from src.keyword_matching import build_patterns

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent.parent / "data" / "tracker.db"

NEW_KEYWORDS = [
    "saying goodbye",
    "taken away",
    "mourning",
    "mourn",
    "devastated",
    "grieve",
    "goodbye",
    "farewell",
]

RUPTURE_CATEGORY = "rupture"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Count matches but do not insert")
    args = parser.parse_args()

    # Build patterns from one synthetic category
    synthetic = [{"name": RUPTURE_CATEGORY, "terms": NEW_KEYWORDS}]
    patterns = build_patterns(synthetic)
    logger.info("Built %d patterns for %d keywords", len(patterns), len(NEW_KEYWORDS))

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    keyword_subs = [c["subreddit"] for c in load_keyword_communities()]
    logger.info("Keyword-eligible subreddits (T1-T3): %d", len(keyword_subs))

    placeholders = ",".join("?" for _ in keyword_subs)
    total_query = (
        f"SELECT COUNT(*) FROM posts WHERE subreddit IN ({placeholders})"
    )
    total_posts = conn.execute(total_query, keyword_subs).fetchone()[0]
    logger.info("Posts to scan: %d", total_posts)

    cursor = conn.execute(
        "SELECT id, subreddit, title, selftext, "
        "date(created_utc, 'unixepoch') AS post_date "
        f"FROM posts WHERE subreddit IN ({placeholders}) "
        "ORDER BY post_date ASC",
        keyword_subs,
    )

    BATCH = 1000
    processed = 0
    new_tag_rows = 0
    keyword_hit_counts = {kw: 0 for kw in NEW_KEYWORDS}
    batch_rows: list[tuple] = []
    start = time.time()

    for row in cursor:
        processed += 1
        text = " ".join(filter(None, [row["title"], row["selftext"]]))
        if not text:
            continue
        for category, term, pat in patterns:
            if pat.search(text):
                keyword_hit_counts[term] += 1
                batch_rows.append(
                    (row["id"], row["subreddit"], category, term, row["post_date"])
                )

        if len(batch_rows) >= BATCH:
            if not args.dry_run:
                conn.executemany(
                    "INSERT OR IGNORE INTO post_keyword_tags "
                    "(post_id, subreddit, category, matched_term, post_date) "
                    "VALUES (?, ?, ?, ?, ?)",
                    batch_rows,
                )
                conn.commit()
                new_tag_rows += conn.total_changes  # cumulative since connect; we report final
            batch_rows.clear()

        if processed % 50000 == 0:
            elapsed = time.time() - start
            rate = processed / elapsed
            remaining = (total_posts - processed) / rate
            logger.info(
                "  %d/%d posts | %d hits so far | %.0f posts/s | ~%.0fm remaining",
                processed, total_posts, sum(keyword_hit_counts.values()),
                rate, remaining / 60,
            )

    # Flush remaining batch
    if batch_rows and not args.dry_run:
        conn.executemany(
            "INSERT OR IGNORE INTO post_keyword_tags "
            "(post_id, subreddit, category, matched_term, post_date) "
            "VALUES (?, ?, ?, ?, ?)",
            batch_rows,
        )
        conn.commit()

    # Final counts (from DB, since INSERT OR IGNORE filters duplicates)
    if not args.dry_run:
        per_term_final = dict(
            conn.execute(
                "SELECT matched_term, COUNT(DISTINCT post_id) "
                "FROM post_keyword_tags "
                "WHERE category = ? AND matched_term IN ({}) "
                "AND source = 'post' "
                "GROUP BY matched_term".format(",".join("?" * len(NEW_KEYWORDS))),
                [RUPTURE_CATEGORY, *NEW_KEYWORDS],
            ).fetchall()
        )
    else:
        per_term_final = keyword_hit_counts

    conn.close()
    elapsed = time.time() - start
    logger.info("=" * 60)
    logger.info("Done in %.1fm  (dry-run=%s)", elapsed / 60, args.dry_run)
    logger.info("  Posts scanned: %d", processed)
    logger.info("  Per-keyword unique post counts:")
    for term in NEW_KEYWORDS:
        in_text = keyword_hit_counts[term]
        in_db = per_term_final.get(term, 0)
        logger.info("    %-18s in-text hits: %5d   in-db unique: %5d", term, in_text, in_db)


if __name__ == "__main__":
    main()
