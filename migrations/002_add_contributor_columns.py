#!/usr/bin/env python3
"""Migration 002: Add rolling-7d contributor columns to subreddit_snapshots.

Adds three columns to replace the dead `active_users` field (Reddit removed
`active_user_count` from about.json in September 2025):

  - unique_post_authors_7d   — distinct post authors in the 7 days ending
                                on snapshot_date
  - unique_comment_authors_7d — distinct comment authors in the same window
  - unique_contributors_7d   — distinct union of post + comment authors

Also creates idx_posts_subreddit_created to make the backfill + daily
update fast.

Idempotent.

Usage:
    python migrations/002_add_contributor_columns.py
"""

import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "tracker.db"

NEW_COLUMNS = [
    ("unique_post_authors_7d", "INTEGER"),
    ("unique_comment_authors_7d", "INTEGER"),
    ("unique_contributors_7d", "INTEGER"),
]


def migrate(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()

    existing = {row[1] for row in cur.execute("PRAGMA table_info(subreddit_snapshots)").fetchall()}
    for col, col_type in NEW_COLUMNS:
        if col in existing:
            print(f"  [SKIP] subreddit_snapshots.{col} already exists")
            continue
        cur.execute(f"ALTER TABLE subreddit_snapshots ADD COLUMN {col} {col_type}")
        print(f"  [OK] added column subreddit_snapshots.{col}")

    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_posts_subreddit_created "
        "ON posts(subreddit, created_utc)"
    )
    print("  [OK] idx_posts_subreddit_created")

    conn.commit()


def main():
    if not DB_PATH.exists():
        print(f"ERROR: Database not found at {DB_PATH}")
        return 1

    print(f"Running migration 002 on {DB_PATH}")
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA journal_mode=WAL")
    try:
        migrate(conn)
        print("\nMigration 002 complete.")
        return 0
    except Exception as e:
        conn.rollback()
        print(f"\nERROR: Migration failed: {e}")
        return 1
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
