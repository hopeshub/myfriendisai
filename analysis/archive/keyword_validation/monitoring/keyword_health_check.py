#!/usr/bin/env python3
"""Re-validate all active keywords for a theme by sampling recent posts.

Flags any keyword scoring below 70% precision as potentially degraded.

Usage:
    python keyword_health_check.py --theme "sexual_erp" --sample-per-keyword 10 --recent-months 3
    python keyword_health_check.py --theme therapy
"""

import argparse
import csv
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils import get_conn, load_all_theme_keywords, pull_matching_posts, highlight_snippet

RESULTS_DIR = Path(__file__).parent.parent / "results"


def main():
    parser = argparse.ArgumentParser(description="Health check for active keywords")
    parser.add_argument("--theme", required=True, help="Theme to health-check")
    parser.add_argument("--sample-per-keyword", type=int, default=10, help="Posts to sample per keyword")
    parser.add_argument("--recent-months", type=int, default=3, help="Only sample posts from last N months")
    args = parser.parse_args()

    theme_keywords, _ = load_all_theme_keywords()
    if args.theme not in theme_keywords:
        print(f"Error: theme '{args.theme}' not found. Available: {', '.join(theme_keywords.keys())}")
        sys.exit(1)

    keywords = theme_keywords[args.theme]
    conn = get_conn()

    print(f"\nHealth check: '{args.theme}' ({len(keywords)} keywords)")
    print(f"Sampling {args.sample_per_keyword} recent posts per keyword (last {args.recent_months} months)")
    print(f"Scoring: y=yes, n=no, a=ambiguous (half-credit in precision)")
    print("=" * 60)

    results = []

    for keyword in keywords:
        posts = pull_matching_posts(
            keyword, conn,
            limit=args.sample_per_keyword,
            recent_months=args.recent_months
        )

        if not posts:
            print(f"\n  '{keyword}' — NO RECENT POSTS (0 hits in last {args.recent_months}m)")
            results.append((keyword, 0, 0, 0, 0, "NO_DATA"))
            continue

        print(f"\n--- Keyword: '{keyword}' ({len(posts)} posts) ---")
        y_count = 0
        n_count = 0
        amb_count = 0

        for i, post in enumerate(posts, 1):
            title = post.get("title", "") or ""
            body = post.get("selftext", "") or ""
            sub = post.get("subreddit", "")

            print(f"\n  [{i}/{len(posts)}] r/{sub}: {title[:150]}")
            snippet = highlight_snippet(body, keyword, max_len=200)
            if snippet:
                print(f"  {snippet}")

            while True:
                response = input(f"  About [{args.theme}]? (y/n/a for ambiguous): ").strip().lower()
                if response in ("y", "n", "a"):
                    break

            if response == "y":
                y_count += 1
            elif response == "n":
                n_count += 1
            else:
                amb_count += 1

        total_judged = y_count + n_count + amb_count
        precision = ((y_count + amb_count * 0.5) / total_judged * 100) if total_judged > 0 else 0
        ambiguity_rate = (amb_count / total_judged * 100) if total_judged > 0 else 0
        status = "OK" if precision >= 70 else "DEGRADED"
        results.append((keyword, precision, y_count, n_count, amb_count, status))
        print(f"  → {precision:.0f}% ({y_count}y + {amb_count}×0.5a / {total_judged}) — {status}")
        if ambiguity_rate > 0:
            print(f"    Ambiguity rate: {amb_count}/{total_judged} ({ambiguity_rate:.0f}%)")

    # Summary table
    print("\n" + "=" * 70)
    print(f"Health Check Summary: {args.theme}")
    print("-" * 70)
    print(f"{'Keyword':<30} {'Precision':<12} {'Y/N/A':<12} {'Amb%':<8} {'Status':<10}")
    print("-" * 70)
    degraded = []
    for keyword, precision, y, n, amb, status in results:
        flag = "⚠ " if status == "DEGRADED" else "  "
        total_j = y + n + amb
        amb_pct = (amb / total_j * 100) if total_j > 0 else 0
        print(f"{flag}{keyword:<28} {precision:>5.1f}%      {y}/{n}/{amb:<5} {amb_pct:>4.0f}%    {status}")
        if status == "DEGRADED":
            degraded.append(keyword)

    if degraded:
        print(f"\n⚠  {len(degraded)} degraded keyword(s): {', '.join(degraded)}")
    else:
        print(f"\n✓  All keywords passing (≥70%)")
    print("=" * 70)

    # Save results
    date_str = datetime.now().strftime("%Y-%m-%d")
    out_path = RESULTS_DIR / f"health_check_{date_str}.csv"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with open(out_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["keyword", "theme", "precision", "y_count", "n_count",
                         "ambiguous_count", "ambiguity_rate", "status", "date"])
        for keyword, precision, y, n, amb, status in results:
            total_j = y + n + amb
            amb_rate = (amb / total_j * 100) if total_j > 0 else 0
            writer.writerow([keyword, args.theme, f"{precision:.1f}", y, n, amb,
                             f"{amb_rate:.1f}", status, date_str])

    print(f"Results saved to {out_path}")
    conn.close()


if __name__ == "__main__":
    main()
