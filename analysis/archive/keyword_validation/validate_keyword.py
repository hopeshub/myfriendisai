#!/usr/bin/env python3
"""Keyword validation orchestrator — single entry point for the full pipeline.

Mode 1 (Evaluate): Volume check → generate scoring sheet for Claude Code
Mode 2 (Finalize): Record scores from Claude Code → set final status

Usage:
    # Evaluate a new keyword candidate:
    python validate_keyword.py --keyword "selfhood" --theme consciousness

    # After Claude Code scores the posts, finalize:
    python validate_keyword.py --keyword "selfhood" --theme consciousness \
        --finalize --precision 85.0 --ambiguity 5.0 --collisions "none"

    # Options:
    python validate_keyword.py --keyword "reframing" --theme therapy \
        --sample-size 30 --period 1y --source corpus_comparison
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import (
    get_conn, count_keyword_hits, count_keyword_hits_by_sub,
    pull_matching_posts, highlight_snippet, update_candidate,
)

RESULTS_DIR = Path(__file__).parent / "results"

# Theme name normalization — accept display names or config names
THEME_ALIASES = {
    "consciousness": "consciousness",
    "therapy": "therapy",
    "addiction": "addiction",
    "romance": "romance",
    "sexual_erp": "sexual_erp",
    "sex / erp": "sexual_erp",
    "sex/erp": "sexual_erp",
    "rupture": "rupture",
}

THEME_DISPLAY = {
    "consciousness": "Consciousness",
    "therapy": "Therapy",
    "addiction": "Addiction",
    "romance": "Romance",
    "sexual_erp": "Sex / ERP",
    "rupture": "Rupture",
}

CROSS_THEME_NAMES = ["Romance", "Sex/ERP", "Consciousness", "Therapy", "Addiction", "Rupture", "None"]


def normalize_theme(raw):
    """Normalize theme input to config name."""
    key = raw.strip().lower()
    if key in THEME_ALIASES:
        return THEME_ALIASES[key]
    # Try exact match
    if key in THEME_DISPLAY:
        return key
    return None


def run_volume_check(keyword, conn, period=None):
    """Run volume check and concentration analysis. Returns (total, by_sub, concentration_flag)."""
    total = count_keyword_hits(keyword, conn, period=period)
    by_sub = count_keyword_hits_by_sub(keyword, conn, period=period)

    concentration_flag = "none"
    if by_sub and total > 0:
        top1_pct = by_sub[0][1] / total * 100
        top2_pct = sum(s[1] for s in by_sub[:2]) / total * 100 if len(by_sub) >= 2 else top1_pct

        single = top1_pct > 50
        pair = top2_pct > 75 and len(by_sub) >= 2

        if single and pair:
            concentration_flag = "both"
        elif single:
            concentration_flag = "single_sub_dominant"
        elif pair:
            concentration_flag = "top_two_dominant"

    return total, by_sub, concentration_flag


def generate_scoring_sheet(keyword, theme, posts, total_hits, output_path):
    """Write the markdown scoring sheet for Claude Code."""
    theme_display = THEME_DISPLAY.get(theme, theme)
    date_str = datetime.now().strftime("%Y-%m-%d")

    with open(output_path, "w") as f:
        f.write("# Keyword Validation Scoring Sheet\n\n")
        f.write(f"**Keyword:** {keyword}\n")
        f.write(f"**Target Theme:** {theme_display}\n")
        f.write(f"**Date:** {date_str}\n")
        f.write(f"**Sample Size:** {len(posts)}\n")
        f.write(f"**Total Hits:** {total_hits}\n\n")

        f.write("**Instructions:** For each post below, provide TWO scores:\n\n")
        f.write(f'1. **Precision:** Is this post genuinely about the theme "{theme_display}"?\n')
        f.write(f"   - YES: The post is clearly about {theme_display}\n")
        f.write(f"   - NO: The post is not about {theme_display}\n")
        f.write("   - AMBIGUOUS: Unclear or borderline\n\n")
        f.write("2. **Best-fit theme:** Which theme does this post BEST belong to?\n")
        f.write("   - Romance, Sex/ERP, Consciousness, Therapy, Addiction, Rupture, or None\n\n")

        f.write("After scoring all posts, provide a summary in this exact format:\n\n")
        f.write("```\n")
        f.write("PRECISION: {yes_count}/{total} = {percentage}%\n")
        f.write("AMBIGUOUS: {count}/{total} = {percentage}%\n")
        f.write("CROSS-THEME DISTRIBUTION:\n")
        for t in CROSS_THEME_NAMES:
            f.write(f"  {t}: {{count}}\n")
        f.write('COLLISIONS ABOVE 30%: {list or "none"}\n')
        f.write("```\n\n")

        f.write("---\n\n")
        f.write("## Posts to Score\n\n")

        for i, post in enumerate(posts, 1):
            title = post.get("title", "") or "(no title)"
            sub = post.get("subreddit", "")
            date = post.get("collected_date", "")
            post_id = post.get("id", "")
            body = post.get("selftext", "") or ""

            permalink = f"https://www.reddit.com/comments/{post_id}" if post_id else ""
            snippet = highlight_snippet(body, keyword, max_len=500)

            f.write(f"### Post {i} of {len(posts)}\n")
            f.write(f"**Title:** {title}\n")
            f.write(f"**Subreddit:** r/{sub}\n")
            f.write(f"**Date:** {date}\n")
            if permalink:
                f.write(f"**Permalink:** {permalink}\n")
            if snippet:
                f.write(f"**Snippet:**\n> {snippet}\n")
            f.write("\n---\n\n")


def mode_evaluate(args):
    """Mode 1: Volume check + generate scoring sheet."""
    theme = normalize_theme(args.theme)
    if not theme:
        print(f"Error: unknown theme '{args.theme}'. Use one of: {', '.join(THEME_ALIASES.keys())}")
        sys.exit(1)

    conn = get_conn()

    # Step 1: Volume check
    print(f"\n{'='*55}")
    print(f"  EVALUATING: '{args.keyword}' → {THEME_DISPLAY.get(theme, theme)}")
    print(f"{'='*55}\n")

    total, by_sub, concentration = run_volume_check(args.keyword, conn, period=args.period)

    period_label = f" (last {args.period})" if args.period else " (all time)"
    print(f"Volume: {total} hits{period_label}")

    if by_sub:
        print(f"\nPer-subreddit breakdown:")
        for sub, count in by_sub:
            pct = (count / total * 100) if total > 0 else 0
            bar = "█" * max(1, int(pct / 3))
            print(f"  r/{sub:<25} {count:>5}  ({pct:5.1f}%) {bar}")

    if total < 50:
        print(f"\n❌ REJECTED: Below volume threshold ({total} hits)")
        update_candidate(args.keyword, theme, {
            "source_method": args.source,
            "discovery_date": datetime.now().strftime("%Y-%m-%d"),
            "raw_count": str(total),
            "concentration_flag": concentration,
            "status": "rejected",
            "notes": f"Below volume threshold ({total} hits)",
        })
        print(f"Logged to candidates.csv → status: rejected")
        conn.close()
        return

    print(f"\n✓ Volume: {total} hits (passes threshold)")

    if concentration != "none":
        if "single" in concentration or concentration == "both":
            print(f"⚠  Concentration: r/{by_sub[0][0]} accounts for {by_sub[0][1]/total*100:.0f}% of hits")
        if "top_two" in concentration or concentration == "both":
            top2 = sum(s[1] for s in by_sub[:2]) / total * 100
            print(f"⚠  Concentration: Top 2 subs account for {top2:.0f}% of hits")
    else:
        print(f"✓ Concentration: evenly distributed")

    # Step 2: Sample posts and generate scoring sheet
    print(f"\nSampling {args.sample_size} posts...")
    posts = pull_matching_posts(args.keyword, conn, limit=args.sample_size)

    if not posts:
        print("Error: No matching posts found.")
        conn.close()
        return

    print(f"Got {len(posts)} posts.")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    date_str = datetime.now().strftime("%Y-%m-%d")
    safe_kw = args.keyword.replace(" ", "_")
    filename = f"scoring_{safe_kw}_{theme}_{date_str}.md"
    output_path = RESULTS_DIR / filename

    generate_scoring_sheet(args.keyword, theme, posts, total, output_path)

    # Log to candidates.csv as testing
    update_candidate(args.keyword, theme, {
        "source_method": args.source,
        "discovery_date": datetime.now().strftime("%Y-%m-%d"),
        "raw_count": str(total),
        "concentration_flag": concentration,
        "status": "testing",
    })

    # Step 3: Print next steps
    rel_path = f"analysis/keyword_validation/results/{filename}"
    print(f"""
{'═'*55}
  VALIDATION FILE READY

  Volume: {total} hits ✓
  Concentration: {concentration}

  Next step — tell Claude Code:

    read {rel_path} and score every post according to the instructions. Give me the summary at the end.

  Then run:

    python validate_keyword.py --keyword "{args.keyword}" --theme "{args.theme}" --finalize --precision {{score}} --ambiguity {{score}} --collisions "{{collision_string}}"
{'═'*55}""")

    conn.close()


def mode_finalize(args):
    """Mode 2: Record scores and set final status."""
    theme = normalize_theme(args.theme)
    if not theme:
        print(f"Error: unknown theme '{args.theme}'. Use one of: {', '.join(THEME_ALIASES.keys())}")
        sys.exit(1)

    precision = args.precision
    ambiguity = args.ambiguity
    collisions_raw = args.collisions.strip()

    # Parse collisions
    has_collision = False
    if collisions_raw.lower() != "none" and collisions_raw:
        # Parse "Addiction:35%,Therapy:10%" format
        for part in collisions_raw.split(","):
            part = part.strip()
            if ":" in part:
                pct_str = part.split(":")[1].strip().rstrip("%")
                try:
                    if float(pct_str) > 30:
                        has_collision = True
                except ValueError:
                    pass

    # Apply decision rules — precision <60% is always rejected regardless of collisions
    if precision < 60:
        status = "rejected"
    elif precision >= 80 and not has_collision:
        status = "validated"
    else:
        status = "testing"

    # Determine icons
    prec_icon = "✓" if precision >= 80 else ("⚠" if precision >= 60 else "❌")
    collision_display = collisions_raw if collisions_raw.lower() != "none" else "none"

    # Get existing candidate data for volume/concentration
    from utils import _read_candidates
    rows = _read_candidates()
    existing = None
    for r in rows:
        if r.get("candidate") == args.keyword and r.get("target_theme") == theme:
            existing = r
            break

    volume = existing.get("raw_count", "?") if existing else "?"
    conc = existing.get("concentration_flag", "?") if existing else "?"

    # Update candidates.csv
    update_candidate(args.keyword, theme, {
        "precision_score": f"{precision:.1f}",
        "ambiguity_rate": f"{ambiguity:.1f}",
        "cross_theme_collisions": collision_display,
        "status": status,
    })

    # Build verdict
    if status == "validated":
        status_label = "VALIDATED"
        next_step = f'Ready to add to keyword list. Tell CC:\n    Add \'{args.keyword}\' to the {THEME_DISPLAY.get(theme, theme)} theme keyword list and backfill historical posts.'
    elif status == "testing":
        status_label = "NEEDS SECOND ROUND"
        reasons = []
        if precision < 80:
            reasons.append(f"precision {precision:.1f}% (needs ≥80%)")
        if has_collision:
            reasons.append(f"cross-theme collision")
        next_step = f"Run again with --sample-size 200 for a larger review.\n    Reason: {', '.join(reasons)}"
    else:
        status_label = "REJECTED"
        next_step = "Logged as rejected in candidates.csv."

    print(f"""
{'═'*55}
  VERDICT: {args.keyword} → {THEME_DISPLAY.get(theme, theme)}

  Precision:     {precision:.1f}% {prec_icon}
  Ambiguity:     {ambiguity:.1f}%
  Volume:        {volume} hits
  Concentration: {conc}
  Collisions:    {collision_display}

  Status: {status_label}

  {next_step}
{'═'*55}""")


def main():
    parser = argparse.ArgumentParser(
        description="Keyword validation orchestrator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Evaluate a new keyword (generates scoring sheet):
  python validate_keyword.py --keyword "selfhood" --theme consciousness

  # Finalize after Claude Code scores the posts:
  python validate_keyword.py --keyword "selfhood" --theme consciousness \\
      --finalize --precision 85.0 --ambiguity 5.0 --collisions "none"

  # Evaluate with options:
  python validate_keyword.py --keyword "reframing" --theme therapy \\
      --sample-size 30 --period 1y --source corpus_comparison
""",
    )
    parser.add_argument("--keyword", required=True, help="Keyword to validate")
    parser.add_argument("--theme", required=True, help="Target theme (e.g. consciousness, therapy, 'Sex / ERP')")
    parser.add_argument("--sample-size", type=int, default=100, help="Number of posts to sample (default: 100)")
    parser.add_argument("--period", default=None, help="Time period for volume check: '1y', '6m', '30d'")
    parser.add_argument("--source", default="manual",
                        choices=["corpus_comparison", "emergence_monitor", "ethnographic", "manual"],
                        help="How this keyword was discovered (default: manual)")

    # Finalize mode flags
    parser.add_argument("--finalize", action="store_true", help="Finalize mode: record scores from Claude Code")
    parser.add_argument("--precision", type=float, help="Precision percentage from scoring (finalize mode)")
    parser.add_argument("--ambiguity", type=float, default=0.0, help="Ambiguity rate percentage (finalize mode)")
    parser.add_argument("--collisions", type=str, default="none",
                        help='Collision string: "none" or "Addiction:35%%,Therapy:10%%" (finalize mode)')

    args = parser.parse_args()

    if args.finalize:
        if args.precision is None:
            parser.error("--finalize requires --precision")
        mode_finalize(args)
    else:
        mode_evaluate(args)


if __name__ == "__main__":
    main()
