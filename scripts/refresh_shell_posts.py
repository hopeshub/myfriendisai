#!/usr/bin/env python3
"""Re-fetch archived "shell" posts and fill in bodies that arrived after collection.

Why this exists: since 2026-06-09 the collector runs arctic-first, pulling each
sub's posts from the Arctic Shift archive inside a 7-day window. Arctic captures
a post within hours of creation — frequently while it is still sitting in a
moderator queue, so its record has selftext='[removed]'. The archive record is
updated when the post is approved; ours never was, because inserts were
INSERT OR IGNORE and the first snapshot won forever. Result: ~30% of stored
posts since June 2026 are title-only shells, against a stable 16-20% in every
earlier year. Those rows sit in the per-1k denominator with almost no matchable
text, depressing every theme line ~12-16%, and they distort the community
volume charts.

Measured 2026-09-08 by re-fetching stored shells from the archive: r/KindroidAI
recovered 20/25, r/replika 13/25, r/CharacterAI 3/25, r/ChaiApp 0/25 (the last
being genuine removals — a shell that stays a shell is the honest answer, not a
failure).

The repair rule itself lives in src/db/operations.insert_posts (a stored shell
is upgraded only by real incoming text; a stored body is never downgraded), so
this script and the daily collector cannot drift apart. Repaired posts are
re-tagged via retag_posts so their recovered bodies reach the theme counts.

Idempotent: a post that comes back still-shell is simply left alone, and
re-running over the same window is safe.

Usage:
    python scripts/refresh_shell_posts.py --dry-run
    python scripts/refresh_shell_posts.py --since 2026-03-11 --until 2026-05-27
    python scripts/refresh_shell_posts.py --subreddit replika
    python scripts/refresh_shell_posts.py --rollback logs/shell_refresh_2026-09-08.jsonl
"""

import argparse
import json
import logging
import sqlite3
import sys
import time
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import load_communities, load_keywords
from src.db.schema import initialize as init_db
from src.db.operations import SHELL_BODIES, insert_posts, retag_posts
from src.keyword_matching import build_patterns
from scripts.backfill_arctic import (
    RETRYABLE_STATUS, THROTTLE_EVENTS, USER_AGENT, parse_arctic_post,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

PROJECT_DIR = Path(__file__).parent.parent

# Arctic Shift's bulk-by-id endpoint: comma-separated fullnames (t3_xxxxx),
# max 100 per request, same response envelope as the search endpoint.
IDS_API_BASE = "https://arctic-shift.photon-reddit.com/api/posts/ids"
BATCH_SIZE = 100
REQUEST_DELAY = 2.0  # seconds between requests — matches backfill_arctic
MAX_RETRIES = 5

# Default age window. A post younger than 10 days may still be queued (nothing
# to recover yet); past 35 days approvals have effectively stopped and the
# requests are wasted.
DEFAULT_MIN_AGE_DAYS = 10
DEFAULT_MAX_AGE_DAYS = 35

# Resume marker for capped runs (--use-cursor, used by the daily pipeline).
# Without it a capped run re-checks the same oldest shells every day and never
# reaches the newest, because most shells are genuine removals that never
# recover and only age out of the window. The cursor is re-read with a small
# overlap so a post approved a day or two after its first check is still caught.
CURSOR_KEY = "shell_refresh_cursor"
CURSOR_OVERLAP_DAYS = 2


# ── Selection ───────────────────────────────────────────────────────────────

def _tracked_subreddits() -> list:
    """Every active tracked sub, all tiers — the volume charts use them all."""
    return [c["subreddit"] for c in load_communities()]


def select_shells(conn: sqlite3.Connection, since_epoch: int, until_epoch: int,
                  subreddits: list) -> list:
    """Shell rows in the window, oldest first.

    author='[deleted]' rows are included because they are the other shape of an
    incomplete row; note that only a shell *body* can actually be repaired (see
    insert_posts), and a deleted account is rarely recoverable — they mostly
    come back unchanged.
    """
    placeholders = ",".join("?" * len(subreddits))
    shell_ph = ",".join("?" * len(SHELL_BODIES))
    return conn.execute(
        f"""
        SELECT id, subreddit, selftext, author, score, num_comments, upvote_ratio,
               created_utc
        FROM posts
        WHERE (selftext IN ({shell_ph}) OR author = '[deleted]')
          AND created_utc IS NOT NULL
          AND created_utc >= ? AND created_utc < ?
          AND subreddit IN ({placeholders})
        ORDER BY created_utc ASC
        """,
        (*SHELL_BODIES, since_epoch, until_epoch, *subreddits),
    ).fetchall()


def _read_cursor(conn: sqlite3.Connection):
    row = conn.execute(
        "SELECT value FROM pipeline_meta WHERE key = ?", (CURSOR_KEY,)
    ).fetchone()
    try:
        return int(row[0]) if row else None
    except (TypeError, ValueError):
        return None


def _write_cursor(conn: sqlite3.Connection, epoch: int) -> None:
    """Advance the cursor monotonically (never rewind on a partial run)."""
    current = _read_cursor(conn) or 0
    conn.execute(
        "INSERT INTO pipeline_meta (key, value, updated_at) "
        "VALUES (?, ?, CURRENT_TIMESTAMP) "
        "ON CONFLICT(key) DO UPDATE SET value = excluded.value, "
        "updated_at = CURRENT_TIMESTAMP",
        (CURSOR_KEY, str(max(current, epoch))),
    )
    conn.commit()


# ── Fetch ───────────────────────────────────────────────────────────────────

def fetch_posts_by_ids(ids: list) -> "tuple[list, int, bool]":
    """Fetch up to BATCH_SIZE posts by id. Returns (posts, requests_made, ok).

    Same backoff style as backfill_arctic._fetch_window: transient overload
    (422 "slow down a bit", 429, 5xx) is retried with an increasing wait, and
    persistent failure gives up cleanly rather than looping. Throttle events are
    counted into backfill_arctic's shared counters so the run's published
    arctic_throttle_events telemetry covers this path too.
    """
    params = {"ids": ",".join("t3_" + i for i in ids)}
    requests_made = 0
    retries = 0
    while True:
        requests_made += 1
        try:
            resp = requests.get(
                IDS_API_BASE, params=params,
                headers={"User-Agent": USER_AGENT}, timeout=30,
            )
        except requests.RequestException as e:
            retries += 1
            THROTTLE_EVENTS["network_error"] += 1
            if retries > MAX_RETRIES:
                logger.error("  gave up after %d network errors: %s", MAX_RETRIES, e)
                return [], requests_made, False
            logger.warning("  network error (retry %d): %s", retries, e)
            time.sleep(5 * retries)
            continue

        if resp.status_code in RETRYABLE_STATUS:
            retries += 1
            THROTTLE_EVENTS["retryable_status"] += 1
            detail = resp.text[:120].replace("\n", " ")
            if retries > MAX_RETRIES:
                logger.error("  HTTP %d after %d retries — giving up (%s)",
                             resp.status_code, MAX_RETRIES, detail)
                return [], requests_made, False
            wait = 60 if resp.status_code == 429 else min(15 * retries, 90)
            logger.warning("  HTTP %d — backing off %ds (retry %d/%d): %s",
                           resp.status_code, wait, retries, MAX_RETRIES, detail)
            time.sleep(wait)
            continue

        if resp.status_code != 200:
            logger.error("  HTTP %d from %s — giving up", resp.status_code, IDS_API_BASE)
            return [], requests_made, False

        return (resp.json().get("data") or []), requests_made, True


# ── Refresh ─────────────────────────────────────────────────────────────────

def _old_values(row) -> dict:
    return {
        "selftext": row["selftext"], "author": row["author"],
        "score": row["score"], "num_comments": row["num_comments"],
        "upvote_ratio": row["upvote_ratio"],
    }


def refresh_shells(conn: sqlite3.Connection, since_epoch: int, until_epoch: int,
                   subreddits=None, max_requests: int = 0,
                   rollback_log=None, dry_run: bool = False,
                   use_cursor: bool = False) -> dict:
    """Re-fetch shells in a created_utc window and repair the ones that recovered.

    max_requests=0 means unbounded. use_cursor resumes a capped run where the
    last one stopped (see CURSOR_KEY) — the daily pipeline uses it; a manual
    repair of a specific window should not.
    """
    subreddits = subreddits or _tracked_subreddits()

    effective_since = since_epoch
    if use_cursor:
        cursor = _read_cursor(conn)
        if cursor:
            effective_since = max(
                since_epoch, cursor - CURSOR_OVERLAP_DAYS * 86400
            )
            logger.info("Resuming from cursor %s (-%dd overlap)",
                        _fmt(cursor), CURSOR_OVERLAP_DAYS)

    rows = select_shells(conn, effective_since, until_epoch, subreddits)
    logger.info("%d shell posts in window %s .. %s across %d subreddit(s)",
                len(rows), _fmt(effective_since), _fmt(until_epoch), len(subreddits))

    stats = {
        "selected": len(rows), "fetched": 0, "recovered": 0, "still_shell": 0,
        "requests": 0, "batches": 0, "api_failures": 0, "capped": False,
        "by_subreddit": {}, "rollback_log": None,
    }
    if not rows:
        return stats

    n_batches = (len(rows) + BATCH_SIZE - 1) // BATCH_SIZE
    logger.info("Would issue up to %d request(s) of %d ids%s",
                n_batches, BATCH_SIZE,
                " (capped at %d)" % max_requests if max_requests else "")

    by_id = {r["id"]: r for r in rows}
    log_fh = None
    last_processed_utc = None
    patterns = None  # built once on the first repair, reused across batches
    try:
        for start in range(0, len(rows), BATCH_SIZE):
            if max_requests and stats["requests"] >= max_requests:
                stats["capped"] = True
                logger.info("Request cap (%d) reached — stopping; the rest is "
                            "picked up next run", max_requests)
                break
            batch = rows[start:start + BATCH_SIZE]
            if stats["batches"]:
                time.sleep(REQUEST_DELAY)
            fetched, made, ok = fetch_posts_by_ids([r["id"] for r in batch])
            stats["requests"] += made
            stats["batches"] += 1
            if not ok:
                stats["api_failures"] += 1
                logger.error("  batch %d failed — aborting run", stats["batches"])
                break
            stats["fetched"] += len(fetched)
            last_processed_utc = batch[-1]["created_utc"]

            parsed = []
            for p in fetched:
                stored = by_id.get(p.get("id"))
                if stored is None:
                    continue  # not something we asked for
                row = parse_arctic_post(p)
                # Force our canonical casing — Arctic Shift returns e.g.
                # "antiai", which case-sensitive IN(...) filters would drop.
                row["subreddit"] = stored["subreddit"]
                parsed.append(row)

            would_update = [
                r for r in parsed
                if by_id[r["id"]]["selftext"] in SHELL_BODIES
                and r["selftext"] and r["selftext"] not in SHELL_BODIES
            ]
            stats["still_shell"] += len(parsed) - len(would_update)
            for r in parsed:
                sub_stats = stats["by_subreddit"].setdefault(
                    r["subreddit"], {"checked": 0, "recovered": 0})
                sub_stats["checked"] += 1

            if dry_run:
                stats["recovered"] += len(would_update)
                for r in would_update:
                    stats["by_subreddit"][r["subreddit"]]["recovered"] += 1
                continue

            updated_ids = []
            insert_posts(parsed, conn=conn, updated_ids=updated_ids)
            if not updated_ids:
                continue

            # Rollback log first: written before the tags change, so a restore
            # always has the pre-refresh values even if tagging dies mid-way.
            if rollback_log is not None:
                if log_fh is None:
                    Path(rollback_log).parent.mkdir(parents=True, exist_ok=True)
                    log_fh = open(rollback_log, "a")
                    stats["rollback_log"] = str(rollback_log)
                now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
                new_by_id = {r["id"]: r for r in parsed}
                for pid in updated_ids:
                    log_fh.write(json.dumps({
                        "refreshed_at": now,
                        "id": pid,
                        "subreddit": by_id[pid]["subreddit"],
                        "old": _old_values(by_id[pid]),
                        "new": _old_values(new_by_id[pid]),
                    }) + "\n")
                log_fh.flush()

            if patterns is None:
                patterns = build_patterns(load_keywords())
            tag_stats = retag_posts(updated_ids, conn=conn, patterns=patterns)
            stats["recovered"] += len(updated_ids)
            for pid in updated_ids:
                stats["by_subreddit"][by_id[pid]["subreddit"]]["recovered"] += 1
            logger.info("  batch %d: %d fetched, %d repaired (%d tags added)",
                        stats["batches"], len(fetched), len(updated_ids),
                        tag_stats["tags_added"])
    finally:
        if log_fh is not None:
            log_fh.close()

    if use_cursor and not dry_run and last_processed_utc:
        _write_cursor(conn, last_processed_utc)
        stats["cursor"] = last_processed_utc

    return stats


def rollback(conn: sqlite3.Connection, path: Path) -> dict:
    """Restore pre-refresh values from a rollback log and re-tag those posts.

    Re-tagging against the restored (shell) text is what removes the tags the
    recovered body produced — retag_posts deletes the post-source rows and
    rebuilds them from whatever the post now says.
    """
    entries = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                entries.append(json.loads(line))
    logger.info("Rolling back %d row(s) from %s", len(entries), path)

    restored = 0
    for e in entries:
        old = e["old"]
        result = conn.execute(
            "UPDATE posts SET selftext = ?, author = ?, score = ?, "
            "num_comments = ?, upvote_ratio = ? WHERE id = ?",
            (old["selftext"], old["author"], old["score"],
             old["num_comments"], old.get("upvote_ratio"), e["id"]),
        )
        restored += result.rowcount
    conn.commit()

    tag_stats = retag_posts([e["id"] for e in entries], conn=conn)
    logger.info("Restored %d row(s); re-tagged %d (%d tag rows deleted, %d added)",
                restored, tag_stats["posts_retagged"],
                tag_stats["tags_deleted"], tag_stats["tags_added"])
    return {"restored": restored, **tag_stats}


# ── CLI ─────────────────────────────────────────────────────────────────────

def _fmt(epoch: int) -> str:
    return datetime.fromtimestamp(epoch, tz=timezone.utc).strftime("%Y-%m-%d")


def _epoch(day: date) -> int:
    return int(datetime.combine(
        day, datetime.min.time(), tzinfo=timezone.utc).timestamp())


def print_summary(stats: dict, dry_run: bool) -> None:
    logger.info("=" * 60)
    logger.info("SHELL REFRESH %s", "(DRY RUN — nothing written)" if dry_run else "COMPLETE")
    logger.info("  Shells selected: %d", stats["selected"])
    logger.info("  Fetched:         %d in %d request(s)", stats["fetched"], stats["requests"])
    logger.info("  Recovered:       %d", stats["recovered"])
    logger.info("  Still shells:    %d", stats["still_shell"])
    if stats["capped"]:
        logger.info("  Stopped early:   request cap reached (backlog resumes next run)")
    if stats["api_failures"]:
        logger.error("  API failures:    %d", stats["api_failures"])
    if stats.get("rollback_log"):
        logger.info("  Rollback log:    %s", stats["rollback_log"])
    for sub, s in sorted(stats["by_subreddit"].items(),
                         key=lambda kv: kv[1]["recovered"], reverse=True):
        if s["checked"]:
            logger.info("    r/%-25s checked=%4d  recovered=%4d", sub, s["checked"], s["recovered"])
    logger.info("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="Re-fetch shell posts from Arctic Shift and fill in recovered bodies")
    parser.add_argument("--since", help="Earliest post created_utc date, YYYY-MM-DD "
                                        "(default: %d days ago)" % DEFAULT_MAX_AGE_DAYS)
    parser.add_argument("--until", help="Latest post created_utc date, YYYY-MM-DD "
                                        "(default: %d days ago)" % DEFAULT_MIN_AGE_DAYS)
    parser.add_argument("--subreddit", help="Only this subreddit")
    parser.add_argument("--max-requests", type=int, default=0,
                        help="Stop after N API requests (0 = unbounded)")
    parser.add_argument("--use-cursor", action="store_true",
                        help="Resume a capped run where the last one stopped "
                             "(the daily pipeline uses this; manual repairs should not)")
    parser.add_argument("--rollback-log", help="Path for the JSONL rollback log "
                                               "(default: logs/shell_refresh_<date>.jsonl)")
    parser.add_argument("--rollback", help="Restore old values from a rollback log and exit")
    parser.add_argument("--dry-run", action="store_true",
                        help="Fetch and report what would change, write nothing")
    parser.add_argument("--db", help="Database path (default: the project database)")
    args = parser.parse_args()

    conn = init_db(Path(args.db)) if args.db else init_db()
    try:
        if args.rollback:
            rollback(conn, Path(args.rollback))
            return 0

        today = date.today()
        since_epoch = (_epoch(datetime.strptime(args.since, "%Y-%m-%d").date())
                       if args.since else _epoch(today - timedelta(days=DEFAULT_MAX_AGE_DAYS)))
        until_epoch = (_epoch(datetime.strptime(args.until, "%Y-%m-%d").date())
                       if args.until else _epoch(today - timedelta(days=DEFAULT_MIN_AGE_DAYS)))
        if since_epoch >= until_epoch:
            logger.error("--since must be before --until")
            return 2

        subreddits = [args.subreddit] if args.subreddit else _tracked_subreddits()
        rollback_log = None
        if not args.dry_run:
            rollback_log = Path(args.rollback_log) if args.rollback_log else (
                PROJECT_DIR / "logs" / ("shell_refresh_%s.jsonl" % today.isoformat()))

        stats = refresh_shells(
            conn, since_epoch, until_epoch, subreddits=subreddits,
            max_requests=args.max_requests, rollback_log=rollback_log,
            dry_run=args.dry_run, use_cursor=args.use_cursor,
        )
        print_summary(stats, args.dry_run)
        return 1 if stats["api_failures"] else 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
