"""Insert and query helpers for the SQLite database."""

import json
import sqlite3
from datetime import date
from pathlib import Path
from typing import Optional

from src.db.schema import get_connection

DATA_DIR = Path(__file__).parent.parent.parent / "data"

# Platform-staff / dev accounts excluded from theme counts.
# These users post developer announcements, patch notes, or marketing
# content that's not community discourse. They shouldn't drive theme
# trends. Identified during the 2026-05-13 adversarial audit.
# Add accounts here as we discover them — leave the SQL hooks in place.
EXCLUDED_AUTHORS = (
    "SoulmateAI_Dev",  # Soulmate platform creator — 89 posts, 57 tagged sex/ERP
)


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

    Emits both the post+comment metric (the default, all sources) and a
    post-only control series so downstream analysis can decompose whether
    trend shifts reflect new comment coverage or discourse changes. The two
    are identical for all dates prior to comment collection (2026-03-18).

    Output format:
        {
          "category_name": [
            {
              "date": "YYYY-MM-DD",
              "count": N,              # post+comment (all sources)
              "count_7d_avg": N,
              "count_post_only": N,    # source='post' only (control)
              "count_post_only_7d_avg": N
            },
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

    excluded_authors_placeholders = ",".join("?" * len(EXCLUDED_AUTHORS))
    try:
        # Post+comment metric (all sources — the default). Excludes posts
        # from EXCLUDED_AUTHORS (platform-dev accounts whose content is
        # marketing/announcements, not community discourse).
        rows = _conn.execute(
            f"""
            SELECT t.category, t.post_date,
                   COUNT(DISTINCT t.post_id) AS count
            FROM post_keyword_tags t
            JOIN posts p ON p.id = t.post_id
            WHERE t.subreddit IN ({placeholders})
              AND (p.author IS NULL OR p.author NOT IN ({excluded_authors_placeholders}))
            GROUP BY t.category, t.post_date
            ORDER BY t.category, t.post_date
            """,
            (*active_subreddits, *EXCLUDED_AUTHORS),
        ).fetchall()
        # Post-only control series (source='post' only). Same exclusion.
        post_only_rows = _conn.execute(
            f"""
            SELECT t.category, t.post_date,
                   COUNT(DISTINCT t.post_id) AS count
            FROM post_keyword_tags t
            JOIN posts p ON p.id = t.post_id
            WHERE t.subreddit IN ({placeholders})
              AND t.source = 'post'
              AND (p.author IS NULL OR p.author NOT IN ({excluded_authors_placeholders}))
            GROUP BY t.category, t.post_date
            ORDER BY t.category, t.post_date
            """,
            (*active_subreddits, *EXCLUDED_AUTHORS),
        ).fetchall()
        # NOTE: a count_llm_verified series was removed from this export on
        # 2026-05-15. LLM verification is not part of the published chart;
        # keeping the series here also made the exporter query
        # the optional llm_classifications table, breaking fresh-schema exports
        # and the test suite. LLM verdicts live in audit data only.
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

    from collections import defaultdict
    by_category: dict = defaultdict(list)
    for category, post_date, count in rows:
        by_category[category].append({"date": post_date, "count": count})

    post_only_lookup: dict = defaultdict(dict)
    for category, post_date, count in post_only_rows:
        post_only_lookup[category][post_date] = count

    result = {}
    for category, entries in sorted(by_category.items()):
        with_avg = []
        post_only_series = post_only_lookup.get(category, {})
        for i, entry in enumerate(entries):
            window = [e["count"] for e in entries[max(0, i - 6): i + 1]]
            avg = round(sum(window) / len(window), 2)
            # Post-only count: 0 if this category had no post-source hits on this date
            post_only_count = post_only_series.get(entry["date"], 0)
            post_only_window = [
                post_only_series.get(e["date"], 0) for e in entries[max(0, i - 6): i + 1]
            ]
            post_only_avg = round(sum(post_only_window) / len(post_only_window), 2)
            with_avg.append({
                "date": entry["date"],
                "count": entry["count"],
                "count_7d_avg": avg,
                "count_post_only": post_only_count,
                "count_post_only_7d_avg": post_only_avg,
            })
        result[category] = with_avg

    # Total posts per day across active subreddits (for client-side normalization)
    total_posts_list = [
        {"date": date, "count": count}
        for date, count in total_posts_rows
    ]
    result["_total_posts"] = total_posts_list

    # ─── Per-theme coverage_start computation ──────────────────────────
    # Rule (uniform across themes):
    # coverage_start is the first month where the theme's monthly post-only
    # count is ≥ COVERAGE_THRESHOLD AND every subsequent COMPLETE month also
    # clears the threshold. The current (in-progress) calendar month is
    # excluded from the "all later months" check because it's not yet a
    # full month's data.
    #
    # Why post-only and not post+comment: post-only is comparable across the
    # full 2023-2026 timeline (comments only began tagging March 2026). Using
    # post+comment would create a phantom step-change at 2026-03 for every
    # theme. Using post-only keeps the rule corpus-comparable.
    #
    # Why N=5: empirically calibrated against 2026-05-12 data. Lands every
    # established theme at 2023-01 and consciousness at 2025-04 — the latter
    # matching the documented finding that consciousness vocabulary (currently
    # personhood/selfhood/subjective experience) is post-2024 community-jargon
    # and pre-coverage data is keyword-coverage-artifactual rather than
    # representative of real discourse. See docs/validation_v8_2_expansion_2026-05-12.md
    # and the agent-derived calibration analysis from 2026-05-13.
    COVERAGE_THRESHOLD = 5
    from datetime import date as _date
    current_month = _date.today().strftime("%Y-%m")
    coverage_start: dict[str, Optional[str]] = {}
    for category, entries in result.items():
        if category.startswith("_"):
            continue
        # Aggregate post-only counts by month
        monthly_post_only: defaultdict[str, int] = defaultdict(int)
        for entry in entries:
            month = entry["date"][:7]  # YYYY-MM
            monthly_post_only[month] += entry["count_post_only"]
        if not monthly_post_only:
            coverage_start[category] = None
            continue
        # Sort months chronologically
        months = sorted(monthly_post_only.keys())
        # Find first month where this month and every subsequent COMPLETE
        # month clears the threshold (current month excluded from check).
        chosen: Optional[str] = None
        for i, month in enumerate(months):
            if monthly_post_only[month] < COVERAGE_THRESHOLD:
                continue
            # Check all subsequent completed months
            later = [m for m in months[i + 1:] if m != current_month]
            if all(monthly_post_only[m] >= COVERAGE_THRESHOLD for m in later):
                chosen = month
                break
        # Convert YYYY-MM to YYYY-MM-01 for ISO consistency
        coverage_start[category] = f"{chosen}-01" if chosen else None
    result["_coverage_start"] = coverage_start

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


def export_theme_health_json(
    output_path: Optional[Path] = None,
    conn: Optional[sqlite3.Connection] = None,
) -> Path:
    """Export per-theme health metrics for public methodology surface.

    Combines current corpus concentration stats with drift_history.json
    precision tracking. Frontend reads this to render the Theme Health
    section of the about page.
    """
    from src.config import load_keyword_communities

    path = output_path or DATA_DIR / "theme_health.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    _conn = conn or get_connection()

    DRIFT_PATH = Path(__file__).parent.parent.parent / "analysis" / "keyword_pipeline" / "drift_history.json"
    drift = json.loads(DRIFT_PATH.read_text()) if DRIFT_PATH.exists() else {"themes": {}, "keywords": {}}

    THEMES = ["rupture", "addiction", "romance", "sexual_erp", "consciousness", "therapy"]
    T1_T3 = [c["subreddit"] for c in load_keyword_communities()]
    sub_ph = ",".join("?" * len(T1_T3))

    try:
        out_themes = {}
        for theme in THEMES:
            # Post tags + comment tags
            post_total = _conn.execute(
                f"SELECT COUNT(DISTINCT post_id) FROM post_keyword_tags "
                f"WHERE category=? AND source='post' AND subreddit IN ({sub_ph})",
                (theme, *T1_T3),
            ).fetchone()[0]
            comment_total = _conn.execute(
                f"SELECT COUNT(DISTINCT comment_id) FROM comment_keyword_hits "
                f"WHERE category=? AND subreddit IN ({sub_ph})",
                (theme, *T1_T3),
            ).fetchone()[0]

            # Top sub (posts)
            top_sub_post_row = _conn.execute(
                f"""SELECT subreddit, COUNT(DISTINCT post_id) AS n
                   FROM post_keyword_tags
                   WHERE category=? AND source='post' AND subreddit IN ({sub_ph})
                   GROUP BY subreddit ORDER BY n DESC LIMIT 1""",
                (theme, *T1_T3),
            ).fetchone()
            top_sub_post = (
                {"subreddit": top_sub_post_row[0], "n": top_sub_post_row[1],
                 "pct": round(100 * top_sub_post_row[1] / post_total, 1)}
                if top_sub_post_row and post_total else None
            )

            # Top sub (comments)
            top_sub_comm_row = _conn.execute(
                f"""SELECT subreddit, COUNT(DISTINCT comment_id) AS n
                   FROM comment_keyword_hits
                   WHERE category=? AND subreddit IN ({sub_ph})
                   GROUP BY subreddit ORDER BY n DESC LIMIT 1""",
                (theme, *T1_T3),
            ).fetchone()
            top_sub_comment = (
                {"subreddit": top_sub_comm_row[0], "n": top_sub_comm_row[1],
                 "pct": round(100 * top_sub_comm_row[1] / comment_total, 1)}
                if top_sub_comm_row and comment_total else None
            )

            # Top day (posts)
            top_day_row = _conn.execute(
                f"""SELECT date(p.created_utc,'unixepoch') AS d,
                          COUNT(DISTINCT t.post_id) AS n
                   FROM post_keyword_tags t JOIN posts p ON p.id = t.post_id
                   WHERE t.category=? AND t.source='post' AND p.subreddit IN ({sub_ph})
                   GROUP BY d ORDER BY n DESC LIMIT 1""",
                (theme, *T1_T3),
            ).fetchone()
            top_day = (
                {"date": top_day_row[0], "n": top_day_row[1],
                 "pct": round(100 * top_day_row[1] / post_total, 2)}
                if top_day_row and post_total else None
            )

            # Top author share (top 5 authors' combined share)
            top5_row = _conn.execute(
                f"""SELECT SUM(n) FROM (
                       SELECT COUNT(DISTINCT t.post_id) AS n
                       FROM post_keyword_tags t JOIN posts p ON p.id = t.post_id
                       WHERE t.category=? AND t.source='post' AND p.subreddit IN ({sub_ph})
                         AND p.author NOT IN ('[deleted]','AutoModerator') AND p.author IS NOT NULL
                       GROUP BY p.author ORDER BY n DESC LIMIT 5
                   )""",
                (theme, *T1_T3),
            ).fetchone()
            top5_n = top5_row[0] if top5_row and top5_row[0] is not None else 0
            top5_authors_pct = round(100 * top5_n / post_total, 1) if post_total else 0.0

            # 3-month event share: month with largest contribution + flanking 2 months
            # Approximation: take top month and report it + its share
            top_month_row = _conn.execute(
                f"""SELECT strftime('%Y-%m', p.created_utc, 'unixepoch') AS m,
                          COUNT(DISTINCT t.post_id) AS n
                   FROM post_keyword_tags t JOIN posts p ON p.id = t.post_id
                   WHERE t.category=? AND t.source='post' AND p.subreddit IN ({sub_ph})
                   GROUP BY m ORDER BY n DESC LIMIT 1""",
                (theme, *T1_T3),
            ).fetchone()
            top_month = (
                {"month": top_month_row[0], "n": top_month_row[1],
                 "pct": round(100 * top_month_row[1] / post_total, 1)}
                if top_month_row and post_total else None
            )

            # Drift precision
            drift_theme = drift.get("themes", {}).get(theme, {})
            post_history = drift_theme.get("post_level", {}).get("history", [])
            comm_history = drift_theme.get("comment_level", {}).get("history", [])
            post_precision = post_history[-1] if post_history else None
            comment_precision = comm_history[-1] if comm_history else None

            # LLM-verified precision stats were removed from this export on
            # 2026-05-15. The verdicts were produced under a lenient prompt that
            # inflates precision (~95% vs an adversarial audit's 51-72%), so a
            # public precision number derived from them would mislead. LLM
            # verification is no longer surfaced on the site.

            out_themes[theme] = {
                "total_post_tags": post_total,
                "total_comment_tags": comment_total,
                "top_sub_post": top_sub_post,
                "top_sub_comment": top_sub_comment,
                "top_day": top_day,
                "top_month": top_month,
                "top5_authors_pct": top5_authors_pct,
                "post_precision": post_precision,
                "comment_precision": comment_precision,
                "noisy_keywords_comment": drift_theme.get("noisy_keywords_comment", []),
            }

        result = {
            "generated_at": date.today().isoformat(),
            "drift_last_updated": drift.get("last_updated"),
            "themes": out_themes,
        }
        path.write_text(json.dumps(result, indent=2))
    finally:
        if conn is None:
            _conn.close()
    return path
