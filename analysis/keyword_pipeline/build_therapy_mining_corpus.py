#!/usr/bin/env python3
"""Build a YES-post corpus for therapy anchor-mining.

Pulls posts labeled YES under the cleanest therapy anchors (coping mechanism,
ai therapist) and formats them as a corpus file. CC subagents read this and
extract candidate phrases (2-5 words) that signal first-person AI-therapy use
but are NOT already in keywords_v8.yaml.

Output: results/mining_therapy_yes_corpus_2026-05-12.md
"""

import sqlite3
import yaml
from datetime import date
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
DB_PATH = PROJECT_ROOT / "data" / "tracker.db"
RESULTS = Path(__file__).parent / "results"

ANCHORS = [
    ("coping mechanism", "100% audit agreement"),
    ("ai therapist", "85% audit agreement"),
]


def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    # Read existing therapy keywords for the exclusion list
    with open(PROJECT_ROOT / "config" / "keywords_v8.yaml") as f:
        cfg = yaml.safe_load(f)
    existing_therapy = []
    for cat in cfg["keyword_categories"]:
        if cat["name"] == "therapy":
            existing_therapy = list(cat.get("terms", []))
            break

    out_path = RESULTS / f"mining_therapy_yes_corpus_{date.today().isoformat()}.md"

    posts_pulled = []
    seen_ids = set()
    for keyword, note in ANCHORS:
        rows = conn.execute(
            """SELECT lc.post_id, p.title, p.selftext, p.subreddit,
                      date(p.created_utc, 'unixepoch') AS post_date
               FROM llm_classifications lc
               JOIN posts p ON p.id = lc.post_id
               WHERE lc.keyword = ? AND lc.theme = 'therapy'
                 AND lc.classification = 'YES'
               ORDER BY lc.classified_at DESC""",
            (keyword,),
        ).fetchall()
        for r in rows:
            if r["post_id"] in seen_ids:
                continue
            seen_ids.add(r["post_id"])
            posts_pulled.append((keyword, dict(r)))

    print(f"Posts in corpus: {len(posts_pulled)} (deduplicated)")
    print(f"Existing therapy keywords (excluded from candidate list): {existing_therapy}")

    with open(out_path, "w") as f:
        f.write("# Therapy anchor-mining YES corpus\n\n")
        f.write(f"**Date:** {date.today().isoformat()}\n")
        f.write(f"**Anchors used:** {', '.join(kw for kw, _ in ANCHORS)}\n")
        f.write(f"**Posts:** {len(posts_pulled)} (deduplicated across anchors)\n\n")
        f.write(f"**Existing therapy keywords (DO NOT propose these as candidates):**\n")
        for kw in existing_therapy:
            f.write(f"- `{kw}`\n")
        f.write("\n---\n\n")
        f.write("## Task\n\n")
        f.write("These posts have all been independently verified as belonging to the **Therapy** theme ")
        f.write("(AI used for mental health support, therapy substitution, emotional processing, etc.). ")
        f.write("Read each post and identify recurring 2-5-word phrases that:\n\n")
        f.write("1. Appear in multiple posts (signaling a genuine community vocabulary pattern, not idiosyncratic phrasing)\n")
        f.write("2. Express first-person AI-therapy framing (e.g., possessive AI-as-therapy, substitution comparisons, ")
        f.write("therapeutic-action verbs paired with AI)\n")
        f.write("3. Are NOT already in the existing therapy keyword list above\n")
        f.write("4. Are specific enough that you'd expect ≥80% precision (not generic words like 'depression' or 'helpful')\n\n")
        f.write("Output your candidates in a single ranked list, format:\n\n")
        f.write("```\n")
        f.write("## CANDIDATES\n")
        f.write("1. <phrase>  # appeared in ~N posts; signals X (e.g., 'substitution framing')\n")
        f.write("2. <phrase>  # appeared in ~N posts; signals X\n")
        f.write("...\n")
        f.write("```\n\n")
        f.write("Aim for 10-20 candidates ordered by your confidence they'd validate at ≥80% precision. ")
        f.write("Be specific: include the exact phrase as it should appear in a regex word-boundary match. ")
        f.write("Prefer multi-word phrases over single words (single words usually generalize too broadly).\n\n")
        f.write("---\n\n")
        f.write("## Posts\n\n")

        for i, (anchor, post) in enumerate(posts_pulled, 1):
            f.write(f"### Post {i} (anchor: {anchor})\n")
            f.write(f"**Subreddit:** r/{post['subreddit']}  ")
            f.write(f"**Date:** {post['post_date']}\n\n")
            f.write(f"**Title:** {post['title'] or '(no title)'}\n\n")
            body = (post['selftext'] or '').strip()
            if body:
                # Limit each post body to 800 chars to keep prompt size sane
                if len(body) > 800:
                    body = body[:800] + "..."
                f.write(f"**Body:** {body}\n\n")
            else:
                f.write("**Body:** (empty)\n\n")
            f.write("---\n\n")

    print(f"Wrote corpus: {out_path}")
    print(f"File size: {out_path.stat().st_size // 1024} KB")
    # Print line count for offset calculation
    with open(out_path) as f:
        lines = sum(1 for _ in f)
    print(f"Lines: {lines}")


if __name__ == "__main__":
    main()
