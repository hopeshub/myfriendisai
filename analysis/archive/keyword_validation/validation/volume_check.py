#!/usr/bin/env python3
"""Quick count of how many posts a candidate keyword matches.

Includes subreddit concentration analysis.

Usage:
    python volume_check.py --keyword "intimate"
    python volume_check.py --keyword "intimate" --period 1y
    python volume_check.py --keyword "ai therapist" --period 6m --theme therapy
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils import get_conn, count_keyword_hits, count_keyword_hits_by_sub, update_candidate


def main():
    parser = argparse.ArgumentParser(description="Volume check for a keyword")
    parser.add_argument("--keyword", required=True, help="Keyword to check")
    parser.add_argument("--period", default=None, help="Time period: '1y', '6m', '30d' (default: all time)")
    parser.add_argument("--theme", default=None, help="Target theme (for candidates.csv logging)")
    args = parser.parse_args()

    conn = get_conn()

    total = count_keyword_hits(args.keyword, conn, period=args.period)
    by_sub = count_keyword_hits_by_sub(args.keyword, conn, period=args.period)

    period_label = f" (last {args.period})" if args.period else " (all time)"
    print(f"\nKeyword: '{args.keyword}'{period_label}")
    print(f"Total hits: {total}")

    if total < 50:
        print(f"  ⚠  Below 50-hit volume threshold")

    if by_sub:
        print(f"\nPer-subreddit breakdown:")
        for sub, count in by_sub:
            pct = (count / total * 100) if total > 0 else 0
            bar = "█" * max(1, int(pct / 3))
            print(f"  r/{sub:<25} {count:>5}  ({pct:5.1f}%) {bar}")

    # Concentration analysis
    concentration_flag = "none"
    top1_pct = (by_sub[0][1] / total * 100) if by_sub and total > 0 else 0
    top2_pct = (sum(s[1] for s in by_sub[:2]) / total * 100) if len(by_sub) >= 2 and total > 0 else top1_pct

    warnings = []
    if top1_pct > 50:
        warnings.append(f"⚠  CONCENTRATION WARNING: r/{by_sub[0][0]} accounts for {top1_pct:.0f}% of all hits")
        concentration_flag = "single_sub_dominant"
    if top2_pct > 75 and len(by_sub) >= 2:
        warnings.append(f"⚠  CONCENTRATION WARNING: Top 2 subreddits account for {top2_pct:.0f}% of all hits")
        if concentration_flag == "single_sub_dominant":
            concentration_flag = "both"
        else:
            concentration_flag = "top_two_dominant"

    print()
    if warnings:
        for w in warnings:
            print(w)
    else:
        print("✓  Distribution: No concentration issues detected")

    # Auto-log to candidates.csv if theme is provided
    if args.theme:
        candidate_updates = {
            "raw_count": str(total),
            "concentration_flag": concentration_flag,
            "discovery_date": datetime.now().strftime("%Y-%m-%d"),
        }
        if total < 50:
            candidate_updates["status"] = "rejected"
            candidate_updates["notes"] = f"Below volume threshold ({total} hits)"
        update_candidate(args.keyword, args.theme, candidate_updates)
        print(f"\nUpdated candidates.csv → raw_count: {total}, concentration: {concentration_flag}")

    conn.close()


if __name__ == "__main__":
    main()
