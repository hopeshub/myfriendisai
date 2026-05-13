#!/usr/bin/env python3
"""Migration 003: Extend llm_classifications for production hybrid gating.

Background: an existing llm_classifications table was created during the
March 2026 validation effort with schema (post_id, theme, keyword,
classification YES/NO, reason, model, classified_at, run_id) and ~10k rows
of claude-code-sourced verdicts. This migration extends it to support
comment-level classification and production-grade tracking without
disturbing the legacy data.

Changes:
  - Add tag_type column (default 'post') so comments can coexist
  - Add comment_id column (nullable, only set when tag_type='comment')
  - Add verdict column normalized to {'TP', 'FP', 'AMBIGUOUS'} alongside
    the legacy classification column (YES/NO). Code reads verdict when
    set, falls back to classification when not.
  - Drop the old (post_id, theme, keyword) unique index — too narrow:
    can't distinguish multiple model verdicts for the same post.
  - Add (tag_type, tag_id, theme, keyword, model) unique index where
    tag_id is post_id for posts and comment_id for comments (via the
    coalesce of the two columns).

Idempotent.

Usage:
    .venv/bin/python migrations/003_add_llm_classifications.py
"""

import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "tracker.db"


def column_exists(cur: sqlite3.Cursor, table: str, column: str) -> bool:
    cur.execute(f"PRAGMA table_info({table})")
    return any(row[1] == column for row in cur.fetchall())


def index_exists(cur: sqlite3.Cursor, name: str) -> bool:
    cur.execute(
        "SELECT 1 FROM sqlite_master WHERE type='index' AND name=?", (name,)
    )
    return cur.fetchone() is not None


def has_legacy_pk(cur: sqlite3.Cursor) -> bool:
    """Detect whether the table still has the legacy (post_id, theme, keyword) PK."""
    row = cur.execute(
        "SELECT sql FROM sqlite_master WHERE type='table' AND name='llm_classifications'"
    ).fetchone()
    if not row or not row[0]:
        return False
    return "PRIMARY KEY (post_id, theme, keyword)" in row[0]


def rebuild_without_legacy_pk(cur: sqlite3.Cursor) -> None:
    """Recreate the table without the over-narrow legacy PK so the same item
    can have verdicts from multiple models (needed for drift detection).
    Preserves all existing rows."""
    print("  rebuilding table to drop legacy PRIMARY KEY ...")
    cur.executescript("""
        CREATE TABLE llm_classifications_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tag_type TEXT NOT NULL DEFAULT 'post',
            post_id TEXT,
            comment_id TEXT,
            theme TEXT NOT NULL,
            keyword TEXT NOT NULL,
            classification TEXT,           -- legacy YES/NO (kept for compat)
            verdict TEXT,                  -- normalized TP/FP/AMBIGUOUS
            confidence REAL,
            reason TEXT,
            model TEXT NOT NULL,
            classified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            run_id TEXT
        );

        INSERT INTO llm_classifications_new
            (tag_type, post_id, theme, keyword, classification, verdict,
             confidence, reason, model, classified_at, run_id)
        SELECT 'post', post_id, theme, keyword, classification,
               CASE
                   WHEN UPPER(classification) IN ('YES', 'TP') THEN 'TP'
                   WHEN UPPER(classification) IN ('NO', 'FP') THEN 'FP'
                   ELSE 'AMBIGUOUS'
               END AS verdict,
               NULL, reason, model, classified_at, run_id
        FROM llm_classifications;

        DROP TABLE llm_classifications;
        ALTER TABLE llm_classifications_new RENAME TO llm_classifications;
    """)
    row = cur.execute("SELECT COUNT(*) FROM llm_classifications").fetchone()
    print(f"    {row[0]} rows preserved")


def migrate(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()

    # Ensure the table exists (idempotency for fresh databases).
    cur.execute("""
        CREATE TABLE IF NOT EXISTS llm_classifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tag_type TEXT NOT NULL DEFAULT 'post',
            post_id TEXT,
            comment_id TEXT,
            theme TEXT NOT NULL,
            keyword TEXT NOT NULL,
            classification TEXT,
            verdict TEXT,
            confidence REAL,
            reason TEXT,
            model TEXT NOT NULL,
            classified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            run_id TEXT
        )
    """)

    # Rebuild without legacy PK if present.
    if has_legacy_pk(cur):
        rebuild_without_legacy_pk(cur)

    # Add new columns if missing (idempotency for fresh-but-newer schemas).
    if not column_exists(cur, "llm_classifications", "tag_type"):
        cur.execute(
            "ALTER TABLE llm_classifications ADD COLUMN tag_type TEXT NOT NULL DEFAULT 'post'"
        )
        print("  added column tag_type")
    if not column_exists(cur, "llm_classifications", "comment_id"):
        cur.execute("ALTER TABLE llm_classifications ADD COLUMN comment_id TEXT")
        print("  added column comment_id")
    if not column_exists(cur, "llm_classifications", "verdict"):
        cur.execute("ALTER TABLE llm_classifications ADD COLUMN verdict TEXT")
        print("  added column verdict")
    if not column_exists(cur, "llm_classifications", "confidence"):
        cur.execute("ALTER TABLE llm_classifications ADD COLUMN confidence REAL")
        print("  added column confidence")

    # Backfill verdict from legacy classification column where verdict is null.
    # Legacy YES => TP, NO => FP, anything else => AMBIGUOUS.
    cur.execute("""
        UPDATE llm_classifications
        SET verdict = CASE
            WHEN UPPER(classification) IN ('YES', 'TP') THEN 'TP'
            WHEN UPPER(classification) IN ('NO', 'FP') THEN 'FP'
            ELSE 'AMBIGUOUS'
        END
        WHERE verdict IS NULL
    """)
    print(f"  backfilled verdict on {cur.rowcount} legacy rows")

    # Drop the legacy primary-key-style unique constraint by giving the table
    # a fresh covering index that includes tag_type and model. SQLite doesn't
    # let us drop PK, but we can add a UNIQUE index that supersedes it for
    # new inserts that include tag_type/comment_id/model.
    if not index_exists(cur, "idx_llm_class_unique_v2"):
        # Use coalesce so a single index covers both post and comment rows.
        cur.execute("""
            CREATE UNIQUE INDEX idx_llm_class_unique_v2
            ON llm_classifications(
                tag_type,
                COALESCE(comment_id, post_id),
                theme,
                keyword,
                model
            )
        """)
        print("  created unique index idx_llm_class_unique_v2")

    # Lookup indices.
    for idx_name, idx_sql in [
        ("idx_llm_class_tag", "CREATE INDEX idx_llm_class_tag ON llm_classifications(tag_type, post_id, comment_id)"),
        ("idx_llm_class_verdict", "CREATE INDEX idx_llm_class_verdict ON llm_classifications(theme, verdict)"),
        ("idx_llm_class_keyword", "CREATE INDEX idx_llm_class_keyword ON llm_classifications(keyword, verdict)"),
    ]:
        if not index_exists(cur, idx_name):
            cur.execute(idx_sql)
            print(f"  created index {idx_name}")

    conn.commit()
    print("Migration 003 applied: llm_classifications extended for hybrid gating.")


if __name__ == "__main__":
    if not DB_PATH.exists():
        print(f"ERROR: database not found at {DB_PATH}", file=sys.stderr)
        sys.exit(1)
    conn = sqlite3.connect(DB_PATH)
    try:
        migrate(conn)
    finally:
        conn.close()
