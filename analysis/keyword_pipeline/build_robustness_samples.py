#!/usr/bin/env python3
"""Build samples for the robustness audit (Tests A, B, C).

A: per-theme construct validity — 60 random tagged posts per theme
B: event-day deep dive — all tagged posts from 4 chosen dates
C: subreddit character audit — 40 posts per sub (mixed tagged + untagged)

Outputs separate .md files per test/theme/date/sub, ready for agent dispatch.
"""

import json
import random
import sqlite3
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from src.config import load_keyword_communities

PROJECT_ROOT = Path(__file__).parent.parent.parent
DB_PATH = PROJECT_ROOT / "data" / "tracker.db"
RESULTS = Path(__file__).parent / "results"
SEED = 20260513


def post_md_entry(i: int, row, show_tags: bool = False) -> str:
    body = (row['selftext'] or '').strip()
    if len(body) > 500:
        body = body[:500] + "..."
    if not body:
        body = "(no body / image post)"
    tag_line = ""
    if show_tags and 'tags' in row.keys() and row['tags']:
        tag_line = f"**Current keyword tags:** {row['tags']}\n\n"
    return (f"### POST {i}\n"
            f"**ID:** {row['id']}  **Subreddit:** r/{row['subreddit']}  "
            f"**Date:** {row['post_date']}\n\n"
            f"**Title:** {row['title'] or '(no title)'}\n\n"
            f"{tag_line}"
            f"**Body:** {body}\n\n"
            f"---\n\n")


def main():
    random.seed(SEED)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    T1_T3 = [c["subreddit"] for c in load_keyword_communities()]
    sub_ph = ",".join("?" * len(T1_T3))

    # ── Test A: 60 random tagged posts per theme ──────────────────────
    themes = ['rupture', 'addiction', 'romance', 'sexual_erp', 'consciousness']
    for theme in themes:
        rows = conn.execute(
            f"""SELECT p.id, p.subreddit, p.title, p.selftext,
                       date(p.created_utc,'unixepoch') AS post_date,
                       GROUP_CONCAT(DISTINCT t.matched_term) AS tags
                FROM post_keyword_tags t
                JOIN posts p ON p.id = t.post_id
                WHERE t.category = ? AND t.source='post'
                  AND p.subreddit IN ({sub_ph})
                GROUP BY p.id
                ORDER BY RANDOM()
                LIMIT 60""",
            (theme, *T1_T3)
        ).fetchall()
        out = RESULTS / f"robustness_A_{theme}_construct_2026-05-13.md"
        with open(out, "w") as f:
            f.write(f"# Test A — {theme.capitalize()} construct validity\n\n")
            f.write(f"60 random posts currently tagged as **{theme}** by the keyword set.\n\n")
            f.write("Read each post and answer three questions overall (one short report at the end):\n\n")
            f.write(f"1. **Per-post YES/NO**: is this post genuinely about {theme} under the rubric? Use the topical reading.\n")
            f.write("2. **Sub-type clustering**: what sub-categories of the theme do these posts cluster into? (e.g., for rupture: platform changes, model deprecation, personality loss, filter tightening, shutdown, etc.)\n")
            f.write("3. **Construct-invalid patterns**: any patterns where the keyword caught something off-theme? Be specific about the matched term and the off-theme context.\n\n")
            f.write("Output format at end:\n\n```\n")
            f.write("## Per-post quick verdicts\n")
            f.write("1. YES  # short reason or sub-type label\n")
            f.write("2. NO   # why not\n")
            f.write("...\n")
            f.write("60. YES  # short reason or sub-type label\n\n")
            f.write("## Sub-type breakdown\n")
            f.write("- sub-type 1: count, examples (post numbers)\n")
            f.write("- sub-type 2: count, examples\n")
            f.write("- ...\n\n")
            f.write("## Construct-invalid patterns\n")
            f.write("- pattern 1: description, posts affected, suggested fix\n")
            f.write("- ...\n\n")
            f.write("## Bottom line\n")
            f.write("One paragraph: does the theme tag what we say it tags?\n")
            f.write("```\n\n")
            f.write("---\n\n## Posts\n\n")
            for i, r in enumerate(rows, 1):
                f.write(post_md_entry(i, r, show_tags=True))
        print(f"Wrote {out}")

    # ── Test B: event-day deep dive ─────────────────────────────────────
    # All rupture-tagged posts from 4 chosen dates
    event_dates = [
        ('2023-02-13', 'Replika ERP removal era'),
        ('2024-09-24', 'CharacterAI September update (all-time daily max)'),
        ('2026-02-13', 'GPT-4o sunset in ChatGPT'),
        ('2026-05-09', 'Sonnet 4.5 retirement petition begins circulating'),
    ]
    for d, label in event_dates:
        rows = conn.execute(
            f"""SELECT p.id, p.subreddit, p.title, p.selftext,
                       date(p.created_utc,'unixepoch') AS post_date,
                       GROUP_CONCAT(DISTINCT t.matched_term) AS tags
                FROM post_keyword_tags t
                JOIN posts p ON p.id = t.post_id
                WHERE t.category = 'rupture' AND t.source='post'
                  AND t.post_date = ?
                  AND p.subreddit IN ({sub_ph})
                GROUP BY p.id
                ORDER BY p.created_utc ASC""",
            (d, *T1_T3)
        ).fetchall()
        out = RESULTS / f"robustness_B_event_{d}_2026-05-13.md"
        with open(out, "w") as f:
            f.write(f"# Test B — Event-day deep dive: {d} ({label})\n\n")
            f.write(f"{len(rows)} posts tagged as **rupture** on this date.\n\n")
            f.write("Read them all and answer:\n\n")
            f.write(f"1. Are these posts genuinely about the event we expected ({label})? Or is this date showing a different event, or no coherent event at all?\n")
            f.write("2. If they cluster on a different event, what is it?\n")
            f.write("3. Any posts that don't fit any coherent event narrative (random rupture posts that happen to share a date)?\n\n")
            f.write("Output format:\n\n```\n## Bottom line\n")
            f.write("One sentence: what is this date about?\n\n")
            f.write("## Evidence\n")
            f.write("- Specific post titles or quotes that confirm the event\n")
            f.write("- Sub-cluster breakdown (e.g., which platforms users are reacting to)\n\n")
            f.write("## Off-narrative posts\n")
            f.write("- Posts that don't fit the dominant event\n")
            f.write("```\n\n")
            f.write("---\n\n## Posts\n\n")
            for i, r in enumerate(rows, 1):
                f.write(post_md_entry(i, r, show_tags=True))
        print(f"Wrote {out} ({len(rows)} posts)")

    # ── Test C: subreddit character audit ──────────────────────────────
    subs = ['CharacterAI', 'replika', 'MyBoyfriendIsAI', 'BeyondThePromptAI', 'Character_AI_Recovery']
    for sub in subs:
        # 20 tagged + 20 untagged posts, recent
        tagged = conn.execute(
            """SELECT p.id, p.subreddit, p.title, p.selftext,
                      date(p.created_utc,'unixepoch') AS post_date,
                      GROUP_CONCAT(DISTINCT t.category || ':' || t.matched_term) AS tags
               FROM post_keyword_tags t
               JOIN posts p ON p.id = t.post_id
               WHERE t.source='post' AND p.subreddit = ?
               GROUP BY p.id
               ORDER BY RANDOM()
               LIMIT 20""",
            (sub,)
        ).fetchall()
        untagged = conn.execute(
            """SELECT p.id, p.subreddit, p.title, p.selftext,
                      date(p.created_utc,'unixepoch') AS post_date,
                      '' AS tags
               FROM posts p
               LEFT JOIN (SELECT DISTINCT post_id FROM post_keyword_tags WHERE source='post') tt
                 ON tt.post_id = p.id
               WHERE p.subreddit = ?
                 AND tt.post_id IS NULL
                 AND p.created_utc > strftime('%s', '2025-01-01')
               ORDER BY RANDOM()
               LIMIT 20""",
            (sub,)
        ).fetchall()
        # Interleave for fairness
        combined = []
        for i in range(20):
            combined.append(tagged[i] if i < len(tagged) else None)
            combined.append(untagged[i] if i < len(untagged) else None)
        combined = [r for r in combined if r is not None]
        out = RESULTS / f"robustness_C_sub_{sub}_2026-05-13.md"
        with open(out, "w") as f:
            f.write(f"# Test C — Subreddit character: r/{sub}\n\n")
            f.write(f"{len(combined)} posts from r/{sub}, mixed (tagged and untagged, interleaved).\n\n")
            f.write("Read all posts. Answer:\n\n")
            f.write(f"1. **What is r/{sub} actually about?** Characterize the community's content in 2-3 sentences.\n")
            f.write("2. **Tagging quality**: of the 'Current keyword tags' shown, do they match the post's content? Any obviously wrong tags?\n")
            f.write("3. **Missed content**: of the untagged posts, how many SHOULD be theme-tagged but aren't? Which themes are missed most?\n")
            f.write("4. **Mismatch between sub and tagging**: is our keyword set well-tuned for this sub, or does it systematically over/under-tag specific themes here?\n\n")
            f.write("Output format:\n\n```\n## Sub character\n2-3 sentences.\n\n")
            f.write("## Tagging quality\nPost #: correct/wrong, brief reason.\n\n")
            f.write("## Missed content\nPost #: should be tagged as X, why our keyword set missed it.\n\n")
            f.write("## Sub vs tagging mismatch\nOne paragraph: where is the keyword set tuned right or wrong for this sub?\n```\n\n")
            f.write("---\n\n## Posts\n\n")
            for i, r in enumerate(combined, 1):
                f.write(post_md_entry(i, r, show_tags=True))
        print(f"Wrote {out}")

    conn.close()


if __name__ == "__main__":
    main()
