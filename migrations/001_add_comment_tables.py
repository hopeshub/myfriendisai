#!/usr/bin/env python3
"""Migration 001: Add comment collection and tagging tables.

Creates:
  - comments — stores Reddit comment text and metadata
  - comment_keyword_hits — stores keyword matches found in comment text
  - comment_collection_log — tracks which posts have had comments collected

Modifies:
  - post_keyword_tags — adds `source` column (default 'post'), updates unique
    constraint to (post_id, category, matched_term, source) so a post can have
    both post-sourced and comment-sourced tags for the same keyword.

Idempotent: safe to run multiple times.

Usage:
    python migrations/001_add_comment_tables.py
"""

import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "tracker.db"


def migrate(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()

    # ── 1. comments table ───────────────────────────────────────────────
    cur.executescript("""
        CREATE TABLE IF NOT EXISTS comments (
            id TEXT PRIMARY KEY,
            post_id TEXT NOT NULL,
            subreddit TEXT NOT NULL,
            author TEXT,
            body TEXT,
            score INTEGER,
            depth INTEGER NOT NULL DEFAULT 0,
            parent_id TEXT,
            created_utc INTEGER,
            permalink TEXT,
            collected_at TEXT NOT NULL
                DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),

            FOREIGN KEY (post_id) REFERENCES posts(id)
        );

        CREATE INDEX IF NOT EXISTS idx_comments_post_id
            ON comments(post_id);

        CREATE INDEX IF NOT EXISTS idx_comments_subreddit_created
            ON comments(subreddit, created_utc);
    """)
    print("  [OK] comments table")

    # ── 2. comment_keyword_hits table ───────────────────────────────────
    cur.executescript("""
        CREATE TABLE IF NOT EXISTS comment_keyword_hits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            comment_id TEXT NOT NULL,
            post_id TEXT NOT NULL,
            subreddit TEXT NOT NULL,
            category TEXT NOT NULL,
            matched_term TEXT NOT NULL,
            post_date DATE NOT NULL,

            FOREIGN KEY (comment_id) REFERENCES comments(id),
            FOREIGN KEY (post_id) REFERENCES posts(id)
        );

        CREATE INDEX IF NOT EXISTS idx_comment_hits_post_id
            ON comment_keyword_hits(post_id);

        CREATE INDEX IF NOT EXISTS idx_comment_hits_keyword
            ON comment_keyword_hits(category, matched_term);

        CREATE UNIQUE INDEX IF NOT EXISTS idx_comment_hits_unique
            ON comment_keyword_hits(comment_id, category, matched_term);
    """)
    print("  [OK] comment_keyword_hits table")

    # ── 3. comment_collection_log table ─────────────────────────────────
    cur.executescript("""
        CREATE TABLE IF NOT EXISTS comment_collection_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id TEXT NOT NULL,
            subreddit TEXT NOT NULL,
            comments_collected INTEGER NOT NULL DEFAULT 0,
            collected_at TEXT NOT NULL
                DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),

            FOREIGN KEY (post_id) REFERENCES posts(id)
        );

        CREATE UNIQUE INDEX IF NOT EXISTS idx_comment_log_post
            ON comment_collection_log(post_id);
    """)
    print("  [OK] comment_collection_log table")

    # ── 4. Add `source` column to post_keyword_tags ─────────────────────
    # Check if migration already applied
    cols = [row[1] for row in cur.execute("PRAGMA table_info(post_keyword_tags)").fetchall()]
    if "source" in cols:
        print("  [SKIP] post_keyword_tags already has source column")
        return

    # SQLite can't ALTER a unique constraint, so we rebuild the table.
    # 1. Rename old table
    # 2. Create new table with source column and updated unique constraint
    # 3. Copy data with source='post'
    # 4. Drop old table
    # 5. Recreate indexes

    print("  Rebuilding post_keyword_tags with source column...")

    row_count = cur.execute("SELECT COUNT(*) FROM post_keyword_tags").fetchone()[0]
    print(f"    {row_count} existing rows will get source='post'")

    cur.execute("ALTER TABLE post_keyword_tags RENAME TO _post_keyword_tags_old")

    cur.execute("""
        CREATE TABLE post_keyword_tags (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id     TEXT    NOT NULL,
            subreddit   TEXT    NOT NULL,
            category    TEXT    NOT NULL,
            matched_term TEXT   NOT NULL,
            post_date   DATE    NOT NULL,
            source      TEXT    NOT NULL DEFAULT 'post',
            UNIQUE(post_id, category, matched_term, source)
        )
    """)

    cur.execute("""
        INSERT INTO post_keyword_tags (post_id, subreddit, category, matched_term, post_date, source)
        SELECT post_id, subreddit, category, matched_term, post_date, 'post'
        FROM _post_keyword_tags_old
    """)

    migrated = cur.execute("SELECT COUNT(*) FROM post_keyword_tags").fetchone()[0]
    assert migrated == row_count, f"Row count mismatch: {migrated} vs {row_count}"

    cur.execute("DROP TABLE _post_keyword_tags_old")

    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_pkt_subreddit_date
            ON post_keyword_tags(subreddit, post_date)
    """)
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_pkt_category_date
            ON post_keyword_tags(category, post_date)
    """)

    conn.commit()
    print(f"  [OK] post_keyword_tags: {migrated} rows migrated with source='post'")


def main():
    if not DB_PATH.exists():
        print(f"ERROR: Database not found at {DB_PATH}")
        return 1

    print(f"Running migration 001 on {DB_PATH}")
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")

    try:
        migrate(conn)
        conn.commit()
        print("\nMigration 001 complete.")
        return 0
    except Exception as e:
        conn.rollback()
        print(f"\nERROR: Migration failed: {e}")
        return 1
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
