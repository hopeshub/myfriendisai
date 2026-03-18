#!/usr/bin/env python3
"""Prepare a post sample for Claude Code classification.

Pulls posts matching a keyword from the corpus, formats them into a prompt file
that CC can read and classify. CC itself is the classification engine — no API
calls needed.

Usage:
    # Prepare 100 posts for classification
    python prepare_sample.py --keyword "grieving" --theme rupture

    # Smaller sample
    python prepare_sample.py --keyword "selfhood" --theme consciousness --sample-size 20

    # Use specific posts from an existing scoring sheet
    python prepare_sample.py --keyword "grieving" --theme rupture --from-scoring-sheet ../keyword_validation/results/scoring_grieving_rupture_2026-03-16.md
"""

import argparse
import re
import sys
import yaml
from datetime import date
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
THEME_DEFS_PATH = SCRIPT_DIR / "theme_definitions.yaml"
RESULTS_DIR = SCRIPT_DIR / "results"

from utils import get_conn, pull_matching_posts, highlight_snippet


def load_theme_definitions():
    with open(THEME_DEFS_PATH) as f:
        return yaml.safe_load(f)


def extract_post_ids_from_scoring_sheet(filepath):
    """Extract Reddit post IDs from permalink lines in a scoring sheet."""
    post_ids = []
    with open(filepath) as f:
        for line in f:
            m = re.search(r'reddit\.com/comments/(\w+)', line)
            if m:
                post_ids.append(m.group(1))
    return post_ids


def fetch_posts_by_ids(post_ids, conn):
    """Fetch posts from DB by their IDs, preserving order."""
    placeholders = ",".join("?" * len(post_ids))
    rows = conn.execute(
        f"SELECT id, subreddit, title, selftext, collected_date FROM posts WHERE id IN ({placeholders})",
        post_ids
    ).fetchall()
    by_id = {r["id"]: dict(r) for r in rows}
    return [by_id[pid] for pid in post_ids if pid in by_id]


def generate_prompt_file(keyword, theme, theme_def, posts, output_path):
    """Write the classification prompt file for CC."""
    with open(output_path, "w") as f:
        f.write(f"# Post Classification Task\n\n")
        f.write(f"**Keyword:** {keyword}\n")
        f.write(f"**Target Theme:** {theme_def['name']}\n")
        f.write(f"**Date:** {date.today().isoformat()}\n")
        f.write(f"**Sample Size:** {len(posts)}\n\n")

        f.write(f"## Theme Definition\n\n")
        f.write(f"**{theme_def['name']}** — what COUNTS:\n")
        f.write(f"{theme_def['definition'].strip()}\n\n")
        f.write(f"What does NOT count:\n")
        f.write(f"{theme_def['excludes'].strip()}\n\n")

        f.write("---\n\n")
        f.write("## Instructions\n\n")
        f.write(f'For each post, classify whether it belongs to the **{theme_def["name"]}** theme.\n\n')
        f.write("Respond with a structured list in this exact format:\n\n")
        f.write("```\n")
        f.write("1. YES|NO  # brief reason\n")
        f.write("2. YES|NO  # brief reason\n")
        f.write("...\n")
        f.write("```\n\n")
        f.write("After all posts, provide:\n\n")
        f.write("```\n")
        f.write("TOTAL: {n}\n")
        f.write("YES: {count}\n")
        f.write("NO: {count}\n")
        f.write("PRECISION: {yes/total as percentage}%\n")
        f.write("```\n\n")
        f.write("---\n\n")
        f.write("## Posts to Classify\n\n")

        for i, post in enumerate(posts, 1):
            title = post.get("title", "") or ""
            body = post.get("selftext", "") or ""
            subreddit = post.get("subreddit", "")
            post_date = post.get("collected_date", "")
            post_id = post.get("id", "")
            snippet = highlight_snippet(body, keyword, max_len=500) if body else "(no body)"

            f.write(f"### Post {i} of {len(posts)}\n")
            f.write(f"**ID:** {post_id}\n")
            f.write(f"**Title:** {title}\n")
            f.write(f"**Subreddit:** r/{subreddit}\n")
            f.write(f"**Date:** {post_date}\n")
            f.write(f"**Snippet:**\n> {snippet}\n\n")
            f.write("---\n\n")

    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="Prepare a post sample for Claude Code classification.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  python prepare_sample.py --keyword "grieving" --theme rupture
  python prepare_sample.py --keyword "selfhood" --theme consciousness --sample-size 20
  python prepare_sample.py --keyword "grieving" --theme rupture \\
      --from-scoring-sheet ../keyword_validation/results/scoring_grieving_rupture_2026-03-16.md
"""
    )
    parser.add_argument("--keyword", required=True, help="Keyword to sample posts for")
    parser.add_argument("--theme", required=True, help="Target theme (romance, sexual_erp, consciousness, therapy, addiction, rupture)")
    parser.add_argument("--sample-size", type=int, default=100, help="Number of posts to sample (default: 100)")
    parser.add_argument("--from-scoring-sheet", type=str, help="Reuse post IDs from an existing scoring sheet instead of sampling new ones")

    args = parser.parse_args()

    themes = load_theme_definitions()
    if args.theme not in themes:
        print(f"ERROR: Unknown theme '{args.theme}'. Available: {', '.join(themes.keys())}")
        sys.exit(1)

    theme_def = themes[args.theme]
    conn = get_conn()

    if args.from_scoring_sheet:
        sheet_path = Path(args.from_scoring_sheet)
        if not sheet_path.exists():
            print(f"ERROR: Scoring sheet not found: {sheet_path}")
            sys.exit(1)
        post_ids = extract_post_ids_from_scoring_sheet(sheet_path)
        posts = fetch_posts_by_ids(post_ids, conn)
        print(f"Loaded {len(posts)} posts from scoring sheet ({len(post_ids)} IDs extracted)")
    else:
        posts = pull_matching_posts(args.keyword, conn, limit=args.sample_size)
        print(f"Sampled {len(posts)} posts matching '{args.keyword}'")

    conn.close()

    if not posts:
        print("No posts found.")
        sys.exit(1)

    RESULTS_DIR.mkdir(exist_ok=True)
    output_file = RESULTS_DIR / f"classify_{args.keyword}_{args.theme}_{date.today().isoformat()}.md"
    generate_prompt_file(args.keyword, args.theme, theme_def, posts, output_file)

    print(f"\nWrote: {output_file}")
    print(f"\nNext step — tell Claude Code:")
    print(f"  read {output_file} and classify every post according to the instructions.")
    print(f"\nThen run:")
    print(f"  python parse_classifications.py --input {output_file} --classifications <CC's output>")


if __name__ == "__main__":
    main()
