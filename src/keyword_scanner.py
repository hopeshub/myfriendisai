"""Scan collected posts for keyword matches by category.

Scans post title + selftext using case-insensitive substring matching.
"""

import json
import logging
import sqlite3
from datetime import date
from typing import Optional

from src.config import load_keywords
from src.db.schema import get_connection

logger = logging.getLogger(__name__)


def scan_subreddit_keywords(
    subreddit: str,
    snapshot_date: date,
    conn: Optional[sqlite3.Connection] = None,
) -> list[dict]:
    """Scan all posts for a subreddit on a given date against keyword categories.

    Returns a list of dicts with category, count, matched_terms, and post_sample_ids.
    """
    _conn = conn or get_connection()
    categories = load_keywords()

    try:
        rows = _conn.execute(
            "SELECT id, title, selftext FROM posts WHERE subreddit = ? AND collected_date = ?",
            (subreddit, snapshot_date.isoformat()),
        ).fetchall()
    finally:
        if conn is None:
            _conn.close()

    results = []
    for cat in categories:
        cat_name = cat["name"]
        terms = cat["terms"]
        matched_terms = set()
        matched_post_ids = []
        count = 0

        for row in rows:
            text = ((row["title"] or "") + " " + (row["selftext"] or "")).lower()
            post_matched = False
            for term in terms:
                if term.lower() in text:
                    matched_terms.add(term)
                    if not post_matched:
                        count += 1
                        post_matched = True
            if post_matched and len(matched_post_ids) < 10:
                matched_post_ids.append(row["id"])

        results.append({
            "subreddit": subreddit,
            "date": snapshot_date.isoformat(),
            "category": cat_name,
            "count": count,
            "matched_terms": sorted(matched_terms),
            "post_sample_ids": matched_post_ids,
        })

    return results


def store_keyword_counts(
    results: list[dict],
    conn: Optional[sqlite3.Connection] = None,
) -> None:
    """Insert or replace keyword count rows."""
    _conn = conn or get_connection()
    try:
        for r in results:
            _conn.execute(
                """
                INSERT INTO keyword_counts (subreddit, date, category, count, matched_terms, post_sample_ids)
                VALUES (:subreddit, :date, :category, :count, :matched_terms, :post_sample_ids)
                ON CONFLICT(subreddit, date, category) DO UPDATE SET
                    count=excluded.count,
                    matched_terms=excluded.matched_terms,
                    post_sample_ids=excluded.post_sample_ids
                """,
                {
                    "subreddit": r["subreddit"],
                    "date": r["date"],
                    "category": r["category"],
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
    """Export keyword_counts table to JSON."""
    from pathlib import Path
    from src.db.operations import DATA_DIR

    path = output_path or DATA_DIR / "keywords.json"
    path.parent.mkdir(parents=True, exist_ok=True)

    _conn = conn or get_connection()
    try:
        rows = _conn.execute(
            "SELECT subreddit, date, category, count, matched_terms, post_sample_ids FROM keyword_counts ORDER BY subreddit, date, category"
        ).fetchall()
        data = []
        for r in rows:
            data.append({
                "subreddit": r["subreddit"],
                "date": r["date"],
                "category": r["category"],
                "count": r["count"],
                "matched_terms": json.loads(r["matched_terms"]) if r["matched_terms"] else [],
            })
        path.write_text(json.dumps(data, indent=2))
    finally:
        if conn is None:
            _conn.close()
    return path
