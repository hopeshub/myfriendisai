#!/usr/bin/env python3
"""Summarize all CC classifications stored in SQLite.

Reads the llm_classifications table and outputs a summary table showing
precision per keyword/theme, with top false-positive patterns.

Usage:
    # Show all classified keywords
    python summarize_batch.py

    # Filter to a specific theme
    python summarize_batch.py --theme rupture

    # Show FP details (top NO reasons per keyword)
    python summarize_batch.py --show-fps
"""

import argparse
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
DB_PATH = PROJECT_ROOT / "data" / "tracker.db"

from utils import get_conn, count_keyword_hits


def main():
    parser = argparse.ArgumentParser(
        description="Summarize CC classifications from SQLite.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  python summarize_batch.py
  python summarize_batch.py --theme rupture
  python summarize_batch.py --show-fps
"""
    )
    parser.add_argument("--theme", help="Filter to a specific theme")
    parser.add_argument("--show-fps", action="store_true", help="Show top false-positive reasons per keyword")
    parser.add_argument("--all-runs", action="store_true",
                        help="Summarize all stored rows instead of only the latest run per keyword/theme")
    parser.add_argument("--run-id", help="Summarize a specific run ID")

    args = parser.parse_args()

    conn = get_conn()

    # Check table exists
    table_check = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='llm_classifications'"
    ).fetchone()
    if not table_check:
        print("No llm_classifications table found. Run classifications first.")
        sys.exit(1)

    columns = {
        row["name"] for row in conn.execute("PRAGMA table_info(llm_classifications)").fetchall()
    }
    has_run_id = "run_id" in columns

    # Get all keyword/theme combos
    query = """
        SELECT keyword, theme,
               COALESCE(run_id, 'legacy') as run_id,
               SUM(CASE WHEN classification = 'YES' THEN 1 ELSE 0 END) as yes_count,
               SUM(CASE WHEN classification = 'NO' THEN 1 ELSE 0 END) as no_count,
               COUNT(*) as total,
               MAX(classified_at) as last_classified_at
        FROM llm_classifications
    """
    params = []
    where_clauses = []
    if args.theme:
        where_clauses.append("theme = ?")
        params.append(args.theme)
    if args.run_id:
        if has_run_id:
            where_clauses.append("run_id = ?")
            params.append(args.run_id)
        else:
            print("This database does not have run_id data yet.")
            sys.exit(1)
    if where_clauses:
        query += " WHERE " + " AND ".join(where_clauses)
    query += " GROUP BY keyword, theme, COALESCE(run_id, 'legacy')"
    query += " ORDER BY theme, keyword, last_classified_at DESC"

    rows = conn.execute(query, params).fetchall()

    if not rows:
        print("No classifications found.")
        sys.exit(0)

    if not args.all_runs and not args.run_id:
        latest_rows = {}
        for row in rows:
            key = (row["keyword"], row["theme"])
            latest_rows.setdefault(key, row)
        rows = list(latest_rows.values())

    # Build summary with volume data
    print()
    print("=" * 95)
    print(f"  {'Keyword':<20s} {'Theme':<15s} {'Run':<24s} {'Hits':>6s} {'Sample':>7s} {'YES':>5s} {'NO':>5s} {'Prec':>7s}")
    print("-" * 95)

    for row in rows:
        keyword = row["keyword"]
        theme = row["theme"]
        run_id = row["run_id"]
        yes = row["yes_count"]
        no = row["no_count"]
        total = row["total"]
        pct = yes / total * 100 if total > 0 else 0

        # Get corpus volume
        hits = count_keyword_hits(keyword, conn)

        # Verdict marker
        if pct >= 80:
            marker = "  <<"
        elif pct >= 60:
            marker = "  ~"
        else:
            marker = ""

        print(f"  {keyword:<20s} {theme:<15s} {run_id:<24s} {hits:>6d} {total:>7d} {yes:>5d} {no:>5d} {pct:>6.1f}%{marker}")

    print("-" * 95)
    print("  << = likely keep (≥80%)   ~ = review band (60-79%)")
    if not args.all_runs and not args.run_id:
        print("  Showing latest run per keyword/theme")
    print("=" * 95)

    # Show FP details if requested
    if args.show_fps:
        print()
        for row in rows:
            keyword = row["keyword"]
            theme = row["theme"]

            fp_rows = conn.execute(
                """SELECT reason FROM llm_classifications
                   WHERE keyword = ? AND theme = ? AND COALESCE(run_id, 'legacy') = ?
                   AND classification = 'NO' AND reason != ''""",
                (keyword, theme, row["run_id"])
            ).fetchall()

            if not fp_rows:
                continue

            reasons = [r["reason"] for r in fp_rows]
            print(f"  FPs for '{keyword}' → {theme} ({len(reasons)} NO posts):")
            # Show each reason (they're brief enough)
            for r in reasons[:10]:
                print(f"    - {r}")
            if len(reasons) > 10:
                print(f"    ... and {len(reasons) - 10} more")
            print()

    conn.close()


if __name__ == "__main__":
    main()
