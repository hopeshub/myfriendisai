#!/usr/bin/env python3
"""Quick status report on data collection health.

Usage:
    python scripts/collection_status.py
"""

import sqlite3
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

DB_PATH = Path(__file__).parent.parent / "data" / "tracker.db"


def main():
    if not DB_PATH.exists():
        print("ERROR: Database not found at", DB_PATH)
        return 1

    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row

    today = date.today()

    # Last 7 days of snapshots
    print("=== Daily Collection Summary (last 7 days) ===")
    rows = conn.execute(
        """
        SELECT snapshot_date,
               COUNT(*) as subs_tracked,
               SUM(COALESCE(subscribers, 0)) as total_subscribers,
               SUM(COALESCE(posts_today, 0)) as total_posts,
               COUNT(CASE WHEN subscribers IS NOT NULL AND subscribers > 0 THEN 1 END) as subs_with_data
        FROM subreddit_snapshots s
        INNER JOIN subreddit_config c ON c.subreddit = s.subreddit AND c.is_active = 1
        WHERE snapshot_date >= ?
        GROUP BY snapshot_date
        ORDER BY snapshot_date DESC
        """,
        ((today - timedelta(days=7)).isoformat(),),
    ).fetchall()

    if not rows:
        print("  No snapshots in the last 7 days!")
    for r in rows:
        status = "OK" if r["subs_with_data"] == r["subs_tracked"] else f"PARTIAL ({r['subs_with_data']}/{r['subs_tracked']} have subscriber data)"
        print(f"  {r['snapshot_date']}  tracked={r['subs_tracked']}  posts={r['total_posts']}  subs={r['total_subscribers']:,}  [{status}]")

    # Check if today's collection ran
    today_row = conn.execute(
        "SELECT COUNT(*) as c FROM subreddit_snapshots WHERE snapshot_date = ?",
        (today.isoformat(),),
    ).fetchone()
    print()
    if today_row["c"] > 0:
        print(f"Today ({today}): COLLECTED ({today_row['c']} snapshots)")
    else:
        print(f"Today ({today}): NOT YET COLLECTED")

    # New posts in last 7 days
    print()
    print("=== New Posts (last 7 days) ===")
    rows = conn.execute(
        """
        SELECT collected_date, COUNT(*) as posts
        FROM posts
        WHERE collected_date >= ?
        GROUP BY collected_date
        ORDER BY collected_date DESC
        """,
        ((today - timedelta(days=7)).isoformat(),),
    ).fetchall()
    total_posts = 0
    for r in rows:
        print(f"  {r['collected_date']}  {r['posts']} posts")
        total_posts += r["posts"]
    print(f"  Total: {total_posts} posts")

    # Keyword tagging status
    print()
    print("=== Keyword Tagging ===")
    kw_row = conn.execute(
        """
        SELECT COUNT(DISTINCT post_id) as tagged, MAX(post_date) as last_date
        FROM post_keyword_tags
        """
    ).fetchone()
    print(f"  Total tagged posts: {kw_row['tagged']:,}")
    print(f"  Last tagged date: {kw_row['last_date']}")

    # Overall DB stats
    print()
    print("=== Database Totals ===")
    snap = conn.execute("SELECT COUNT(*) as c FROM subreddit_snapshots").fetchone()
    post = conn.execute("SELECT COUNT(*) as c FROM posts").fetchone()
    active = conn.execute("SELECT COUNT(*) as c FROM subreddit_config WHERE is_active = 1").fetchone()
    print(f"  Active subreddits: {active['c']}")
    print(f"  Total snapshots: {snap['c']:,}")
    print(f"  Total posts: {post['c']:,}")

    # Check log file for errors
    log_path = Path(__file__).parent.parent / "logs" / "collect_daily.log"
    if log_path.exists():
        log_text = log_path.read_text()
        if "Traceback" in log_text or "Error" in log_text.split("\n")[-5:]:
            print()
            print("=== WARNING: Errors in last collection log ===")
            lines = log_text.strip().split("\n")
            # Print last 10 lines for context
            for line in lines[-10:]:
                print(f"  {line}")

    conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
