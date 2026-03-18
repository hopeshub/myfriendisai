#!/usr/bin/env python3
"""Prepare a batch of keyword samples for Claude Code classification.

Takes a YAML file listing keyword/theme pairs, samples posts for each, and
generates one combined prompt file. CC classifies the whole batch in one pass.

Usage:
    python prepare_batch.py --batch-file batch.yaml
    python prepare_batch.py --batch-file batch.yaml --sample-size 50

batch.yaml format:
    - keyword: soulless
      theme: rupture
    - keyword: intimate
      theme: sexual_erp
    - keyword: coping mechanism
      theme: therapy
"""

import argparse
import sys
import yaml
from datetime import date
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
THEME_DEFS_PATH = SCRIPT_DIR / "theme_definitions.yaml"
RESULTS_DIR = SCRIPT_DIR / "results"

from utils import get_conn, pull_matching_posts, highlight_snippet, count_keyword_hits


def load_theme_definitions():
    with open(THEME_DEFS_PATH) as f:
        return yaml.safe_load(f)


def main():
    parser = argparse.ArgumentParser(
        description="Prepare a batch of keyword samples for CC classification.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Example batch.yaml:
  - keyword: soulless
    theme: rupture
  - keyword: intimate
    theme: sexual_erp
"""
    )
    parser.add_argument("--batch-file", required=True, help="YAML file with keyword/theme pairs")
    parser.add_argument("--sample-size", type=int, default=100, help="Posts per keyword (default: 100)")

    args = parser.parse_args()

    batch_path = Path(args.batch_file)
    if not batch_path.exists():
        print(f"ERROR: Batch file not found: {batch_path}")
        sys.exit(1)

    with open(batch_path) as f:
        pairs = yaml.safe_load(f)

    if not pairs or not isinstance(pairs, list):
        print("ERROR: Batch file must contain a YAML list of keyword/theme pairs")
        sys.exit(1)

    themes = load_theme_definitions()
    conn = get_conn()

    RESULTS_DIR.mkdir(exist_ok=True)
    output_file = RESULTS_DIR / f"batch_{date.today().isoformat()}.md"

    skipped = []
    included = []

    with open(output_file, "w") as f:
        f.write(f"# Batch Classification Task\n\n")
        f.write(f"**Date:** {date.today().isoformat()}\n")
        f.write(f"**Keywords:** {len(pairs)}\n")
        f.write(f"**Sample size per keyword:** {args.sample_size}\n\n")

        f.write("## Instructions\n\n")
        f.write("For each keyword section below, classify every post as YES or NO for the given theme.\n\n")
        f.write("Respond with a structured list per keyword section:\n\n")
        f.write("```\n")
        f.write("## KEYWORD: {keyword} → {theme}\n")
        f.write("1. YES|NO  # brief reason\n")
        f.write("2. YES|NO  # brief reason\n")
        f.write("...\n")
        f.write("PRECISION: {yes}/{total} = {pct}%\n")
        f.write("```\n\n")
        f.write("Repeat for each keyword section.\n\n")

        for entry in pairs:
            keyword = entry["keyword"]
            theme = entry["theme"]

            if theme not in themes:
                print(f"  SKIP: Unknown theme '{theme}' for '{keyword}'")
                skipped.append((keyword, theme, "unknown theme"))
                continue

            theme_def = themes[theme]

            # Volume check
            hits = count_keyword_hits(keyword, conn)
            if hits < 50:
                print(f"  SKIP: '{keyword}' → {theme} — only {hits} hits (need ≥50)")
                skipped.append((keyword, theme, f"{hits} hits"))
                continue

            # Sample posts
            posts = pull_matching_posts(keyword, conn, limit=args.sample_size)
            if not posts:
                print(f"  SKIP: '{keyword}' → {theme} — no posts returned")
                skipped.append((keyword, theme, "no posts"))
                continue

            included.append((keyword, theme, hits, len(posts)))
            print(f"  OK: '{keyword}' → {theme} — {hits} hits, {len(posts)} sampled")

            # Write section
            f.write("=" * 60 + "\n\n")
            f.write(f"# KEYWORD: {keyword} → {theme_def['name']}\n\n")
            f.write(f"**Keyword:** {keyword}\n")
            f.write(f"**Target Theme:** {theme_def['name']}\n")
            f.write(f"**Volume:** {hits} total hits\n")
            f.write(f"**Sample Size:** {len(posts)}\n\n")

            f.write(f"**{theme_def['name']}** — what COUNTS:\n")
            f.write(f"{theme_def['definition'].strip()}\n\n")
            f.write(f"What does NOT count:\n")
            f.write(f"{theme_def['excludes'].strip()}\n\n")

            f.write("---\n\n")

            for i, post in enumerate(posts, 1):
                title = post.get("title", "") or ""
                body = post.get("selftext", "") or ""
                post_id = post.get("id", "")
                subreddit = post.get("subreddit", "")
                post_date = post.get("collected_date", "")
                snippet = highlight_snippet(body, keyword, max_len=500) if body else "(no body)"

                f.write(f"### Post {i} of {len(posts)}\n")
                f.write(f"**ID:** {post_id}\n")
                f.write(f"**Title:** {title}\n")
                f.write(f"**Subreddit:** r/{subreddit}\n")
                f.write(f"**Date:** {post_date}\n")
                f.write(f"**Snippet:**\n> {snippet}\n\n")
                f.write("---\n\n")

    conn.close()

    # Summary
    print()
    print("=" * 55)
    print(f"  BATCH PREPARED: {len(included)} keywords")
    print("=" * 55)
    for kw, th, hits, sampled in included:
        print(f"  {kw:20s} → {th:15s} ({hits} hits, {sampled} sampled)")
    if skipped:
        print()
        print(f"  Skipped {len(skipped)}:")
        for kw, th, reason in skipped:
            print(f"  {kw:20s} → {th:15s} ({reason})")
    print()
    print(f"  Output: {output_file}")
    print()
    print(f"  Next step — tell Claude Code:")
    print(f"    read {output_file} and classify every post according to the instructions.")
    print()
    print(f"  Then run:")
    print(f"    python summarize_batch.py")
    print("=" * 55)


if __name__ == "__main__":
    main()
