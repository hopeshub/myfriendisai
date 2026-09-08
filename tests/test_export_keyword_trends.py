"""Tests for export_keyword_trends_json dual-metric output.

Verifies the post-only control series is correctly emitted alongside
the post+comment default, and that scope filtering / dedup / rolling
averages match the contract documented in src/db/operations.py.
"""

import calendar
import json
import sqlite3
from pathlib import Path

import pytest

from src.db.schema import SCHEMA


@pytest.fixture
def conn_and_patches(tmp_path, monkeypatch):
    """In-memory SQLite wired into the export module."""
    c = sqlite3.connect(":memory:")
    c.row_factory = sqlite3.Row
    c.executescript(SCHEMA)

    # Route load_keyword_communities (used inside the export) to a fixed
    # active-sub list so tests don't depend on config/communities.yaml.
    import src.config as config_mod
    monkeypatch.setattr(
        config_mod, "load_keyword_communities",
        lambda: [{"subreddit": "replika"}, {"subreddit": "CharacterAI"}],
    )

    yield c, tmp_path
    c.close()


def _seed_post(conn, post_id, subreddit="replika", created_utc=1_760_000_000):
    conn.execute(
        "INSERT INTO posts (id, subreddit, created_utc, collected_date) VALUES (?, ?, ?, ?)",
        (post_id, subreddit, created_utc, "2026-01-01"),
    )


def _seed_tag(conn, post_id, category, term, post_date, source, subreddit="replika"):
    conn.execute(
        "INSERT INTO post_keyword_tags (post_id, subreddit, category, matched_term, post_date, source) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (post_id, subreddit, category, term, post_date, source),
    )


def _run_export(conn, tmp_path):
    from src.db.operations import export_keyword_trends_json
    out = tmp_path / "keyword_trends.json"
    export_keyword_trends_json(output_path=out, conn=conn)
    return json.loads(out.read_text())


def test_dual_metric_fields_present(conn_and_patches):
    conn, tmp_path = conn_and_patches
    _seed_post(conn, "p1")
    _seed_tag(conn, "p1", "therapy", "therapist", "2026-03-20", "post")
    conn.commit()

    data = _run_export(conn, tmp_path)
    entry = data["therapy"][0]
    assert set(entry.keys()) == {
        "date", "count", "count_7d_avg",
        "count_post_only", "count_post_only_7d_avg",
    }
    assert entry["count"] == 1
    assert entry["count_post_only"] == 1


def test_comment_only_hit_counts_total_but_not_post_only(conn_and_patches):
    conn, tmp_path = conn_and_patches
    _seed_post(conn, "p1")
    _seed_tag(conn, "p1", "addiction", "relapsed", "2026-03-20", "comment")
    conn.commit()

    data = _run_export(conn, tmp_path)
    entry = data["addiction"][0]
    assert entry["count"] == 1
    assert entry["count_post_only"] == 0


def test_both_sources_still_count_one_post(conn_and_patches):
    conn, tmp_path = conn_and_patches
    _seed_post(conn, "p1")
    _seed_tag(conn, "p1", "rupture", "nerfed", "2026-03-20", "post")
    _seed_tag(conn, "p1", "rupture", "lobotomy", "2026-03-20", "comment")
    conn.commit()

    data = _run_export(conn, tmp_path)
    entry = data["rupture"][0]
    # DISTINCT post_id — same post matched via both sources is still 1
    assert entry["count"] == 1
    assert entry["count_post_only"] == 1


def test_out_of_scope_subs_excluded(conn_and_patches):
    """Tags from subreddits not in load_keyword_communities() must not appear."""
    conn, tmp_path = conn_and_patches
    _seed_post(conn, "p1", subreddit="ChatGPT")  # T0 not in patched list
    _seed_tag(conn, "p1", "therapy", "therapist", "2026-03-20", "post", subreddit="ChatGPT")
    conn.commit()

    data = _run_export(conn, tmp_path)
    # Category absent because only match was in an excluded sub
    assert "therapy" not in data


def test_rolling_average_over_7_day_window(conn_and_patches):
    """One hit per day for 8 consecutive days → rolling avg stays 1.0.

    Each post is created on the day it is tagged, so the corpus calendar (the
    window's index) is exactly those 8 days.
    """
    conn, tmp_path = conn_and_patches
    base = calendar.timegm((2026, 3, 1, 12, 0, 0))
    dates = [f"2026-03-{i:02d}" for i in range(1, 9)]
    for i, d in enumerate(dates):
        pid = f"p{i}"
        _seed_post(conn, pid, created_utc=base + i * 86_400)
        _seed_tag(conn, pid, "romance", "my ai boyfriend", d, "post")
    conn.commit()

    data = _run_export(conn, tmp_path)
    for entry in data["romance"]:
        assert entry["count"] == 1
        assert entry["count_7d_avg"] == 1.0
        assert entry["count_post_only_7d_avg"] == 1.0


def test_rolling_average_window_is_the_corpus_calendar(conn_and_patches):
    """The 7-day mean is over CORPUS days, not over the theme's hit-days.

    Regression for the defect where `count_post_only_7d_avg` was a mean over
    the last 7 entries of the category's own series: zero-hit days are absent
    from that series, so three consecutive hit-days averaged to 1.0 no matter
    how empty the surrounding week was. With the corpus calendar as the index
    a hitless corpus day is a real 0 and the divisor is the window length.
    """
    conn, tmp_path = conn_and_patches

    # Gapless corpus calendar: one post every day, 2026-03-01 .. 2026-03-20.
    base = calendar.timegm((2026, 3, 1, 12, 0, 0))
    days = [f"2026-03-{d:02d}" for d in range(1, 21)]
    for i, d in enumerate(days):
        _seed_post(conn, f"corpus{i}", created_utc=base + i * 86_400)

    # Theme hits on three consecutive days only, then nothing for a week.
    hit_days = ["2026-03-10", "2026-03-11", "2026-03-12"]
    for i, d in enumerate(hit_days):
        pid = f"hit{i}"
        _seed_post(conn, pid, created_utc=calendar.timegm(
            (2026, 3, 10 + i, 13, 0, 0)))
        _seed_tag(conn, pid, "therapy", "therapist", d, "post")
    conn.commit()

    data = _run_export(conn, tmp_path)

    # The corpus calendar is gapless, so it is the denominator's index too.
    assert [e["date"] for e in data["_total_posts"]] == days
    # Zero-hit days are NOT emitted as entries (keeps the export small).
    assert [e["date"] for e in data["therapy"]] == hit_days

    by_date = {e["date"]: e for e in data["therapy"]}
    # 2026-03-10 is the 10th corpus day, so the window is the full 7 days
    # 03-04..03-10 and holds exactly one hit.
    assert by_date["2026-03-10"]["count_post_only_7d_avg"] == round(1 / 7, 2)
    assert by_date["2026-03-11"]["count_post_only_7d_avg"] == round(2 / 7, 2)
    # The day the old hit-day window reported as 1.0:
    assert by_date["2026-03-12"]["count_post_only_7d_avg"] == round(3 / 7, 2)
    assert by_date["2026-03-12"]["count_post_only_7d_avg"] != 1.0
    # The post+comment series shares the definition.
    assert by_date["2026-03-12"]["count_7d_avg"] == round(3 / 7, 2)


def test_rolling_average_window_ramps_up_at_start_of_corpus(conn_and_patches):
    """At the very start of the corpus the window is short, as it is for the
    denominator: calendar[max(0, i-6) : i+1] has fewer than 7 entries."""
    conn, tmp_path = conn_and_patches
    base = calendar.timegm((2026, 3, 1, 12, 0, 0))
    for i in range(5):
        pid = f"p{i}"
        _seed_post(conn, pid, created_utc=base + i * 86_400)
        _seed_tag(conn, pid, "romance", "my ai boyfriend", f"2026-03-{i + 1:02d}", "post")
    conn.commit()

    data = _run_export(conn, tmp_path)
    by_date = {e["date"]: e for e in data["romance"]}
    # Day 1 of the corpus: window length 1. Day 5: window length 5.
    assert by_date["2026-03-01"]["count_post_only_7d_avg"] == 1.0
    assert by_date["2026-03-05"]["count_post_only_7d_avg"] == 1.0


def test_total_posts_series_included(conn_and_patches):
    conn, tmp_path = conn_and_patches
    _seed_post(conn, "p1", created_utc=1_740_000_000)  # 2025-02-19 UTC
    _seed_post(conn, "p2", created_utc=1_740_000_000)
    conn.commit()

    data = _run_export(conn, tmp_path)
    assert "_total_posts" in data
    assert sum(e["count"] for e in data["_total_posts"]) == 2
