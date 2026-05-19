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
from src.config import load_keywords, load_keyword_communities, keyword_fingerprint
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
    parser.add_argument(
        "--retag", action="store_true",
        help="Re-scan every post even if already tagged (use after adding "
             "keywords; INSERT OR IGNORE dedupes existing rows)",
    )
    parser.add_argument(
        "--prune-orphans", action="store_true",
        help="Delete tag rows whose keyword is no longer in the config",
    )
    args = parser.parse_args()

    conn = init_db()

    # Create table and indexes
    conn.executescript(CREATE_TABLE + CREATE_INDEX)
    conn.commit()

    # Load keyword categories
    keyword_categories = load_keywords()
    patterns = build_patterns(keyword_categories)
    logger.info("Loaded %d patterns across %d categories", len(patterns), len(keyword_categories))

    # --- Keyword-set version safety ---------------------------------------
    # The skip-cache below makes tagging fast by ignoring already-tagged
    # posts. That is only safe while the keyword set is unchanged — a newly
    # added keyword would otherwise never reach old posts. Compare a
    # fingerprint of the current keyword set against the one the corpus was
    # last fully tagged at, and fall back to a full re-scan when they differ.
    current_fp = keyword_fingerprint(keyword_categories)
    row = conn.execute(
        "SELECT value FROM pipeline_meta WHERE key = 'keyword_fingerprint'"
    ).fetchone()
    stored_fp = row[0] if row else None
    full_scope = not args.subreddit and not args.since
    version_changed = stored_fp is not None and stored_fp != current_fp
    retag = args.retag or (full_scope and version_changed)

    if full_scope and version_changed:
        logger.warning(
            "Keyword set changed since last full tagging (%s -> %s) "
            "-> re-scanning the full corpus so new keywords reach old posts",
            (stored_fp or "none")[:12], current_fp[:12],
        )
    elif args.retag:
        logger.info("--retag: re-scanning all posts (skip-cache disabled)")

    if retag:
        tagged_ids = set()
        logger.info("Re-tag mode: not skipping already-tagged posts "
                    "(INSERT OR IGNORE dedupes existing rows)")
    else:
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

    # --- Orphan tags + fingerprint bookkeeping ----------------------------
    # Tags whose (category, term) is no longer in the keyword config — these
    # accumulate when a keyword is removed or renamed in a config bump.
    if full_scope or args.prune_orphans:
        config_pairs = {
            (cat["name"], str(t).strip().lower())
            for cat in keyword_categories
            for t in cat.get("terms", [])
        }
        db_pairs = conn.execute(
            "SELECT DISTINCT category, matched_term FROM post_keyword_tags"
        ).fetchall()
        orphans = sorted(
            {(c, t) for c, t in db_pairs
             if (c, str(t).strip().lower()) not in config_pairs}
        )
        if orphans and args.prune_orphans:
            for cat, term in orphans:
                conn.execute(
                    "DELETE FROM post_keyword_tags WHERE category = ? AND matched_term = ?",
                    (cat, term),
                )
            conn.commit()
            logger.info("Pruned %d orphan keyword(s) no longer in config: %s",
                        len(orphans), ", ".join(f"{c}/{t}" for c, t in orphans))
        elif orphans:
            logger.warning(
                "%d tagged keyword(s) are no longer in config: %s. "
                "Re-run with --prune-orphans to remove their tags.",
                len(orphans), ", ".join(f"{c}/{t}" for c, t in orphans),
            )

    # A full-scope run has now tagged the whole corpus at the current keyword
    # set, so record the fingerprint. Partial runs (--subreddit / --since) do
    # not cover the corpus and must not clear the staleness signal.
    if full_scope:
        conn.execute(
            "INSERT INTO pipeline_meta (key, value, updated_at) "
            "VALUES ('keyword_fingerprint', ?, CURRENT_TIMESTAMP) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value, "
            "updated_at = CURRENT_TIMESTAMP",
            (current_fp,),
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
