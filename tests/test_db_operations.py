"""Smoke tests for src/db operations against an in-memory SQLite."""

import sqlite3
from pathlib import Path

import pytest

from src.db.schema import SCHEMA


@pytest.fixture
def conn():
    c = sqlite3.connect(":memory:")
    c.row_factory = sqlite3.Row
    c.executescript(SCHEMA)
    yield c
    c.close()


def test_schema_creates_all_expected_tables(conn):
    tables = {r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()}
    required = {
        "subreddit_snapshots", "posts", "post_keyword_tags",
        "comments", "comment_keyword_hits", "comment_collection_log",
        "subreddit_config",
    }
    assert required.issubset(tables), f"Missing tables: {required - tables}"


def test_posts_primary_key_rejects_duplicate_id(conn):
    conn.execute(
        "INSERT INTO posts (id, subreddit, collected_date) VALUES (?, ?, ?)",
        ("abc123", "replika", "2026-04-14"),
    )
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO posts (id, subreddit, collected_date) VALUES (?, ?, ?)",
            ("abc123", "replika", "2026-04-14"),
        )


def test_snapshot_unique_per_subreddit_per_day(conn):
    conn.execute(
        "INSERT INTO subreddit_snapshots (subreddit, snapshot_date, subscribers) VALUES (?, ?, ?)",
        ("replika", "2026-04-14", 83907),
    )
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO subreddit_snapshots (subreddit, snapshot_date, subscribers) VALUES (?, ?, ?)",
            ("replika", "2026-04-14", 83908),
        )


def test_post_keyword_tags_unique_on_post_category_term_source(conn):
    conn.execute(
        "INSERT INTO posts (id, subreddit, collected_date) VALUES (?, ?, ?)",
        ("p1", "replika", "2026-04-14"),
    )
    conn.execute(
        "INSERT INTO post_keyword_tags (post_id, subreddit, category, matched_term, post_date, source) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        ("p1", "replika", "therapy", "therapist", "2026-04-14", "post"),
    )
    # Same tuple should conflict
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO post_keyword_tags (post_id, subreddit, category, matched_term, post_date, source) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            ("p1", "replika", "therapy", "therapist", "2026-04-14", "post"),
        )
    # Different source is allowed (post vs comment)
    conn.execute(
        "INSERT INTO post_keyword_tags (post_id, subreddit, category, matched_term, post_date, source) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        ("p1", "replika", "therapy", "therapist", "2026-04-14", "comment"),
    )


def test_comments_foreign_key_to_posts(conn):
    conn.execute("PRAGMA foreign_keys=ON")
    # Posts doesn't exist yet — FK should reject
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO comments (id, post_id, subreddit) VALUES (?, ?, ?)",
            ("c1", "nonexistent", "replika"),
        )


def test_snapshot_accepts_null_active_users(conn):
    # Reddit stopped populating active_user_count upstream; NULL must be allowed
    conn.execute(
        "INSERT INTO subreddit_snapshots (subreddit, snapshot_date, subscribers, active_users) "
        "VALUES (?, ?, ?, ?)",
        ("replika", "2026-04-14", 83907, None),
    )
    row = conn.execute(
        "SELECT active_users FROM subreddit_snapshots WHERE subreddit='replika'"
    ).fetchone()
    assert row[0] is None
