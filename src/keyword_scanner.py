"""Scan collected posts (and comments for tier 1/3 subs) for keyword matches.

Features:
- Source tracking: hits stored separately for post_title, post_body, comment
- Deduplication: skips posts already scanned (via scanned_posts table)
- Comment scanning: for tier 1 and tier 3 subs, scans top 20 comments per post
- Normalization: exports keyword_density = count / total_posts_scanned
"""

import json
import logging
import sqlite3
from datetime import date
from typing import Optional

from src.config import load_keywords
from src.db.schema import get_connection

logger = logging.getLogger(__name__)

SOURCES = ("post_title", "post_body", "comment")


def _get_unscanned_posts(
    subreddit: str,
    snapshot_date: date,
    conn: sqlite3.Connection,
) -> list[dict]:
    """Get posts that haven't been keyword-scanned yet for this date."""
    rows = conn.execute(
        """
        SELECT p.id, p.title, p.selftext
        FROM posts p
        WHERE p.subreddit = ? AND p.collected_date = ?
          AND NOT EXISTS (
            SELECT 1 FROM scanned_posts sp
            WHERE sp.post_id = p.id AND sp.scan_date = ?
          )
        """,
        (subreddit, snapshot_date.isoformat(), snapshot_date.isoformat()),
    ).fetchall()
    return [dict(r) for r in rows]


def _mark_posts_scanned(
    post_ids: list[str],
    snapshot_date: date,
    conn: sqlite3.Connection,
) -> None:
    """Mark posts as scanned in the deduplication table."""
    for post_id in post_ids:
        conn.execute(
            "INSERT OR IGNORE INTO scanned_posts (post_id, scan_date) VALUES (?, ?)",
            (post_id, snapshot_date.isoformat()),
        )


def _scan_text_for_keywords(text: str, categories: list[dict]) -> dict[str, set[str]]:
    """Scan a text string against all keyword categories.
    Returns {category_name: set_of_matched_terms}.
    """
    text_lower = text.lower()
    hits = {}
    for cat in categories:
        matched = set()
        for term in cat["terms"]:
            if term.lower() in text_lower:
                matched.add(term)
        if matched:
            hits[cat["name"]] = matched
    return hits


def scan_subreddit_keywords(
    subreddit: str,
    snapshot_date: date,
    conn: Optional[sqlite3.Connection] = None,
    tier: Optional[int] = None,
    client=None,
) -> list[dict]:
    """Scan posts for keyword matches with source tracking and deduplication.

    For tier 1 and tier 3 subs, also scans top 20 comments per post (requires client).

    Returns a list of dicts: {subreddit, date, category, source, count, matched_terms, post_sample_ids}
    """
    _conn = conn or get_connection()
    categories = load_keywords()
    scan_comments = tier in (1, 3) and client is not None

    try:
        posts = _get_unscanned_posts(subreddit, snapshot_date, _conn)
    except Exception:
        if conn is None:
            _conn.close()
        raise

    if not posts:
        logger.info("  r/%s: no new posts to scan", subreddit)
        # Return zero-count rows for all categories/sources
        results = []
        for cat in categories:
            for source in SOURCES:
                if source == "comment" and not scan_comments:
                    continue
                results.append({
                    "subreddit": subreddit,
                    "date": snapshot_date.isoformat(),
                    "category": cat["name"],
                    "source": source,
                    "count": 0,
                    "matched_terms": [],
                    "post_sample_ids": [],
                    "total_posts_scanned": 0,
                })
        return results

    # Accumulators: {(category, source): {"count": int, "terms": set, "sample_ids": list}}
    accum = {}
    active_sources = list(SOURCES) if scan_comments else ["post_title", "post_body"]
    for cat in categories:
        for source in active_sources:
            accum[(cat["name"], source)] = {"count": 0, "terms": set(), "sample_ids": []}

    post_ids = [p["id"] for p in posts]

    for post in posts:
        # Scan title
        title_hits = _scan_text_for_keywords(post["title"] or "", categories)
        for cat_name, terms in title_hits.items():
            entry = accum[(cat_name, "post_title")]
            entry["count"] += 1
            entry["terms"].update(terms)
            if len(entry["sample_ids"]) < 10:
                entry["sample_ids"].append(post["id"])

        # Scan body
        body_hits = _scan_text_for_keywords(post["selftext"] or "", categories)
        for cat_name, terms in body_hits.items():
            entry = accum[(cat_name, "post_body")]
            entry["count"] += 1
            entry["terms"].update(terms)
            if len(entry["sample_ids"]) < 10:
                entry["sample_ids"].append(post["id"])

    # Scan comments for tier 1 and tier 3
    if scan_comments:
        logger.info("  r/%s: scanning comments for %d posts...", subreddit, len(posts))
        for post in posts:
            try:
                comments = client.get_post_comments(subreddit, post["id"], limit=20)
            except Exception as e:
                logger.warning("  r/%s: failed to fetch comments for %s: %s", subreddit, post["id"], e)
                continue

            for comment in comments:
                body = comment.get("body", "")
                comment_hits = _scan_text_for_keywords(body, categories)
                for cat_name, terms in comment_hits.items():
                    entry = accum[(cat_name, "comment")]
                    entry["count"] += 1
                    entry["terms"].update(terms)
                    if len(entry["sample_ids"]) < 10:
                        entry["sample_ids"].append(post["id"])

    # Mark all posts as scanned
    try:
        _mark_posts_scanned(post_ids, snapshot_date, _conn)
        _conn.commit()
    except Exception:
        if conn is None:
            _conn.close()
        raise

    total_posts = len(posts)
    results = []
    for (cat_name, source), data in accum.items():
        results.append({
            "subreddit": subreddit,
            "date": snapshot_date.isoformat(),
            "category": cat_name,
            "source": source,
            "count": data["count"],
            "matched_terms": sorted(data["terms"]),
            "post_sample_ids": data["sample_ids"],
            "total_posts_scanned": total_posts,
        })

    if conn is None:
        _conn.close()

    return results


def store_keyword_counts(
    results: list[dict],
    conn: Optional[sqlite3.Connection] = None,
) -> None:
    """Insert or replace keyword count rows with source tracking."""
    _conn = conn or get_connection()
    try:
        for r in results:
            _conn.execute(
                """
                INSERT INTO keyword_counts (subreddit, date, category, source, count, matched_terms, post_sample_ids)
                VALUES (:subreddit, :date, :category, :source, :count, :matched_terms, :post_sample_ids)
                ON CONFLICT(subreddit, date, category, source) DO UPDATE SET
                    count=excluded.count,
                    matched_terms=excluded.matched_terms,
                    post_sample_ids=excluded.post_sample_ids
                """,
                {
                    "subreddit": r["subreddit"],
                    "date": r["date"],
                    "category": r["category"],
                    "source": r["source"],
                    "count": r["count"],
                    "matched_terms": json.dumps(r["matched_terms"]),
                    "post_sample_ids": json.dumps(r["post_sample_ids"]),
                },
            )
        _conn.commit()
    finally:
        if conn is None:
            _conn.close()


def export_keywords_json(
    output_path=None,
    conn: Optional[sqlite3.Connection] = None,
):
    """Export keyword_counts table to JSON with keyword_density normalization.

    Filters to T1-T3 companion subs only (excludes T0 and bot-listing subs).
    """
    from pathlib import Path
    from src.db.operations import DATA_DIR
    from src.config import load_keyword_communities

    path = output_path or DATA_DIR / "keywords.json"
    path.parent.mkdir(parents=True, exist_ok=True)

    keyword_subs = {c["subreddit"] for c in load_keyword_communities()}

    _conn = conn or get_connection()
    try:
        rows = _conn.execute(
            "SELECT subreddit, date, category, source, count, matched_terms, post_sample_ids FROM keyword_counts ORDER BY subreddit, date, category, source"
        ).fetchall()

        # Get total posts scanned per subreddit+date for density calculation
        post_counts = {}
        post_rows = _conn.execute(
            """
            SELECT subreddit, collected_date, COUNT(*) as total
            FROM posts
            GROUP BY subreddit, collected_date
            """
        ).fetchall()
        for pr in post_rows:
            post_counts[(pr["subreddit"], pr["collected_date"])] = pr["total"]

        data = []
        for r in rows:
            if r["subreddit"] not in keyword_subs:
                continue
            total = post_counts.get((r["subreddit"], r["date"]), 0)
            density = round(r["count"] / total, 4) if total > 0 else 0
            data.append({
                "subreddit": r["subreddit"],
                "date": r["date"],
                "category": r["category"],
                "source": r["source"],
                "count": r["count"],
                "keyword_density": density,
                "matched_terms": json.loads(r["matched_terms"]) if r["matched_terms"] else [],
            })
        path.write_text(json.dumps(data, indent=2))
    finally:
        if conn is None:
            _conn.close()
    return path
