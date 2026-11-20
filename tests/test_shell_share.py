"""Shell-share monitor (handoff D6, 2026-11).

shell_share_by_sub() reports, per keyword sub, the share of the last N days'
posts the archive stored as shells. It feeds theme_health.json and, through
run_collect.sh, status.json and a non-failing GitHub Actions warning.
"""

import sqlite3
from datetime import date, datetime, timezone

import pytest

from src.db import operations as ops
from src.db.schema import SCHEMA


def _utc(datestr):
    return int(
        datetime.strptime(datestr + " 12:00", "%Y-%m-%d %H:%M")
        .replace(tzinfo=timezone.utc)
        .timestamp()
    )


@pytest.fixture
def conn():
    c = sqlite3.connect(":memory:")
    c.executescript(SCHEMA)
    yield c
    c.close()


_n = 0


def _post(conn, sub, day, selftext="real text", author="u"):
    global _n
    _n += 1
    conn.execute(
        "INSERT INTO posts (id, subreddit, title, author, created_utc, selftext, "
        "collected_date, data_source, num_comments, score) "
        "VALUES (?, ?, 't', ?, ?, ?, ?, 'arctic_shift', 0, 0)",
        (f"p{_n}", sub, author, _utc(day), selftext, day),
    )


def test_share_per_sub_and_overall(conn):
    today = date(2026, 11, 20)
    for i in range(40):
        _post(conn, "KindroidAI", "2026-11-01", "[removed]" if i < 24 else "text")
    for i in range(10):
        _post(conn, "replika", "2026-11-01", "[deleted]" if i < 1 else "text")
    out = ops.shell_share_by_sub(conn, ["KindroidAI", "replika"], days=60, today=today)
    assert out["overall"] == {"posts": 50, "shells": 25, "pct": 50.0}
    assert out["by_sub"][0] == {"subreddit": "KindroidAI", "posts": 40, "shells": 24, "pct": 60.0}
    assert out["by_sub"][1]["pct"] == 10.0
    assert out["over_threshold"] == ["KindroidAI"]


def test_window_excludes_older_posts(conn):
    today = date(2026, 11, 20)
    for _ in range(40):
        _post(conn, "aipartners", "2026-08-01", "[removed]")  # >60 days back
    for _ in range(40):
        _post(conn, "aipartners", "2026-11-10", "text")
    out = ops.shell_share_by_sub(conn, ["aipartners"], days=60, today=today)
    assert out["overall"]["posts"] == 40
    assert out["overall"]["shells"] == 0
    assert out["over_threshold"] == []


def test_small_subs_do_not_warn(conn):
    today = date(2026, 11, 20)
    for _ in range(ops.SHELL_SHARE_MIN_POSTS - 1):
        _post(conn, "AI_Addiction", "2026-11-01", "[removed]")
    out = ops.shell_share_by_sub(conn, ["AI_Addiction"], days=60, today=today)
    assert out["by_sub"][0]["pct"] == 100.0
    assert out["over_threshold"] == []


def test_empty_body_is_not_a_shell_and_excluded_authors_are_left_out(conn, monkeypatch):
    today = date(2026, 11, 20)
    monkeypatch.setattr(ops, "EXCLUDED_AUTHORS", ("bot",))
    _post(conn, "replika", "2026-11-01", "")          # image/link post: not a shell
    _post(conn, "replika", "2026-11-01", None)        # no body: not a shell
    _post(conn, "replika", "2026-11-01", "[removed]", author="bot")  # excluded author
    out = ops.shell_share_by_sub(conn, ["replika"], days=60, today=today)
    assert out["overall"] == {"posts": 2, "shells": 0, "pct": 0.0}


def test_other_subs_are_ignored(conn):
    today = date(2026, 11, 20)
    _post(conn, "ChatGPT", "2026-11-01", "[removed]")
    out = ops.shell_share_by_sub(conn, ["replika"], days=60, today=today)
    assert out["by_sub"] == [] and out["overall"]["posts"] == 0
