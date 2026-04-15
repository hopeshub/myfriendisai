"""Insert and query helpers for the SQLite database."""

import json
import sqlite3
from datetime import date
from pathlib import Path
from typing import Optional

from src.db.schema import get_connection

DATA_DIR = Path(__file__).parent.parent.parent / "data"


def sync_subreddit_config(communities: list[dict], conn: Optional[sqlite3.Connection] = None) -> None:
    """Upsert subreddit_config rows from the loaded communities list.

    Also deactivates any subreddits in the DB that are no longer in the config.
    """
    _conn = conn or get_connection()
    today = date.today().isoformat()
    active_subs = set()
    try:
        for c in communities:
            active_subs.add(c["subreddit"])
            _conn.execute(
                """
                INSERT INTO subreddit_config (subreddit, category, tier, display_name, description, added_date, is_active)
                VALUES (:subreddit, :category, :tier, :display_name, :description, :added_date, :is_active)
                ON CONFLICT(subreddit) DO UPDATE SET
                    category=excluded.category,
                    tier=excluded.tier,
                    display_name=excluded.display_name,
                    description=excluded.description,
                    is_active=excluded.is_active
                """,
                {
                    "subreddit": c["subreddit"],
                    "category": c.get("category"),
                    "tier": c.get("tier"),
                    "display_name": c.get("display_name"),
                    "description": c.get("notes"),
                    "added_date": today,
                    "is_active": int(c.get("is_active", True)),
                },
            )
        # Deactivate subreddits no longer in the config
        if active_subs:
            placeholders = ",".join("?" * len(active_subs))
            _conn.execute(
                f"UPDATE subreddit_config SET is_active = 0 WHERE subreddit NOT IN ({placeholders}) AND is_active = 1",
                list(active_subs),
            )
        _conn.commit()
    finally:
        if conn is None:
            _conn.close()


def insert_snapshot(
    subreddit: str,
    snapshot_date: date,
    metrics: dict,
    raw_about_json: Optional[str] = None,
    raw_listing_json: Optional[str] = None,
    data_source: str = "json_endpoint",
    conn: Optional[sqlite3.Connection] = None,
) -> None:
    """Insert or replace a subreddit snapshot row."""
    _conn = conn or get_connection()
    try:
        _conn.execute(
            """
            INSERT INTO subreddit_snapshots
                (subreddit, snapshot_date, data_source, subscribers, active_users,
                 visitors_7d, contributions_7d, posts_today, avg_comments_per_post,
                 avg_score_per_post, unique_authors, raw_about_json, raw_listing_json)
            VALUES
                (:subreddit, :snapshot_date, :data_source, :subscribers, :active_users,
                 :visitors_7d, :contributions_7d, :posts_today, :avg_comments_per_post,
                 :avg_score_per_post, :unique_authors, :raw_about_json, :raw_listing_json)
            ON CONFLICT(subreddit, snapshot_date) DO UPDATE SET
                subscribers=excluded.subscribers,
                active_users=excluded.active_users,
                visitors_7d=excluded.visitors_7d,
                contributions_7d=excluded.contributions_7d,
                posts_today=excluded.posts_today,
                avg_comments_per_post=excluded.avg_comments_per_post,
                avg_score_per_post=excluded.avg_score_per_post,
                unique_authors=excluded.unique_authors,
                raw_about_json=excluded.raw_about_json,
                raw_listing_json=excluded.raw_listing_json
            """,
            {
                "subreddit": subreddit,
                "snapshot_date": snapshot_date.isoformat(),
                "data_source": data_source,
                "subscribers": metrics.get("subscribers"),
                "active_users": metrics.get("active_users"),
                "visitors_7d": metrics.get("visitors_7d"),
                "contributions_7d": metrics.get("contributions_7d"),
                "posts_today": metrics.get("posts_today"),
                "avg_comments_per_post": metrics.get("avg_comments_per_post"),
                "avg_score_per_post": metrics.get("avg_score_per_post"),
                "unique_authors": metrics.get("unique_authors"),
                "raw_about_json": raw_about_json,
                "raw_listing_json": raw_listing_json,
            },
        )
        _conn.commit()
    finally:
        if conn is None:
            _conn.close()


def insert_posts(posts: list[dict], conn: Optional[sqlite3.Connection] = None) -> int:
    """Insert posts, skipping duplicates. Returns count of new rows inserted."""
    _conn = conn or get_connection()
    inserted = 0
    try:
        for p in posts:
            result = _conn.execute(
                """
                INSERT OR IGNORE INTO posts
                    (id, subreddit, title, author, created_utc, score, num_comments,
                     upvote_ratio, is_self, selftext, url, collected_date, data_source, raw_json)
                VALUES
                    (:id, :subreddit, :title, :author, :created_utc, :score, :num_comments,
                     :upvote_ratio, :is_self, :selftext, :url, :collected_date, :data_source, :raw_json)
                """,
                p,
            )
            inserted += result.rowcount
        _conn.commit()
    finally:
        if conn is None:
            _conn.close()
    return inserted


def get_snapshots(
    subreddit: str,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    conn: Optional[sqlite3.Connection] = None,
) -> list[dict]:
    """Return snapshot rows for a subreddit, optionally filtered by date range."""
    _conn = conn or get_connection()
    try:
        query = "SELECT * FROM subreddit_snapshots WHERE subreddit = ?"
        params: list = [subreddit]
        if start_date:
            query += " AND snapshot_date >= ?"
            params.append(start_date.isoformat())
        if end_date:
            query += " AND snapshot_date <= ?"
            params.append(end_date.isoformat())
        query += " ORDER BY snapshot_date ASC"
        rows = _conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]
    finally:
        if conn is None:
            _conn.close()


def get_all_snapshots_for_chart(conn: Optional[sqlite3.Connection] = None) -> list[dict]:
    """Return snapshots for active subreddits, ordered by subreddit + date. Excludes raw JSON blobs."""
    _conn = conn or get_connection()
    try:
        rows = _conn.execute(
            """
            SELECT s.subreddit, s.snapshot_date, s.subscribers, s.active_users,
                   s.posts_today, s.avg_comments_per_post,
                   s.avg_score_per_post, s.unique_authors,
                   s.unique_post_authors_7d, s.unique_comment_authors_7d,
                   s.unique_contributors_7d
            FROM subreddit_snapshots s
            INNER JOIN subreddit_config c ON c.subreddit = s.subreddit AND c.is_active = 1
            ORDER BY s.subreddit ASC, s.snapshot_date ASC
            """
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        if conn is None:
            _conn.close()


def update_contributor_metrics_for_date(
    snapshot_date: date,
    conn: Optional[sqlite3.Connection] = None,
) -> int:
    """Recompute rolling-7d contributor metrics for every snapshot row on a given date.

    Counts distinct post authors and comment authors within the 7-day window
    ending on `snapshot_date` (inclusive). Both counts and their union are
    written to the snapshot row. Deleted / null authors are excluded.

    Returns the number of rows updated.
    """
    from datetime import datetime, time as dtime, timedelta, timezone

    _conn = conn or get_connection()
    try:
        win_start = int(datetime.combine(
            snapshot_date - timedelta(days=6), dtime.min, tzinfo=timezone.utc
        ).timestamp())
        win_end = int(datetime.combine(
            snapshot_date + timedelta(days=1), dtime.min, tzinfo=timezone.utc
        ).timestamp())

        # Does our comments table cover this window at all?
        min_comment_utc_row = _conn.execute("SELECT MIN(created_utc) FROM comments").fetchone()
        min_comment_utc = min_comment_utc_row[0] if min_comment_utc_row else None
        have_comments = min_comment_utc is not None and win_end > min_comment_utc

        # Pull distinct post-authors per sub in the window
        post_rows = _conn.execute(
            """
            SELECT subreddit, COUNT(DISTINCT author) AS n
            FROM posts
            WHERE created_utc >= ? AND created_utc < ?
              AND author IS NOT NULL AND author != '' AND author != '[deleted]'
            GROUP BY subreddit
            """,
            (win_start, win_end),
        ).fetchall()
        post_by_sub = {r["subreddit"]: r["n"] for r in post_rows}

        # Same for comments
        com_by_sub: dict = {}
        contrib_by_sub: dict = {}
        if have_comments:
            com_rows = _conn.execute(
                """
                SELECT subreddit, COUNT(DISTINCT author) AS n
                FROM comments
                WHERE created_utc >= ? AND created_utc < ?
                  AND author IS NOT NULL AND author != '' AND author != '[deleted]'
                GROUP BY subreddit
                """,
                (win_start, win_end),
            ).fetchall()
            com_by_sub = {r["subreddit"]: r["n"] for r in com_rows}

            # Union count (distinct post+comment authors) — needs a UNION query
            union_rows = _conn.execute(
                """
                SELECT subreddit, COUNT(DISTINCT author) AS n FROM (
                    SELECT subreddit, author FROM posts
                    WHERE created_utc >= ? AND created_utc < ?
                      AND author IS NOT NULL AND author != '' AND author != '[deleted]'
                    UNION
                    SELECT subreddit, author FROM comments
                    WHERE created_utc >= ? AND created_utc < ?
                      AND author IS NOT NULL AND author != '' AND author != '[deleted]'
                )
                GROUP BY subreddit
                """,
                (win_start, win_end, win_start, win_end),
            ).fetchall()
            contrib_by_sub = {r["subreddit"]: r["n"] for r in union_rows}

        # Collect the subreddits that have a snapshot row on this date
        snap_rows = _conn.execute(
            "SELECT id, subreddit FROM subreddit_snapshots WHERE snapshot_date = ?",
            (snapshot_date.isoformat(),),
        ).fetchall()

        updates = []
        for row in snap_rows:
            sub = row["subreddit"]
            pc = post_by_sub.get(sub, 0)
            if have_comments:
                cc = com_by_sub.get(sub, 0)
                tot = contrib_by_sub.get(sub, pc)  # fallback: if no union row, use post count
            else:
                cc = None
                tot = pc
            updates.append((pc, cc, tot, row["id"]))

        _conn.executemany(
            "UPDATE subreddit_snapshots "
            "SET unique_post_authors_7d = ?, "
            "    unique_comment_authors_7d = ?, "
            "    unique_contributors_7d = ? "
            "WHERE id = ?",
            updates,
        )
        _conn.commit()
        return len(updates)
    finally:
        if conn is None:
            _conn.close()


def aggregate_posts_to_snapshots(conn: Optional[sqlite3.Connection] = None) -> int:
    """Compute daily aggregates from the posts table and upsert into subreddit_snapshots.

    Uses INSERT OR IGNORE so real json_endpoint snapshots are never overwritten.
    Returns the number of new rows inserted.
    """
    _conn = conn or get_connection()
    try:
        result = _conn.execute(
            """
            INSERT OR IGNORE INTO subreddit_snapshots
                (subreddit, snapshot_date, data_source,
                 posts_today, avg_comments_per_post, avg_score_per_post, unique_authors)
            SELECT
                subreddit,
                collected_date                                                  AS snapshot_date,
                'arctic_shift'                                                  AS data_source,
                COUNT(*)                                                        AS posts_today,
                ROUND(AVG(CASE WHEN num_comments >= 0 THEN num_comments END), 2) AS avg_comments_per_post,
                ROUND(AVG(score), 2)                                            AS avg_score_per_post,
                COUNT(DISTINCT CASE WHEN author != '[deleted]' THEN author END) AS unique_authors
            FROM posts
            WHERE data_source = 'arctic_shift'
            GROUP BY subreddit, collected_date
            """
        )
        _conn.commit()
        return result.rowcount
    finally:
        if conn is None:
            _conn.close()


def export_site_meta_json(
    output_path: Optional[Path] = None,
    conn: Optional[sqlite3.Connection] = None,
) -> Path:
    """Write site metadata JSON (total posts, date range, etc.)."""
    path = output_path or DATA_DIR / "site_meta.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    _conn = conn or get_connection()
    try:
        total_posts = _conn.execute("SELECT COUNT(*) FROM posts").fetchone()[0]
        date_range = _conn.execute(
            "SELECT MIN(date(created_utc, 'unixepoch')), MAX(date(created_utc, 'unixepoch')) FROM posts"
        ).fetchone()
        meta = {
            "total_posts": total_posts,
            "date_start": date_range[0] if date_range else None,
            "date_end": date_range[1] if date_range else None,
        }
        path.write_text(json.dumps(meta, indent=2))
    finally:
        if conn is None:
            _conn.close()
    return path


def export_snapshots_json(
    output_path: Optional[Path] = None,
    conn: Optional[sqlite3.Connection] = None,
) -> Path:
    """Write frontend-ready snapshots JSON."""
    path = output_path or DATA_DIR / "snapshots.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = get_all_snapshots_for_chart(conn=conn)
    path.write_text(json.dumps(rows, indent=2))
    return path


def export_subreddits_json(
    output_path: Optional[Path] = None,
    conn: Optional[sqlite3.Connection] = None,
) -> Path:
    """Write frontend-ready subreddit metadata JSON (latest snapshot per active subreddit)."""
    path = output_path or DATA_DIR / "subreddits.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    _conn = conn or get_connection()
    try:
        rows = _conn.execute(
            """
            SELECT s.subreddit, s.snapshot_date, s.subscribers, s.active_users,
                   s.posts_today, s.avg_comments_per_post, s.avg_score_per_post,
                   s.unique_authors, s.unique_post_authors_7d,
                   s.unique_comment_authors_7d, s.unique_contributors_7d,
                   c.category, c.tier, c.display_name
            FROM subreddit_snapshots s
            INNER JOIN subreddit_config c ON c.subreddit = s.subreddit AND c.is_active = 1
            WHERE s.snapshot_date = (
                SELECT MAX(snapshot_date) FROM subreddit_snapshots WHERE subreddit = s.subreddit
            )
            ORDER BY s.subreddit ASC
            """
        ).fetchall()
        path.write_text(json.dumps([dict(r) for r in rows], indent=2))
    finally:
        if conn is None:
            _conn.close()
    return path


def export_keyword_trends_json(
    output_path: Optional[Path] = None,
    conn: Optional[sqlite3.Connection] = None,
) -> Path:
    """Export daily keyword category counts with 7-day rolling averages.

    Filters to T1-T3 companion subs only (excludes T0 general AI subs and
    bot-listing-heavy subs like JanitorAI/SillyTavern). The subreddit context
    provides the AI companionship filter; keywords capture thematic dimensions.

    Output format:
        {
          "category_name": [
            {"date": "YYYY-MM-DD", "count": N, "count_7d_avg": N},
            ...
          ],
          ...
        }
    """
    from src.config import load_keyword_communities
    active_subreddits = [c["subreddit"] for c in load_keyword_communities()]
    placeholders = ",".join("?" * len(active_subreddits))

    path = output_path or DATA_DIR / "keyword_trends.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    _conn = conn or get_connection()

    try:
        # Post+comment metric (all sources — the new default)
        rows = _conn.execute(
            f"""
            SELECT category, post_date, COUNT(DISTINCT post_id) AS count
            FROM post_keyword_tags
            WHERE subreddit IN ({placeholders})
            GROUP BY category, post_date
            ORDER BY category, post_date
            """,
            active_subreddits,
        ).fetchall()
        total_posts_rows = _conn.execute(
            f"""
            SELECT date(created_utc, 'unixepoch') AS post_date, COUNT(*) AS count
            FROM posts
            WHERE subreddit IN ({placeholders})
              AND created_utc IS NOT NULL
            GROUP BY post_date
            ORDER BY post_date
            """,
            active_subreddits,
        ).fetchall()
    finally:
        if conn is None:
            _conn.close()

    # Group by category, then compute 7-day rolling average
    from collections import defaultdict
    by_category: dict = defaultdict(list)
    for category, post_date, count in rows:
        by_category[category].append({
            "date": post_date,
            "count": count,
        })

    result = {}
    for category, entries in sorted(by_category.items()):
        with_avg = []
        for i, entry in enumerate(entries):
            window = [e["count"] for e in entries[max(0, i - 6): i + 1]]
            avg = round(sum(window) / len(window), 2)
            with_avg.append({
                "date": entry["date"],
                "count": entry["count"],
                "count_7d_avg": avg,
            })
        result[category] = with_avg

    # Total posts per day across active subreddits (for client-side normalization)
    total_posts_list = [
        {"date": date, "count": count}
        for date, count in total_posts_rows
    ]
    result["_total_posts"] = total_posts_list

    # Data quality check: warn if any recent day has abnormal post count
    import logging
    _logger = logging.getLogger(__name__)
    recent = [e for e in total_posts_list if e["date"] >= "2026-01-01"]
    if recent:
        counts = [e["count"] for e in recent]
        median = sorted(counts)[len(counts) // 2]
        for e in recent[-30:]:
            if e["count"] > median * 3:
                _logger.warning(
                    "DATA QUALITY: %s has %d posts (%.1fx median %d) — possible batch collection artifact",
                    e["date"], e["count"], e["count"] / median, median,
                )

    path.write_text(json.dumps(result, indent=2))
    return path
