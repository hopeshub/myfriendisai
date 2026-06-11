"""Tests for arctic-mode snapshot self-healing (rows from our own data)."""

import sqlite3
from datetime import date, datetime, time as dtime, timedelta, timezone

import pytest

from src.db.schema import SCHEMA
from src.db.operations import (
    create_arctic_snapshot_rows,
    update_arctic_comment_averages,
)

DAY = date(2026, 6, 1)


def _epoch(d: date, hour: int = 12) -> int:
    return int(datetime.combine(d, dtime(hour=hour), tzinfo=timezone.utc).timestamp())


@pytest.fixture
def conn():
    c = sqlite3.connect(":memory:")
    c.row_factory = sqlite3.Row
    c.executescript(SCHEMA)
    yield c
    c.close()


def _insert_post(conn, pid, sub, d, author="alice"):
    conn.execute(
        "INSERT INTO posts (id, subreddit, author, created_utc, collected_date) VALUES (?, ?, ?, ?, ?)",
        (pid, sub, author, _epoch(d), d.isoformat()),
    )


def test_creates_rows_with_post_counts(conn):
    _insert_post(conn, "p1", "replika", DAY, "alice")
    _insert_post(conn, "p2", "replika", DAY, "bob")
    _insert_post(conn, "p3", "replika", DAY, "[deleted]")

    created = create_arctic_snapshot_rows(DAY, ["replika", "NomiAI"], conn=conn)
    assert created == 2

    row = conn.execute(
        "SELECT * FROM subreddit_snapshots WHERE subreddit = 'replika'"
    ).fetchone()
    assert row["posts_today"] == 3
    assert row["unique_authors"] == 2  # [deleted] excluded
    assert row["subscribers"] is None
    assert row["data_source"] == "arctic_shift"

    empty = conn.execute(
        "SELECT posts_today FROM subreddit_snapshots WHERE subreddit = 'NomiAI'"
    ).fetchone()
    assert empty["posts_today"] == 0


def test_never_overwrites_real_rows(conn):
    conn.execute(
        "INSERT INTO subreddit_snapshots (subreddit, snapshot_date, subscribers, posts_today) VALUES (?, ?, ?, ?)",
        ("replika", DAY.isoformat(), 83907, 42),
    )
    _insert_post(conn, "p1", "replika", DAY)

    created = create_arctic_snapshot_rows(DAY, ["replika"], conn=conn)
    assert created == 0
    row = conn.execute(
        "SELECT subscribers, posts_today FROM subreddit_snapshots WHERE subreddit = 'replika'"
    ).fetchone()
    assert row["subscribers"] == 83907
    assert row["posts_today"] == 42


def test_idempotent_across_runs(conn):
    _insert_post(conn, "p1", "replika", DAY)
    assert create_arctic_snapshot_rows(DAY, ["replika"], conn=conn) == 1
    assert create_arctic_snapshot_rows(DAY, ["replika"], conn=conn) == 0


def test_comment_averages_fill_only_arctic_rows(conn):
    # Two posts on DAY: 3 comments and 1 comment -> avg 2.0
    _insert_post(conn, "p1", "replika", DAY)
    _insert_post(conn, "p2", "replika", DAY)
    for i, pid in enumerate(["p1", "p1", "p1", "p2"]):
        conn.execute(
            "INSERT INTO comments (id, post_id, subreddit, body, created_utc) VALUES (?, ?, ?, ?, ?)",
            (f"c{i}", pid, "replika", "text", _epoch(DAY + timedelta(days=1))),
        )
    # A real Reddit row for another sub on the same day must not be touched
    conn.execute(
        "INSERT INTO subreddit_snapshots (subreddit, snapshot_date, avg_comments_per_post) VALUES (?, ?, ?)",
        ("NomiAI", DAY.isoformat(), 9.9),
    )
    _insert_post(conn, "p9", "NomiAI", DAY)

    create_arctic_snapshot_rows(DAY, ["replika"], conn=conn)
    updated = update_arctic_comment_averages(DAY, conn=conn)
    assert updated == 1

    arctic = conn.execute(
        "SELECT avg_comments_per_post FROM subreddit_snapshots WHERE subreddit = 'replika'"
    ).fetchone()
    assert arctic["avg_comments_per_post"] == 2.0
    real = conn.execute(
        "SELECT avg_comments_per_post FROM subreddit_snapshots WHERE subreddit = 'NomiAI'"
    ).fetchone()
    assert real["avg_comments_per_post"] == 9.9


def test_posts_outside_day_window_excluded(conn):
    _insert_post(conn, "p1", "replika", DAY)
    _insert_post(conn, "p2", "replika", DAY - timedelta(days=1))
    _insert_post(conn, "p3", "replika", DAY + timedelta(days=1))

    create_arctic_snapshot_rows(DAY, ["replika"], conn=conn)
    row = conn.execute(
        "SELECT posts_today FROM subreddit_snapshots WHERE subreddit = 'replika'"
    ).fetchone()
    assert row["posts_today"] == 1
