"""Tests for export_keyword_trends_json dual-metric output.

Verifies the post-only control series is correctly emitted alongside
the post+comment default, and that scope filtering / dedup / rolling
averages match the contract documented in src/db/operations.py.
"""

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
    """One hit per day for 8 consecutive days → rolling avg stays 1.0."""
    conn, tmp_path = conn_and_patches
    dates = [f"2026-03-{i:02d}" for i in range(1, 9)]
    for i, d in enumerate(dates):
        pid = f"p{i}"
        _seed_post(conn, pid, created_utc=1_760_000_000 + i)
        _seed_tag(conn, pid, "romance", "my ai boyfriend", d, "post")
    conn.commit()

    data = _run_export(conn, tmp_path)
    for entry in data["romance"]:
        assert entry["count"] == 1
        assert entry["count_7d_avg"] == 1.0
        assert entry["count_post_only_7d_avg"] == 1.0


def test_total_posts_series_included(conn_and_patches):
    conn, tmp_path = conn_and_patches
    _seed_post(conn, "p1", created_utc=1_740_000_000)  # 2025-02-19 UTC
    _seed_post(conn, "p2", created_utc=1_740_000_000)
    conn.commit()

    data = _run_export(conn, tmp_path)
    assert "_total_posts" in data
    assert sum(e["count"] for e in data["_total_posts"]) == 2
