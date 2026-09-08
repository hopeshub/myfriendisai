"""Tests for shell-post repair: the insert_posts upsert, retagging, and refresh.

A "shell" is a stored post whose body is '[removed]'/'[deleted]' because Arctic
Shift archived it while it was still in a moderator queue. The rules under test:
a shell may be upgraded by real text, a real body may never be downgraded, and a
repaired post's post-source tags are rebuilt from its new text.
"""

import json
import sqlite3
from datetime import datetime, timedelta, timezone

import pytest

from src.db.schema import SCHEMA
from src.db.operations import insert_posts, retag_posts
from src.keyword_matching import build_patterns
import scripts.refresh_shell_posts as rsp

SUB = "replika"          # T1 — keyword-eligible
OTHER_SUB = "ChatGPT"    # T0 — never keyword-tagged

NOW = int(datetime(2026, 8, 20, 12, 0, tzinfo=timezone.utc).timestamp())


@pytest.fixture
def conn():
    c = sqlite3.connect(":memory:")
    c.row_factory = sqlite3.Row
    c.executescript(SCHEMA)
    yield c
    c.close()


def _post(pid, **overrides):
    """A post dict shaped like parse_arctic_post's output."""
    base = {
        "id": pid, "subreddit": SUB, "title": "A title", "author": "alice",
        "created_utc": NOW, "score": 1, "num_comments": 0, "upvote_ratio": 0.5,
        "is_self": True, "selftext": "[removed]", "url": "",
        "collected_date": "2026-08-20", "data_source": "arctic_shift",
    }
    base.update(overrides)
    return base


def _stored(conn, pid):
    return conn.execute("SELECT * FROM posts WHERE id = ?", (pid,)).fetchone()


# ── 1. insert_posts upsert rules ────────────────────────────────────────────

def test_new_post_is_inserted_and_not_reported_as_updated(conn):
    updated = []
    assert insert_posts([_post("p1")], conn=conn, updated_ids=updated) == 1
    assert updated == []


def test_shell_is_upgraded_when_archive_gains_a_body(conn):
    insert_posts([_post("p1", score=1, num_comments=0)], conn=conn)

    updated = []
    inserted = insert_posts(
        [_post("p1", selftext="the real body", score=42, num_comments=7)],
        conn=conn, updated_ids=updated,
    )

    assert inserted == 0  # a repair is not a new row
    assert updated == ["p1"]
    row = _stored(conn, "p1")
    assert row["selftext"] == "the real body"
    assert row["score"] == 42 and row["num_comments"] == 7


def test_stored_body_is_never_downgraded_to_a_shell(conn):
    insert_posts([_post("p1", selftext="the real body", score=42)], conn=conn)

    updated = []
    inserted = insert_posts(
        [_post("p1", selftext="[removed]", score=0)], conn=conn, updated_ids=updated,
    )

    assert inserted == 0 and updated == []
    row = _stored(conn, "p1")
    assert row["selftext"] == "the real body"
    assert row["score"] == 42  # nothing about the row was touched


@pytest.mark.parametrize("incoming", ["", None, "[deleted]"])
def test_shell_is_left_alone_when_incoming_has_no_real_text(conn, incoming):
    insert_posts([_post("p1")], conn=conn)

    updated = []
    insert_posts([_post("p1", selftext=incoming)], conn=conn, updated_ids=updated)

    assert updated == []
    assert _stored(conn, "p1")["selftext"] == "[removed]"


def test_deleted_author_recovered_only_alongside_a_real_body(conn):
    insert_posts([_post("p1", author="[deleted]")], conn=conn)

    insert_posts([_post("p1", author="bob", selftext="body")], conn=conn)
    assert _stored(conn, "p1")["author"] == "bob"


def test_real_author_is_not_clobbered_by_an_incoming_deleted(conn):
    insert_posts([_post("p1", author="alice")], conn=conn)

    insert_posts([_post("p1", author="[deleted]", selftext="body")], conn=conn)
    row = _stored(conn, "p1")
    assert row["author"] == "alice"
    assert row["selftext"] == "body"  # the body repair still happened


def test_existing_real_post_is_neither_counted_nor_updated(conn):
    insert_posts([_post("p1", selftext="body one")], conn=conn)

    updated = []
    inserted = insert_posts([_post("p1", selftext="body two")], conn=conn,
                            updated_ids=updated)

    assert inserted == 0 and updated == []
    assert _stored(conn, "p1")["selftext"] == "body one"


def test_collected_date_and_source_survive_a_repair(conn):
    """Daily snapshot aggregates group on collected_date — it must not move."""
    insert_posts([_post("p1", collected_date="2026-08-20")], conn=conn)
    insert_posts([_post("p1", selftext="body", collected_date="2026-09-08")], conn=conn)
    assert _stored(conn, "p1")["collected_date"] == "2026-08-20"


# ── 2. retag_posts ──────────────────────────────────────────────────────────

def _tags(conn, pid, source=None):
    q = "SELECT category, matched_term, source FROM post_keyword_tags WHERE post_id = ?"
    params = [pid]
    if source:
        q += " AND source = ?"
        params.append(source)
    return {(r["category"], r["matched_term"], r["source"])
            for r in conn.execute(q, params).fetchall()}


def test_retag_replaces_stale_post_tags_and_keeps_comment_tags(conn):
    insert_posts([_post("p1", title="An update", selftext="my ai boyfriend is back")],
                 conn=conn)
    # A stale post-source tag (from the title-only version) + a comment-sourced
    # tag that must survive: it describes comment text, not the post body.
    conn.executemany(
        "INSERT INTO post_keyword_tags (post_id, subreddit, category, matched_term, post_date, source) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        [("p1", SUB, "romance", "ai husband", "2026-08-20", "post"),
         ("p1", SUB, "therapy", "ai therapist", "2026-08-20", "comment")],
    )

    stats = retag_posts(["p1"], conn=conn)

    assert stats["posts_retagged"] == 1
    assert ("romance", "ai husband", "post") not in _tags(conn, "p1")
    assert ("romance", "my ai boyfriend", "post") in _tags(conn, "p1")
    assert ("therapy", "ai therapist", "comment") in _tags(conn, "p1")


def test_retag_clears_the_already_scanned_marker(conn):
    """The taggers skip posts that have any source='post' row — clear that."""
    insert_posts([_post("p1", title="An update", selftext="nothing matching here")],
                 conn=conn)
    conn.execute(
        "INSERT INTO post_keyword_tags (post_id, subreddit, category, matched_term, post_date, source) "
        "VALUES ('p1', ?, 'romance', 'ai husband', '2026-08-20', 'post')", (SUB,),
    )
    conn.execute("INSERT INTO scanned_posts (post_id, scan_date) VALUES ('p1', '2026-08-20')")

    retag_posts(["p1"], conn=conn)

    assert _tags(conn, "p1", source="post") == set()
    assert conn.execute("SELECT COUNT(*) FROM scanned_posts").fetchone()[0] == 0


def test_retag_ignores_non_keyword_subreddits(conn):
    insert_posts([_post("p1", subreddit=OTHER_SUB, selftext="my ai boyfriend")], conn=conn)
    stats = retag_posts(["p1"], conn=conn)
    assert stats["posts_retagged"] == 0
    assert _tags(conn, "p1") == set()


def test_retag_accepts_injected_patterns(conn):
    insert_posts([_post("p1", selftext="widget talk")], conn=conn)
    patterns = build_patterns([{"name": "romance", "terms": ["widget"]}])
    retag_posts(["p1"], conn=conn, patterns=patterns)
    assert ("romance", "widget", "post") in _tags(conn, "p1")


# ── 3. refresh_shells ───────────────────────────────────────────────────────

def _seed_shell(conn, pid, created_utc, sub=SUB, title="An update",
                selftext="[removed]", author="alice"):
    insert_posts([_post(pid, subreddit=sub, title=title, selftext=selftext,
                        author=author, created_utc=created_utc)], conn=conn)


def _arctic(pid, **overrides):
    """Raw Arctic Shift shape (what fetch_posts_by_ids returns)."""
    base = {"id": pid, "subreddit": SUB.lower(), "title": "An update",
            "author": "alice", "created_utc": NOW, "score": 9, "num_comments": 3,
            "upvote_ratio": 0.9, "is_self": True, "selftext": "[removed]", "url": ""}
    base.update(overrides)
    return base


def test_select_shells_respects_window_and_subreddits(conn):
    _seed_shell(conn, "old", NOW - 40 * 86400)
    _seed_shell(conn, "inside", NOW - 20 * 86400)
    _seed_shell(conn, "young", NOW - 2 * 86400)
    _seed_shell(conn, "untracked", NOW - 20 * 86400, sub="SomeOtherSub")
    _seed_shell(conn, "has_body", NOW - 20 * 86400, selftext="a real body")
    _seed_shell(conn, "author_gone", NOW - 21 * 86400,
                selftext="a real body", author="[deleted]")

    rows = rsp.select_shells(conn, NOW - 35 * 86400, NOW - 10 * 86400, [SUB])

    # Oldest first; author='[deleted]' counts as a shell shape, a real body
    # with a real author does not.
    assert [r["id"] for r in rows] == ["author_gone", "inside"]


def test_refresh_recovers_body_retags_and_logs_rollback(conn, tmp_path, monkeypatch):
    _seed_shell(conn, "p1", NOW - 20 * 86400)
    _seed_shell(conn, "p2", NOW - 19 * 86400)
    conn.execute(
        "INSERT INTO post_keyword_tags (post_id, subreddit, category, matched_term, post_date, source) "
        "VALUES ('p1', ?, 'romance', 'ai husband', '2026-08-20', 'post')", (SUB,),
    )

    monkeypatch.setattr(rsp, "fetch_posts_by_ids", lambda ids: (
        [_arctic("p1", selftext="my ai boyfriend came back", score=9),
         _arctic("p2")],  # still queued/removed
        1, True,
    ))

    log = tmp_path / "rollback.jsonl"
    stats = rsp.refresh_shells(conn, NOW - 35 * 86400, NOW - 10 * 86400,
                               subreddits=[SUB], rollback_log=log)

    assert stats["selected"] == 2 and stats["fetched"] == 2
    assert stats["recovered"] == 1 and stats["still_shell"] == 1
    assert stats["by_subreddit"][SUB] == {"checked": 2, "recovered": 1}

    row = _stored(conn, "p1")
    assert row["selftext"] == "my ai boyfriend came back"
    assert row["subreddit"] == SUB  # canonical casing kept, not arctic's
    assert _stored(conn, "p2")["selftext"] == "[removed]"

    # Repaired post is re-tagged: stale tag gone, new one from the body present.
    assert ("romance", "ai husband", "post") not in _tags(conn, "p1")
    assert ("romance", "my ai boyfriend", "post") in _tags(conn, "p1")

    entries = [json.loads(l) for l in log.read_text().splitlines()]
    assert len(entries) == 1  # only changed rows are logged
    assert entries[0]["id"] == "p1"
    assert entries[0]["old"]["selftext"] == "[removed]"
    assert entries[0]["new"]["selftext"] == "my ai boyfriend came back"


def test_rollback_restores_values_and_tags(conn, tmp_path, monkeypatch):
    _seed_shell(conn, "p1", NOW - 20 * 86400)
    monkeypatch.setattr(rsp, "fetch_posts_by_ids", lambda ids: (
        [_arctic("p1", selftext="my ai boyfriend came back", score=9)], 1, True))

    log = tmp_path / "rollback.jsonl"
    rsp.refresh_shells(conn, NOW - 35 * 86400, NOW - 10 * 86400,
                       subreddits=[SUB], rollback_log=log)
    assert ("romance", "my ai boyfriend", "post") in _tags(conn, "p1")

    stats = rsp.rollback(conn, log)

    assert stats["restored"] == 1
    row = _stored(conn, "p1")
    assert row["selftext"] == "[removed]"
    assert row["score"] == 1 and row["num_comments"] == 0
    # Tags now match the restored (title-only) text again.
    assert _tags(conn, "p1", source="post") == set()


def test_dry_run_writes_nothing(conn, tmp_path, monkeypatch):
    _seed_shell(conn, "p1", NOW - 20 * 86400)
    monkeypatch.setattr(rsp, "fetch_posts_by_ids", lambda ids: (
        [_arctic("p1", selftext="my ai boyfriend came back")], 1, True))

    log = tmp_path / "rollback.jsonl"
    stats = rsp.refresh_shells(conn, NOW - 35 * 86400, NOW - 10 * 86400,
                               subreddits=[SUB], rollback_log=log, dry_run=True,
                               use_cursor=True)

    assert stats["recovered"] == 1  # reported...
    assert _stored(conn, "p1")["selftext"] == "[removed]"  # ...but not applied
    assert not log.exists()
    assert rsp._read_cursor(conn) is None


def test_request_cap_stops_early_and_cursor_resumes(conn, monkeypatch):
    # 250 shells one hour apart; nothing recovers, so a capped run without a
    # cursor would re-check the same oldest 100 forever.
    base = NOW - 30 * 86400
    for i in range(250):
        _seed_shell(conn, "p%03d" % i, base + i * 3600)

    seen = []

    def fake_fetch(ids):
        seen.append(list(ids))
        return [_arctic(i) for i in ids], 1, True

    monkeypatch.setattr(rsp, "fetch_posts_by_ids", fake_fetch)
    monkeypatch.setattr(rsp.time, "sleep", lambda s: None)

    first = rsp.refresh_shells(conn, NOW - 35 * 86400, NOW - 10 * 86400,
                               subreddits=[SUB], max_requests=1, use_cursor=True)
    assert first["capped"] is True
    assert first["requests"] == 1 and len(seen) == 1
    cursor = rsp._read_cursor(conn)
    assert cursor == base + 99 * 3600

    second = rsp.refresh_shells(conn, NOW - 35 * 86400, NOW - 10 * 86400,
                                subreddits=[SUB], max_requests=1, use_cursor=True)
    # Resumes at the cursor minus the re-check overlap, not from the start.
    assert second["selected"] == 250 - 51
    assert seen[1][0] == "p051"


def test_api_failure_is_reported(conn, monkeypatch):
    _seed_shell(conn, "p1", NOW - 20 * 86400)
    monkeypatch.setattr(rsp, "fetch_posts_by_ids", lambda ids: ([], 6, False))

    stats = rsp.refresh_shells(conn, NOW - 35 * 86400, NOW - 10 * 86400,
                               subreddits=[SUB])

    assert stats["api_failures"] == 1
    assert stats["recovered"] == 0
    assert _stored(conn, "p1")["selftext"] == "[removed]"


def test_fetch_by_ids_gives_up_on_persistent_throttling(monkeypatch):
    class _Resp:
        status_code = 429
        text = "Timeout. Maybe slow down a bit"

    monkeypatch.setattr(rsp.requests, "get", lambda *a, **k: _Resp())
    monkeypatch.setattr(rsp.time, "sleep", lambda s: None)

    posts, made, ok = rsp.fetch_posts_by_ids(["p1"])
    assert ok is False and posts == []
    assert made == rsp.MAX_RETRIES + 1  # bounded, not an infinite loop
