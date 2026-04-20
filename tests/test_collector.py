"""Tests for src/collector parsing and metric computation."""

from datetime import datetime, timezone

import pytest

from src.collector import _calc_metrics, _normalize_subreddit, _parse_posts


def _child(**data):
    """Helper: wrap a post dict in the envelope Reddit returns."""
    return {"kind": "t3", "data": data}


def test_parse_posts_extracts_core_fields():
    posts = _parse_posts([
        _child(id="abc", subreddit="replika", title="hi", author="alice",
               created_utc=1_700_000_000, score=5, num_comments=2,
               upvote_ratio=0.9, is_self=True, selftext="body", url="https://example.com"),
    ])
    assert len(posts) == 1
    p = posts[0]
    assert p["id"] == "abc"
    assert p["subreddit"] == "replika"
    assert p["title"] == "hi"
    assert p["author"] == "alice"
    assert p["created_utc"] == 1_700_000_000
    assert p["score"] == 5
    assert p["num_comments"] == 2
    assert p["upvote_ratio"] == 0.9
    assert p["is_self"] is True
    assert p["data_source"] == "json_endpoint"
    assert p["raw_json"]


def test_parse_posts_tolerates_missing_fields():
    # Reddit occasionally omits fields — must not crash
    posts = _parse_posts([_child(id="abc")])
    p = posts[0]
    assert p["id"] == "abc"
    assert p["subreddit"] == ""
    assert p["title"] == ""
    assert p["author"] == ""
    assert p["created_utc"] is None
    assert p["score"] is None
    assert p["is_self"] is False  # bool(None) == False


def test_parse_posts_empty_list():
    assert _parse_posts([]) == []


def test_calc_metrics_empty_listing():
    m = _calc_metrics({"subscribers": 100}, [])
    assert m["subscribers"] == 100
    assert m["posts_today"] == 0
    assert m["avg_comments_per_post"] is None
    assert m["avg_score_per_post"] is None
    assert m["unique_authors"] is None


def test_calc_metrics_computes_averages_ignoring_nulls():
    now = datetime.now(timezone.utc).timestamp()
    children = [
        _child(created_utc=now - 100, score=10, num_comments=4, author="a"),
        _child(created_utc=now - 200, score=None, num_comments=2, author="b"),
        _child(created_utc=now - 300, score=4, num_comments=None, author="[deleted]"),
    ]
    m = _calc_metrics({"subscribers": 50, "active_user_count": None}, children)
    assert m["avg_comments_per_post"] == 3.0       # (4 + 2) / 2, None excluded
    assert m["avg_score_per_post"] == 7.0          # (10 + 4) / 2, None excluded
    assert m["unique_authors"] == 2                # [deleted] excluded


def test_calc_metrics_posts_today_window():
    now = datetime.now(timezone.utc).timestamp()
    children = [
        _child(created_utc=now - 1000),            # in window
        _child(created_utc=now - 86400 - 100),     # just outside 24h
        _child(created_utc=None),                  # must not crash
    ]
    m = _calc_metrics({}, children)
    assert m["posts_today"] == 1


def test_calc_metrics_passes_through_visitor_fields():
    m = _calc_metrics(
        {"subscribers": 1, "visitors_7d": 42, "contributions_7d": 7},
        [],
    )
    assert m["visitors_7d"] == 42
    assert m["contributions_7d"] == 7


def test_normalize_subreddit_canonicalizes_casing():
    # Reddit returns 'Replika' but config uses 'replika' — must normalize
    posts = [{"subreddit": "Replika"}, {"subreddit": "rePLIka"}]
    out = _normalize_subreddit(posts, "replika")
    assert all(p["subreddit"] == "replika" for p in out)


def test_normalize_subreddit_leaves_mismatches_alone():
    # Defensive: if a post has a completely different subreddit name
    # (shouldn't happen but could via cross-posts), don't rewrite it
    posts = [{"subreddit": "SomeOther"}]
    out = _normalize_subreddit(posts, "replika")
    assert out[0]["subreddit"] == "SomeOther"


def test_normalize_subreddit_handles_missing_key():
    posts = [{}]
    out = _normalize_subreddit(posts, "replika")
    # Should not crash and should not add 'replika' since the sub was missing
    assert out[0].get("subreddit", "") == ""
