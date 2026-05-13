#!/usr/bin/env python3
"""Build a YES-post corpus for anchor-mining of a target theme.

Generic version of build_therapy_mining_corpus.py. Takes a theme name and a
list of anchor keywords, pulls YES-labeled posts under those anchors, and
formats them as a corpus file for CC subagent mining.

Usage:
    python build_mining_corpus.py --theme rupture --anchors "lobotomized" "grieving" "nerfed"
    python build_mining_corpus.py --theme addiction --anchors "relapsed" "clean for" "trying to quit"
"""

import argparse
import sqlite3
import yaml
from datetime import date
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
DB_PATH = PROJECT_ROOT / "data" / "tracker.db"
RESULTS = Path(__file__).parent / "results"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--theme", required=True, help="Theme name (must match keywords_v8.yaml)")
    parser.add_argument("--anchors", nargs="+", required=True, help="Anchor keywords to mine from")
    parser.add_argument("--max-posts", type=int, default=200, help="Max posts in corpus")
    args = parser.parse_args()

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    # Read existing keywords for the exclusion list
    with open(PROJECT_ROOT / "config" / "keywords_v8.yaml") as f:
        cfg = yaml.safe_load(f)
    existing = []
    for cat in cfg["keyword_categories"]:
        if cat["name"] == args.theme:
            existing = list(cat.get("terms", []))
            break
    if not existing:
        print(f"ERROR: theme '{args.theme}' not found in keywords_v8.yaml")
        return

    out_path = RESULTS / f"mining_{args.theme}_yes_corpus_{date.today().isoformat()}.md"

    posts_pulled = []
    seen_ids = set()
    for keyword in args.anchors:
        rows = conn.execute(
            """SELECT lc.post_id, p.title, p.selftext, p.subreddit,
                      date(p.created_utc, 'unixepoch') AS post_date
               FROM llm_classifications lc
               JOIN posts p ON p.id = lc.post_id
               WHERE lc.keyword = ? AND lc.theme = ?
                 AND lc.classification = 'YES'
               ORDER BY lc.classified_at DESC""",
            (keyword, args.theme),
        ).fetchall()
        for r in rows:
            if r["post_id"] in seen_ids:
                continue
            if len(posts_pulled) >= args.max_posts:
                break
            seen_ids.add(r["post_id"])
            posts_pulled.append((keyword, dict(r)))

    if not posts_pulled:
        print(f"ERROR: no YES posts found for anchors {args.anchors} in theme {args.theme}")
        return

    print(f"Posts in corpus: {len(posts_pulled)} (deduplicated across {len(args.anchors)} anchors)")

    with open(out_path, "w") as f:
        f.write(f"# {args.theme.capitalize()} anchor-mining YES corpus\n\n")
        f.write(f"**Date:** {date.today().isoformat()}\n")
        f.write(f"**Anchors used:** {', '.join(args.anchors)}\n")
        f.write(f"**Posts:** {len(posts_pulled)} (deduplicated across anchors)\n\n")
        f.write(f"**Existing {args.theme} keywords (DO NOT propose these as candidates):**\n")
        for kw in existing:
            f.write(f"- `{kw}`\n")
        f.write("\n---\n\n")
        f.write("## Task\n\n")
        f.write(f"These posts have all been independently verified as belonging to the **{args.theme.capitalize()}** theme. ")
        f.write("Read each post and identify recurring 2-5-word phrases that:\n\n")
        f.write("1. Appear in multiple posts (signaling a genuine community vocabulary pattern, not idiosyncratic phrasing)\n")
        f.write(f"2. Express first-person {args.theme}-relevant framing\n")
        f.write("3. Are NOT already in the existing keyword list above (or trivial subsets of existing keywords)\n")
        f.write("4. Are specific enough that you'd expect ≥80% precision (avoid generic words)\n")
        f.write("5. Prefer multi-word phrases over single words (single words usually generalize too broadly)\n\n")
        f.write("Output your candidates in a single ranked list, format:\n\n")
        f.write("```\n")
        f.write("## CANDIDATES\n")
        f.write("1. <phrase>  # appeared in ~N posts; signals X\n")
        f.write("2. <phrase>  # appeared in ~N posts; signals X\n")
        f.write("...\n")
        f.write("```\n\n")
        f.write("Aim for 10-20 candidates ordered by your confidence they'd validate at ≥80% precision.\n\n")
        f.write("---\n\n")
        f.write("## Posts\n\n")

        for i, (anchor, post) in enumerate(posts_pulled, 1):
            f.write(f"### Post {i} (anchor: {anchor})\n")
            f.write(f"**Subreddit:** r/{post['subreddit']}  ")
            f.write(f"**Date:** {post['post_date']}\n\n")
            f.write(f"**Title:** {post['title'] or '(no title)'}\n\n")
            body = (post['selftext'] or '').strip()
            if body:
                if len(body) > 800:
                    body = body[:800] + "..."
                f.write(f"**Body:** {body}\n\n")
            else:
                f.write("**Body:** (empty)\n\n")
            f.write("---\n\n")

    print(f"Wrote: {out_path}")
    with open(out_path) as f:
        lines = sum(1 for _ in f)
    print(f"Lines: {lines}")


if __name__ == "__main__":
    main()
