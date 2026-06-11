"""Tests for Arctic Shift comment collection (parse, filter, insert path)."""

import sqlite3

import pytest

from src.db.schema import SCHEMA
from scripts.backfill_arctic import (
    parse_arctic_comment,
    filter_comments,
    insert_comments_for_known_posts,
)


@pytest.fixture
def conn():
    c = sqlite3.connect(":memory:")
    c.row_factory = sqlite3.Row
    c.executescript(SCHEMA)
    yield c
    c.close()


def _arctic_comment(**overrides):
    base = {
        "id": "c1",
        "link_id": "t3_post1",
        "parent_id": "t3_post1",
        "subreddit": "replika",
        "author": "someone",
        "body": "I love my rep",
        "score": 4,
        "created_utc": 1781198595,
        "permalink": "/r/replika/comments/post1/x/c1/",
    }
    base.update(overrides)
    return base


def test_parse_top_level_comment():
    parsed = parse_arctic_comment(_arctic_comment())
    assert parsed["id"] == "c1"
    assert parsed["post_id"] == "post1"  # t3_ prefix stripped
    assert parsed["parent_id"] is None  # parent is the post itself
    assert parsed["depth"] == 0
    assert parsed["created_utc"] == 1781198595


def test_parse_reply_comment():
    parsed = parse_arctic_comment(_arctic_comment(id="c2", parent_id="t1_c1"))
    assert parsed["parent_id"] == "c1"  # t1_ prefix stripped
    assert parsed["depth"] == 1


def test_parse_handles_missing_fields():
    parsed = parse_arctic_comment({"id": "c3"})
    assert parsed["post_id"] == ""
    assert parsed["parent_id"] is None
    assert parsed["created_utc"] == 0


def test_filter_drops_bots_and_deleted():
    raw = [
        _arctic_comment(id="c1"),
        _arctic_comment(id="c2", author="AutoModerator"),
        _arctic_comment(id="c3", body="[deleted]"),
        _arctic_comment(id="c4", body="[removed]"),
    ]
    kept = filter_comments(raw)
    assert [c["id"] for c in kept] == ["c1"]


def test_insert_keeps_known_posts_drops_orphans(conn):
    conn.execute(
        "INSERT INTO posts (id, subreddit, collected_date) VALUES (?, ?, ?)",
        ("post1", "replika", "2026-06-10"),
    )
    parsed = [
        parse_arctic_comment(_arctic_comment(id="c1")),
        parse_arctic_comment(_arctic_comment(id="c2", link_id="t3_unknown")),
    ]
    inserted, orphans = insert_comments_for_known_posts(parsed, "replika", conn)
    assert inserted == 1
    assert orphans == 1
    rows = conn.execute("SELECT id, post_id, subreddit FROM comments").fetchall()
    assert len(rows) == 1
    assert rows[0]["id"] == "c1"
    assert rows[0]["post_id"] == "post1"


def test_insert_forces_canonical_subreddit_casing(conn):
    conn.execute(
        "INSERT INTO posts (id, subreddit, collected_date) VALUES (?, ?, ?)",
        ("post1", "CharacterAI", "2026-06-10"),
    )
    parsed = [parse_arctic_comment(_arctic_comment(subreddit="characterai"))]
    inserted, _ = insert_comments_for_known_posts(parsed, "CharacterAI", conn)
    assert inserted == 1
    row = conn.execute("SELECT subreddit FROM comments").fetchone()
    assert row["subreddit"] == "CharacterAI"


def test_insert_is_idempotent(conn):
    conn.execute(
        "INSERT INTO posts (id, subreddit, collected_date) VALUES (?, ?, ?)",
        ("post1", "replika", "2026-06-10"),
    )
    parsed = [parse_arctic_comment(_arctic_comment())]
    first, _ = insert_comments_for_known_posts(parsed, "replika", conn)
    second, _ = insert_comments_for_known_posts(parsed, "replika", conn)
    assert first == 1
    assert second == 0  # INSERT OR IGNORE absorbed the duplicate
