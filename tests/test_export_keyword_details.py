"""Tests for scripts/export_keyword_details.py: the drift-based "contested"
status override and the cross-keyword sample-post dedupe."""

import json
import sqlite3
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.db.schema import SCHEMA  # noqa: E402
import scripts.export_keyword_details as ekd  # noqa: E402


def test_load_latest_drift_precision_takes_latest_post_level(tmp_path):
    hist = {
        "keywords": {
            "screen time": {"history": [
                {"date": "2026-08-08", "quarter": "2026-07", "level": "post", "precision": 0.80},
                {"date": "2026-08-27", "quarter": "2026-08", "level": "comment", "precision": 0.10},
                {"date": "2026-08-27", "quarter": "2026-08", "level": "post", "precision": 0.52},
            ]},
            "no posts": {"history": [{"date": "2026-08-27", "level": "comment", "precision": 0.2}]},
        }
    }
    path = tmp_path / "drift.json"
    path.write_text(json.dumps(hist))
    latest = ekd.load_latest_drift_precision(path)
    assert latest == {"screen time": 0.52}
    assert ekd.load_latest_drift_precision(tmp_path / "missing.json") == {}


def test_apply_drift_status_marks_below_cut_only_and_wins_over_other_statuses():
    cats = {"addiction": [
        {"term": "screen time", "precision": 89.0, "status": None},
        {"term": "relapse", "precision": 95.0, "status": None},
        {"term": "ai therapy", "precision": 73.3, "status": "low-volume"},
        {"term": "unmeasured", "precision": 81.0, "status": "researcher-accepted"},
    ]}
    drift = {"screen time": 0.52, "relapse": 0.91, "ai therapy": 0.484}
    out = ekd.apply_drift_status(cats, drift)["addiction"]
    by = {t["term"]: t["status"] for t in out}
    assert by["screen time"] == "audit-gate-fail"   # below 0.60 -> contested
    assert by["relapse"] is None                    # fine -> unchanged
    assert by["ai therapy"] == "audit-gate-fail"    # override wins over low-volume
    assert by["unmeasured"] == "researcher-accepted"  # no drift data -> unchanged


def test_real_drift_history_flags_known_drifted_keywords():
    latest = ekd.load_latest_drift_precision()
    if not latest:
        pytest.skip("drift_history.json not available")
    assert latest["screen time"] < ekd.DRIFT_CONTESTED_BELOW
    cats = ekd.parse_keywords_yaml(ekd.KEYWORDS_PATH)
    status = {t["term"]: t["status"] for terms in cats.values() for t in terms}
    assert status["screen time"] == "audit-gate-fail"


def _db():
    conn = sqlite3.connect(":memory:")
    conn.executescript(SCHEMA)
    return conn


def _post(conn, pid, day, title):
    conn.execute(
        "INSERT INTO posts (id, subreddit, created_utc, collected_date, title, selftext) "
        "VALUES (?, 'replika', strftime('%s', ?), ?, ?, ?)",
        (pid, day, day, title, f"body of {pid}"),
    )


def _tag(conn, pid, day, cat, term):
    conn.execute(
        "INSERT INTO post_keyword_tags (post_id, subreddit, category, matched_term, "
        "post_date, source) VALUES (?, 'replika', ?, ?, ?, 'post')",
        (pid, cat, term, day),
    )


def test_sample_posts_prefer_posts_not_used_by_another_keyword():
    conn = _db()
    # Post A (newest) matches both keywords; post B only the second one.
    _post(conn, "A", "2026-09-01", "A title")
    _post(conn, "B", "2026-08-01", "B title")
    _tag(conn, "A", "2026-09-01", "romance", "wedding")
    _tag(conn, "A", "2026-09-01", "sexual_erp", "sex with")
    _tag(conn, "B", "2026-08-01", "sexual_erp", "sex with")
    conn.commit()
    cats = {
        "romance": [{"term": "wedding", "precision": 90.0, "status": None}],
        "sexual_erp": [{"term": "sex with", "precision": 90.0, "status": None}],
    }
    result = ekd.build_keyword_details(conn, cats, ["replika"])
    first_romance = result["romance"]["keywords"][0]["sample_posts"][0]["id"]
    erp_ids = [sp["id"] for sp in result["sexual_erp"]["keywords"][0]["sample_posts"]]
    assert first_romance == "A"
    assert erp_ids[0] == "B", "the post already shown for another keyword must not lead"
    assert erp_ids == ["B", "A"], "used posts still fill a shortfall, after fresh ones"
