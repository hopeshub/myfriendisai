"""Shell-share monitor (handoff D6, 2026-11).

shell_share_by_sub() reports, per keyword sub, the share of posts the archive
stored as shells in the last N days and in the N days before. It feeds
theme_health.json and, through run_collect.sh, status.json and a
non-failing GitHub Actions warning that keys on a RISE, because some subs
(r/ChaiApp) are chronically mostly shells.
"""

import sqlite3
from datetime import date, datetime, timezone

import pytest

from src.db import operations as ops
from src.db.schema import SCHEMA

TODAY = date(2026, 11, 20)   # current window: 2026-09-21 .. 11-19; previous: 07-23 .. 09-20


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


def _fill(conn, sub, day, n, shells):
    for i in range(n):
        _post(conn, sub, day, "[removed]" if i < shells else "text")


def test_current_and_previous_windows(conn):
    _fill(conn, "KindroidAI", "2026-11-01", 60, 36)   # 60% now
    _fill(conn, "KindroidAI", "2026-08-15", 60, 12)   # 20% before
    _fill(conn, "replika", "2026-11-01", 10, 1)
    out = ops.shell_share_by_sub(conn, ["KindroidAI", "replika"], days=60, today=TODAY)
    k = out["by_sub"][0]
    assert k["subreddit"] == "KindroidAI"
    assert (k["posts"], k["shells"], k["pct"]) == (60, 36, 60.0)
    assert (k["prev_posts"], k["prev_pct"], k["change_pts"]) == (60, 20.0, 40.0)
    assert out["overall"]["posts"] == 70 and out["overall"]["shells"] == 37
    assert out["overall"]["prev_pct"] == 20.0
    assert out["rising"] == ["KindroidAI"]
    assert out["high"] == ["KindroidAI"]


def test_chronically_high_sub_is_high_but_not_rising(conn):
    _fill(conn, "ChaiApp", "2026-11-01", 100, 90)
    _fill(conn, "ChaiApp", "2026-08-15", 100, 88)
    out = ops.shell_share_by_sub(conn, ["ChaiApp"], days=60, today=TODAY)
    assert out["high"] == ["ChaiApp"]
    assert out["rising"] == []


def test_rise_needs_enough_posts_in_both_windows(conn):
    _fill(conn, "aipartners", "2026-11-01", 60, 45)
    _fill(conn, "aipartners", "2026-08-15", ops.SHELL_SHARE_MIN_POSTS - 1, 0)
    out = ops.shell_share_by_sub(conn, ["aipartners"], days=60, today=TODAY)
    assert out["by_sub"][0]["change_pts"] == 75.0
    assert out["rising"] == []


def test_posts_older_than_both_windows_are_ignored(conn):
    _fill(conn, "aipartners", "2026-05-01", 40, 40)
    _fill(conn, "aipartners", "2026-11-10", 40, 0)
    out = ops.shell_share_by_sub(conn, ["aipartners"], days=60, today=TODAY)
    r = out["by_sub"][0]
    assert (r["posts"], r["shells"], r["prev_posts"]) == (40, 0, 0)
    assert r["change_pts"] is None


def test_empty_body_is_not_a_shell_and_excluded_authors_are_left_out(conn, monkeypatch):
    monkeypatch.setattr(ops, "EXCLUDED_AUTHORS", ("bot",))
    _post(conn, "replika", "2026-11-01", "")          # image/link post: not a shell
    _post(conn, "replika", "2026-11-01", None)        # no body: not a shell
    _post(conn, "replika", "2026-11-01", "[removed]", author="bot")  # excluded author
    out = ops.shell_share_by_sub(conn, ["replika"], days=60, today=TODAY)
    assert out["overall"]["posts"] == 2 and out["overall"]["shells"] == 0


def test_other_subs_are_ignored(conn):
    _post(conn, "ChatGPT", "2026-11-01", "[removed]")
    out = ops.shell_share_by_sub(conn, ["replika"], days=60, today=TODAY)
    assert out["by_sub"] == [] and out["overall"]["posts"] == 0
