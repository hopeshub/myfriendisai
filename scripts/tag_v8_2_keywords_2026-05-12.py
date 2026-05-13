#!/usr/bin/env python3
"""One-off retag: tag T1-T3 posts against the 8 v8.2 anchor-mining KEEP keywords.

Runs alongside the existing post_keyword_tags table (UNIQUE constraint dedups).
Same pattern as tag_new_rupture_keywords_2026-05-12.py.
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

# (theme, keyword) pairs to tag
NEW_KEYWORDS = [
    ("addiction", "my addiction"),
    ("addiction", "withdrawals"),
    ("addiction", "screen time"),
    ("romance", "in love with an ai"),
    ("romance", "romantic relationship with"),
    ("sexual_erp", "smut"),
    ("sexual_erp", "nsfw content"),
    ("sexual_erp", "nsfw stuff"),
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    # Group by theme for build_patterns
    by_theme: dict[str, list[str]] = {}
    for theme, kw in NEW_KEYWORDS:
        by_theme.setdefault(theme, []).append(kw)
    synthetic = [{"name": t, "terms": kws} for t, kws in by_theme.items()]
    patterns = build_patterns(synthetic)
    logger.info("Built %d patterns across %d themes", len(patterns), len(synthetic))

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    keyword_subs = [c["subreddit"] for c in load_keyword_communities()]
    placeholders = ",".join("?" for _ in keyword_subs)

    total_posts = conn.execute(
        f"SELECT COUNT(*) FROM posts WHERE subreddit IN ({placeholders})",
        keyword_subs,
    ).fetchone()[0]
    logger.info("Posts to scan: %d", total_posts)

    cursor = conn.execute(
        "SELECT id, subreddit, title, selftext, "
        "date(created_utc, 'unixepoch') AS post_date "
        f"FROM posts WHERE subreddit IN ({placeholders})",
        keyword_subs,
    )

    BATCH = 1000
    processed = 0
    keyword_hits: dict[str, int] = {kw: 0 for _, kw in NEW_KEYWORDS}
    batch_rows: list[tuple] = []
    start = time.time()

    for row in cursor:
        processed += 1
        text = " ".join(filter(None, [row["title"], row["selftext"]]))
        if not text:
            continue
        for category, term, pat in patterns:
            if pat.search(text):
                keyword_hits[term] += 1
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
            batch_rows.clear()

        if processed % 100000 == 0:
            elapsed = time.time() - start
            rate = processed / elapsed
            logger.info(
                "  %d/%d posts | %d hits | %.0f posts/s",
                processed, total_posts, sum(keyword_hits.values()), rate,
            )

    if batch_rows and not args.dry_run:
        conn.executemany(
            "INSERT OR IGNORE INTO post_keyword_tags "
            "(post_id, subreddit, category, matched_term, post_date) "
            "VALUES (?, ?, ?, ?, ?)",
            batch_rows,
        )
        conn.commit()

    conn.close()
    elapsed = time.time() - start
    logger.info("=" * 60)
    logger.info("Done in %.1fm  (dry-run=%s)", elapsed / 60, args.dry_run)
    for theme, kw in NEW_KEYWORDS:
        logger.info("  %-12s %-30s  %5d hits", theme, kw, keyword_hits[kw])


if __name__ == "__main__":
    main()
