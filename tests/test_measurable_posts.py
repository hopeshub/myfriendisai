"""The measurable-post population, decided 2026-09-08.

A **shell** is a post whose stored body is '[removed]' or '[deleted]': the
archive captured it after removal, or while it sat in a moderator queue, so
only its title survived. The published population is posts whose text survived
to capture — keeping shells in the per-1,000 denominator made every rate depend
on how hard a community moderates and on which collection regime was running.

A post with an EMPTY body is not a shell: an image or link post is visible and
its title is matchable, so it stays in.

These tests pin the population at every surface that publishes a count, plus
the two estimator properties the same decision settled: the chart's pooled
monthly rate, and the calendar-based (not hit-day-based) rolling averages.
"""

import csv
import json
import sqlite3
from datetime import date, datetime, timezone

import pytest

from src.db.schema import SCHEMA


def _utc(datestr):
    """Midday UTC on a given day — a post's created_utc."""
    return int(
        datetime.strptime(datestr + " 12:00", "%Y-%m-%d %H:%M")
        .replace(tzinfo=timezone.utc)
        .timestamp()
    )


@pytest.fixture
def conn(tmp_path, monkeypatch):
    c = sqlite3.connect(":memory:")
    c.row_factory = sqlite3.Row
    c.executescript(SCHEMA)
    import src.config as config_mod
    monkeypatch.setattr(
        config_mod, "load_keyword_communities",
        lambda: [{"subreddit": "replika"}],
    )
    yield c
    c.close()


def _post(conn, post_id, day, selftext=None, subreddit="replika", author="u"):
    conn.execute(
        "INSERT INTO posts (id, subreddit, title, author, created_utc, selftext, "
        "collected_date, data_source, num_comments, score) "
        "VALUES (?, ?, 'a title', ?, ?, ?, ?, 'arctic_shift', 3, 5)",
        (post_id, subreddit, author, _utc(day), selftext, day),
    )


def _tag(conn, post_id, day, category="therapy", source="post", subreddit="replika"):
    conn.execute(
        "INSERT INTO post_keyword_tags "
        "(post_id, subreddit, category, matched_term, post_date, source) "
        "VALUES (?, ?, ?, 'therapist', ?, ?)",
        (post_id, subreddit, category, day, source),
    )


def _trends(conn, tmp_path, **kwargs):
    from src.db.operations import export_keyword_trends_json
    out = tmp_path / "keyword_trends.json"
    export_keyword_trends_json(output_path=out, conn=conn, **kwargs)
    return json.loads(out.read_text())


# ── population: the theme numerator and the per-1k denominator ───────────

def test_shells_leave_both_numerator_and_denominator(conn, tmp_path):
    """A '[removed]' post is out of the theme count AND out of _total_posts.

    It has to leave both: a shell can still carry a title-only tag, so
    filtering only the denominator would leave the two describing different
    corpora and push the rate up.
    """
    day = "2026-04-01"
    _post(conn, "real", day, selftext="my therapist said")
    _post(conn, "shell", day, selftext="[removed]")
    _post(conn, "gone", day, selftext="[deleted]")
    _tag(conn, "real", day)
    _tag(conn, "shell", day)   # title-only tag on a removed post
    conn.commit()

    data = _trends(conn, tmp_path)
    assert [e["count"] for e in data["therapy"]] == [1]
    assert [e["count_post_only"] for e in data["therapy"]] == [1]
    assert [e["count"] for e in data["_total_posts"]] == [1]


def test_empty_body_posts_stay_in(conn, tmp_path):
    """Image/link posts — empty or NULL body — are visible and stay counted."""
    day = "2026-04-01"
    _post(conn, "img", day, selftext="")
    _post(conn, "link", day, selftext=None)
    _tag(conn, "img", day)
    _tag(conn, "link", day)
    conn.commit()

    data = _trends(conn, tmp_path)
    assert [e["count_post_only"] for e in data["therapy"]] == [2]
    assert [e["count"] for e in data["_total_posts"]] == [2]


def test_comment_sourced_tag_on_a_shell_is_also_dropped(conn, tmp_path):
    """The post+comment series uses the same population as the post-only one."""
    day = "2026-04-01"
    _post(conn, "shell", day, selftext="[removed]")
    _tag(conn, "shell", day, source="comment")
    conn.commit()

    data = _trends(conn, tmp_path)
    assert "therapy" not in data


def test_community_activity_excludes_shells(conn, tmp_path):
    from src.db.operations import export_community_activity_json
    conn.execute(
        "INSERT INTO subreddit_config (subreddit, category, tier, added_date, is_active) "
        "VALUES ('replika', 'Primary', 1, '2023-01-01', 1)"
    )
    _post(conn, "real", "2024-05-02", selftext="text")
    _post(conn, "img", "2024-05-03", selftext="")
    _post(conn, "shell", "2024-05-04", selftext="[removed]")
    conn.commit()

    out = tmp_path / "community_activity.json"
    export_community_activity_json(output_path=out, conn=conn)
    data = json.loads(out.read_text())
    i = data["months"].index("2024-05")
    assert data["activity"]["replika"][i] == 2


# ── population: posts_today, on all three paths that write or read it ────

def test_aggregate_posts_to_snapshots_posts_today_excludes_shells(conn):
    from src.db.operations import aggregate_posts_to_snapshots
    _post(conn, "real", "2026-04-01", selftext="text")
    _post(conn, "img", "2026-04-01", selftext="")
    _post(conn, "shell", "2026-04-01", selftext="[removed]", author="someone_else")
    conn.commit()

    aggregate_posts_to_snapshots(conn=conn)
    row = conn.execute(
        "SELECT posts_today, unique_authors FROM subreddit_snapshots"
    ).fetchone()
    assert row["posts_today"] == 2
    # People are not text: the removed post's author still counts.
    assert row["unique_authors"] == 2


def test_create_arctic_snapshot_rows_posts_today_excludes_shells(conn):
    from src.db.operations import create_arctic_snapshot_rows
    _post(conn, "real", "2026-04-01", selftext="text")
    _post(conn, "shell", "2026-04-01", selftext="[deleted]", author="someone_else")
    conn.commit()

    create_arctic_snapshot_rows(date(2026, 4, 1), ["replika"], conn=conn)
    row = conn.execute(
        "SELECT posts_today, unique_authors FROM subreddit_snapshots"
    ).fetchone()
    assert row["posts_today"] == 1
    assert row["unique_authors"] == 2


def test_snapshots_for_chart_recount_excludes_shells(conn):
    from src.db.operations import get_all_snapshots_for_chart
    conn.execute(
        "INSERT INTO subreddit_config (subreddit, category, tier, added_date, is_active) "
        "VALUES ('replika', 'Primary', 1, '2023-01-01', 1)"
    )
    conn.execute(
        "INSERT INTO subreddit_snapshots (subreddit, snapshot_date, data_source, posts_today) "
        "VALUES ('replika', '2026-04-01', 'json_endpoint', 99)"
    )
    _post(conn, "real", "2026-04-01", selftext="text")
    _post(conn, "img", "2026-04-01", selftext=None)
    _post(conn, "shell", "2026-04-01", selftext="[removed]")
    conn.commit()

    rows = get_all_snapshots_for_chart(conn=conn)
    assert [r["posts_today"] for r in rows] == [2]


# ── estimator: calendar-based rolling averages ──────────────────────────

def test_post_only_7d_avg_is_calendar_based(conn, tmp_path):
    """Zero-hit days pull the trailing mean down; they used to be skipped.

    Seven consecutive corpus days, hits on the first and the last only. Over
    the calendar the day-7 mean is 2/7. Over hit-days — the old behaviour —
    the window held just those two days and read 1.0.
    """
    days = [f"2026-04-{i:02d}" for i in range(1, 8)]
    for i, d in enumerate(days):
        _post(conn, f"p{i}", d, selftext="text")
    _tag(conn, "p0", days[0])
    _tag(conn, "p6", days[6])
    conn.commit()

    data = _trends(conn, tmp_path)
    last = data["therapy"][-1]
    assert last["date"] == days[6]
    assert last["count_post_only_7d_avg"] == pytest.approx(2 / 7, abs=0.01)
    assert last["count_7d_avg"] == pytest.approx(2 / 7, abs=0.01)


def test_shell_days_do_not_enter_the_rolling_calendar(conn, tmp_path):
    """A day whose only posts were removed is not a corpus day at all."""
    _post(conn, "a", "2026-04-01", selftext="text")
    _post(conn, "shell", "2026-04-02", selftext="[removed]")
    _post(conn, "b", "2026-04-03", selftext="text")
    _tag(conn, "a", "2026-04-01")
    _tag(conn, "b", "2026-04-03")
    conn.commit()

    data = _trends(conn, tmp_path)
    assert [e["date"] for e in data["_total_posts"]] == ["2026-04-01", "2026-04-03"]
    # Two corpus days, two hits → the trailing mean on day 2 of the calendar.
    assert data["therapy"][-1]["count_post_only_7d_avg"] == pytest.approx(1.0)


# ── estimator: the dataset's two rate columns now coincide ──────────────

def test_dataset_charted_rate_equals_pooled_rate(tmp_path):
    import sys
    sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent.parent / "scripts"))
    from export_public_dataset import build_theme_rows

    # Two days: a busy one with a low hit rate, a quiet one with a high rate.
    # A mean of daily ratios would land between them; the pooled rate is
    # weighted by volume and lands near the busy day.
    trends = {
        "_coverage_start": {"romance": "2024-01-01"},
        "_total_posts": [
            {"date": "2024-01-01", "count": 900},
            {"date": "2024-01-02", "count": 100},
        ],
        "romance": [
            {"date": "2024-01-01", "count": 9, "count_post_only": 9,
             "count_post_only_7d_avg": 9},
            {"date": "2024-01-02", "count": 5, "count_post_only": 5,
             "count_post_only_7d_avg": 7},
        ],
    }
    rows = [r for r in build_theme_rows(trends) if r["theme"] == "romance"]
    assert len(rows) == 1
    row = rows[0]
    assert row["post_only_count"] == 14
    assert row["eligible_posts"] == 1000
    assert row["rate_per_1k"] == pytest.approx(14.0)
    assert row["rate_per_1k_charted"] == row["rate_per_1k"]
