"""Insert and query helpers for the SQLite database."""

import json
import sqlite3
from datetime import date
from pathlib import Path
from typing import Optional

from src.db.schema import DB_PATH, get_connection, initialize

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
            SELECT s.subreddit, s.snapshot_date, s.data_source, s.subscribers, s.active_users,
                   s.visitors_7d, s.contributions_7d, s.posts_today, s.avg_comments_per_post,
                   s.avg_score_per_post, s.unique_authors
            FROM subreddit_snapshots s
            INNER JOIN subreddit_config c ON c.subreddit = s.subreddit AND c.is_active = 1
            ORDER BY s.subreddit ASC, s.snapshot_date ASC
            """
        ).fetchall()
        return [dict(r) for r in rows]
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
                   s.unique_authors, c.category, c.tier, c.display_name
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
        # Post-only metric (control — preserves historical continuity)
        rows_post_only = _conn.execute(
            f"""
            SELECT category, post_date, COUNT(DISTINCT post_id) AS count
            FROM post_keyword_tags
            WHERE subreddit IN ({placeholders})
              AND source = 'post'
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

    # Build post-only lookup: (category, date) → count
    post_only_lookup = {}
    for category, post_date, count in rows_post_only:
        post_only_lookup[(category, post_date)] = count

    # Group by category, then compute 7-day rolling average
    from collections import defaultdict
    by_category: dict = defaultdict(list)
    for category, post_date, count in rows:
        by_category[category].append({
            "date": post_date,
            "count": count,
            "count_post_only": post_only_lookup.get((category, post_date), 0),
        })

    result = {}
    for category, entries in sorted(by_category.items()):
        with_avg = []
        for i, entry in enumerate(entries):
            window = [e["count"] for e in entries[max(0, i - 6): i + 1]]
            avg = round(sum(window) / len(window), 2)
            window_po = [e["count_post_only"] for e in entries[max(0, i - 6): i + 1]]
            avg_po = round(sum(window_po) / len(window_po), 2)
            with_avg.append({
                "date": entry["date"],
                "count": entry["count"],
                "count_7d_avg": avg,
                "count_post_only": entry["count_post_only"],
                "count_post_only_7d_avg": avg_po,
            })
        result[category] = with_avg

    # Total posts per day across active subreddits (for client-side normalization)
    result["_total_posts"] = [
        {"date": date, "count": count}
        for date, count in total_posts_rows
    ]

    path.write_text(json.dumps(result, indent=2))
    return path
