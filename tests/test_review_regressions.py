"""Regression tests for the 2026-06-09 review fixes.

Locks in the invariants that broke (or nearly broke) when Reddit killed
unauthenticated .json access and the Arctic Shift fallback was added:

1. Keyword-scope gating: T0/T4 and exclude_from_keywords subs can never
   enter the keyword pipeline; deactivated subs (r/HeavenGF) stay in the
   historical corpus.
2. OAuth credential handling in RedditClient (mode selection, env parsing).
3. Arctic Shift fetch: truncated windows are surfaced, not silently
   returned as complete; 429s count against retries.
4. The daily fallback canonicalizes subreddit casing and refuses
   truncated windows.
5. coverage_start treats zero-tag gap months as 0, not as absent.
"""

import json
import sqlite3

import pytest

from src.db.schema import SCHEMA


# ── 1. Keyword-scope gating (runs against the real config) ──────────────────

def test_keyword_communities_only_tiers_1_to_3():
    from src.config import load_keyword_communities
    for c in load_keyword_communities():
        assert c["tier"] in (1, 2, 3), f"r/{c['subreddit']} (tier {c['tier']}) leaked into keyword scope"


def test_keyword_communities_respect_exclude_flag():
    from src.config import load_keyword_communities
    for c in load_keyword_communities():
        assert not c.get("exclude_from_keywords", False), \
            f"r/{c['subreddit']} carries exclude_from_keywords but is in keyword scope"


def test_no_t4_sub_in_keyword_scope_by_name():
    from src.config import _load_all_communities, load_keyword_communities
    t4_names = {c["subreddit"] for c in _load_all_communities() if c.get("tier") == 4}
    assert t4_names, "expected T4 subs in config"
    keyword_names = {c["subreddit"] for c in load_keyword_communities()}
    assert not (t4_names & keyword_names)


def test_deactivated_sub_stays_in_keyword_corpus_but_not_collection():
    from src.config import load_communities, load_keyword_communities
    collected = {c["subreddit"] for c in load_communities()}
    keyword = {c["subreddit"] for c in load_keyword_communities()}
    # r/HeavenGF was banned by Reddit (~May 2026): never collected again,
    # but its historical posts stay in numerator and denominator.
    assert "HeavenGF" not in collected
    assert "HeavenGF" in keyword


# ── 2. OAuth credentials ─────────────────────────────────────────────────────

def _write_creds(tmp_path, text):
    p = tmp_path / "creds.env"
    p.write_text(text)
    return p


def test_load_oauth_creds_missing_file(tmp_path, monkeypatch):
    import src.reddit_client as rc
    monkeypatch.setattr(rc, "CREDS_PATH", tmp_path / "nope.env")
    assert rc.load_oauth_creds() is None


def test_load_oauth_creds_empty_values(tmp_path, monkeypatch):
    import src.reddit_client as rc
    monkeypatch.setattr(rc, "CREDS_PATH", _write_creds(
        tmp_path, "# template\nREDDIT_CLIENT_ID=\nREDDIT_CLIENT_SECRET=\n"))
    assert rc.load_oauth_creds() is None


def test_load_oauth_creds_valid_and_quoted(tmp_path, monkeypatch):
    import src.reddit_client as rc
    monkeypatch.setattr(rc, "CREDS_PATH", _write_creds(
        tmp_path, "# comment\nREDDIT_CLIENT_ID='abc123'\nREDDIT_CLIENT_SECRET=\"s3cret\"\n"))
    assert rc.load_oauth_creds() == ("abc123", "s3cret")


def test_client_unauth_mode_without_creds(monkeypatch):
    import src.reddit_client as rc
    monkeypatch.setattr(rc, "load_oauth_creds", lambda: None)
    client = rc.RedditClient()
    assert not client.is_authenticated
    assert client.base_url == rc.BASE_URL
    assert client.rate_limiter.min_interval == rc.UNAUTH_MIN_INTERVAL


def test_client_oauth_mode_with_creds(monkeypatch):
    import src.reddit_client as rc
    monkeypatch.setattr(rc, "load_oauth_creds", lambda: ("id", "secret"))
    client = rc.RedditClient()
    assert client.is_authenticated
    assert client.base_url == rc.OAUTH_BASE_URL
    assert client.rate_limiter.min_interval == rc.OAUTH_MIN_INTERVAL


# ── 3. Arctic Shift fetch: truncation and 429 retries ───────────────────────

class _FakeResp:
    def __init__(self, status_code, payload=None):
        self.status_code = status_code
        self._payload = payload or {}

    def json(self):
        return self._payload


def test_fetch_posts_non_200_is_truncated(monkeypatch):
    import scripts.backfill_arctic as ba
    monkeypatch.setattr(ba.requests, "get", lambda *a, **k: _FakeResp(422))
    posts, truncated = ba.fetch_posts("replika", 1_000, 2_000)
    assert posts == []
    assert truncated is True


def test_fetch_posts_persistent_429_is_truncated(monkeypatch):
    import scripts.backfill_arctic as ba
    monkeypatch.setattr(ba.requests, "get", lambda *a, **k: _FakeResp(429))
    monkeypatch.setattr(ba.time, "sleep", lambda s: None)
    posts, truncated = ba.fetch_posts("replika", 1_000, 2_000)
    assert truncated is True  # must give up, not loop forever


def test_fetch_posts_clean_short_page_not_truncated(monkeypatch):
    import scripts.backfill_arctic as ba
    payload = {"data": [{"id": "x1", "created_utc": 1_500, "subreddit": "replika"}]}
    monkeypatch.setattr(ba.requests, "get", lambda *a, **k: _FakeResp(200, payload))
    posts, truncated = ba.fetch_posts("replika", 1_000, 2_000)
    assert len(posts) == 1
    assert truncated is False


def test_parse_arctic_post_fields():
    from scripts.backfill_arctic import parse_arctic_post
    p = parse_arctic_post({"id": "x1", "subreddit": "replika", "created_utc": 1_760_000_000})
    assert p["data_source"] == "arctic_shift"
    assert p["collected_date"] == "2025-10-09"  # derived from created_utc, UTC


# ── 4. Daily fallback: canonical casing + truncation refusal ────────────────

@pytest.fixture
def mem_conn():
    c = sqlite3.connect(":memory:")
    c.row_factory = sqlite3.Row
    c.executescript(SCHEMA)
    yield c
    c.close()


def test_fallback_canonicalizes_subreddit_casing(monkeypatch, mem_conn):
    import scripts.backfill_arctic as ba
    from scripts.collect_daily import _step_collect_posts_arctic

    raw = [{"id": "z1", "subreddit": "character_ai_recovery",
            "title": "t", "created_utc": 1_760_000_000}]
    monkeypatch.setattr(ba, "fetch_posts", lambda *a, **k: (raw, False))

    stats = _step_collect_posts_arctic(
        [{"subreddit": "Character_AI_Recovery"}], mem_conn)

    assert stats["ok"] == 1 and stats["errors"] == 0
    row = mem_conn.execute("SELECT subreddit FROM posts WHERE id='z1'").fetchone()
    assert row["subreddit"] == "Character_AI_Recovery"


def test_fallback_counts_truncated_window_as_error(monkeypatch, mem_conn):
    import scripts.backfill_arctic as ba
    from scripts.collect_daily import _step_collect_posts_arctic

    monkeypatch.setattr(ba, "fetch_posts", lambda *a, **k: ([], True))
    stats = _step_collect_posts_arctic([{"subreddit": "replika"}], mem_conn)
    assert stats["ok"] == 0 and stats["errors"] == 1


# ── 5. coverage_start: gap months count as zero ──────────────────────────────

def test_coverage_start_rejects_candidate_before_gap_month(tmp_path, monkeypatch, mem_conn):
    import src.config as config_mod
    monkeypatch.setattr(config_mod, "load_keyword_communities",
                        lambda: [{"subreddit": "replika"}])

    # 5 tagged posts in 2025-01, ZERO in 2025-02, 5 in 2025-03.
    # The documented rule ("every later completed month >= 5") must treat the
    # empty gap month as 0 and reject 2025-01 as coverage_start.
    def seed(month, day_base, n):
        for i in range(n):
            pid = f"p{month}{i}"
            mem_conn.execute(
                "INSERT INTO posts (id, subreddit, created_utc, collected_date) "
                "VALUES (?, 'replika', strftime('%s', ?), ?)",
                (pid, f"2025-{month}-0{day_base + i % 5 + 1}", "2025-12-01"),
            )
            mem_conn.execute(
                "INSERT INTO post_keyword_tags (post_id, subreddit, category, "
                "matched_term, post_date, source) VALUES (?, 'replika', 'romance', "
                "'kw', ?, 'post')",
                (pid, f"2025-{month}-0{day_base + i % 5 + 1}"),
            )

    seed("01", 1, 5)
    seed("03", 1, 5)
    mem_conn.commit()

    from src.db.operations import export_keyword_trends_json
    out = tmp_path / "kt.json"
    export_keyword_trends_json(output_path=out, conn=mem_conn)
    cs = json.loads(out.read_text())["_coverage_start"]
    assert cs["romance"] == "2025-03-01", \
        f"gap month 2025-02 must disqualify 2025-01 (got {cs['romance']})"
