#!/usr/bin/env python3
"""Backfill unique_post_authors_7d, unique_comment_authors_7d, and
unique_contributors_7d on every existing subreddit_snapshots row.

For each snapshot_date, counts distinct authors whose post / comment
fell in the 7-day window ending on that date (inclusive). Deleted /
null authors are excluded.

Comment metrics are NULL for snapshots whose 7d window ends before the
earliest comment created_utc in the DB — that data simply doesn't exist
for those dates (comment collection started 2026-03-18, forward-looking).
For those rows, unique_contributors_7d falls back to unique_post_authors_7d.

Idempotent: re-running overwrites all three columns with freshly-computed
values.

Usage:
    python scripts/backfill_contributors.py
"""

import bisect
import logging
import sqlite3
import sys
import time
from datetime import date, datetime, time as dtime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

DB_PATH = Path(__file__).parent.parent / "data" / "tracker.db"

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger(__name__)


def _window_bounds(snap_date: date) -> tuple[int, int]:
    """Return [start, end) unix timestamps for the 7d window ending on snap_date."""
    start_dt = datetime.combine(snap_date - timedelta(days=6), dtime.min, tzinfo=timezone.utc)
    end_dt = datetime.combine(snap_date + timedelta(days=1), dtime.min, tzinfo=timezone.utc)
    return int(start_dt.timestamp()), int(end_dt.timestamp())


def backfill(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()

    min_comment_utc_row = cur.execute("SELECT MIN(created_utc) FROM comments").fetchone()
    min_comment_utc = min_comment_utc_row[0] if min_comment_utc_row and min_comment_utc_row[0] else None
    if min_comment_utc is None:
        log.info("No comments in DB — comment_authors_7d will be NULL for every snapshot")
    else:
        log.info("Earliest comment created_utc: %s (%s)", min_comment_utc,
                 datetime.fromtimestamp(min_comment_utc, tz=timezone.utc).date().isoformat())

    subs = [r[0] for r in cur.execute("SELECT DISTINCT subreddit FROM subreddit_snapshots ORDER BY subreddit").fetchall()]
    log.info("Processing %d subreddits", len(subs))

    total_updated = 0
    t_start = time.time()

    for sub in subs:
        # Load all post (created_utc, author) pairs, filtered + sorted by time.
        posts = cur.execute(
            "SELECT created_utc, author FROM posts "
            "WHERE subreddit = ? AND created_utc IS NOT NULL "
            "AND author IS NOT NULL AND author != '' AND author != '[deleted]' "
            "ORDER BY created_utc",
            (sub,),
        ).fetchall()
        post_ts = [r[0] for r in posts]
        post_authors = [r[1] for r in posts]

        comments = cur.execute(
            "SELECT created_utc, author FROM comments "
            "WHERE subreddit = ? AND created_utc IS NOT NULL "
            "AND author IS NOT NULL AND author != '' AND author != '[deleted]' "
            "ORDER BY created_utc",
            (sub,),
        ).fetchall()
        com_ts = [r[0] for r in comments]
        com_authors = [r[1] for r in comments]

        snapshots = cur.execute(
            "SELECT id, snapshot_date FROM subreddit_snapshots WHERE subreddit = ? ORDER BY snapshot_date",
            (sub,),
        ).fetchall()

        updates = []
        for snap_id, snap_date_str in snapshots:
            snap_date = date.fromisoformat(snap_date_str)
            win_start, win_end = _window_bounds(snap_date)

            pi0 = bisect.bisect_left(post_ts, win_start)
            pi1 = bisect.bisect_left(post_ts, win_end)
            post_set = set(post_authors[pi0:pi1])
            post_count = len(post_set)

            have_comments = min_comment_utc is not None and win_end > min_comment_utc
            if have_comments:
                ci0 = bisect.bisect_left(com_ts, win_start)
                ci1 = bisect.bisect_left(com_ts, win_end)
                com_set = set(com_authors[ci0:ci1])
                com_count = len(com_set)
                contributor_count = len(post_set | com_set)
            else:
                com_count = None
                contributor_count = post_count

            updates.append((post_count, com_count, contributor_count, snap_id))

        cur.executemany(
            "UPDATE subreddit_snapshots "
            "SET unique_post_authors_7d = ?, "
            "    unique_comment_authors_7d = ?, "
            "    unique_contributors_7d = ? "
            "WHERE id = ?",
            updates,
        )
        conn.commit()
        total_updated += len(updates)
        log.info("  r/%s: %d snapshots updated (%d posts, %d comments in source)",
                 sub, len(updates), len(posts), len(comments))

    dur = time.time() - t_start
    log.info("Backfill complete: %d snapshot rows updated in %.1fs", total_updated, dur)


def main():
    if not DB_PATH.exists():
        log.error("Database not found at %s", DB_PATH)
        return 1

    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA journal_mode=WAL")
    try:
        backfill(conn)
        return 0
    except Exception as e:
        conn.rollback()
        log.error("Backfill failed: %s", e, exc_info=True)
        return 1
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
