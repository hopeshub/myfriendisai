#!/usr/bin/env python3
"""Build a stratified random sample for the comprehensiveness/recall audit.

Strategy: combine uniform-random sample (across all T1-T3) with targeted
oversamples from subs where rare themes (consciousness, therapy) should
appear. Output is a Markdown prompt file an agent reads to classify each
post for all 6 themes.

Output: results/recall_audit_sample_YYYY-MM-DD.md
"""

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

# Stratified composition
STRATA = {
    "random_t1_t3": (200, None),           # 200 random from full T1-T3
    "r_mybfisai": (40, "MyBoyfriendIsAI"), # romance-rich
    "r_beyondthepromptai": (40, "BeyondThePromptAI"),  # consciousness-rich
    "r_character_ai_recovery": (40, "Character_AI_Recovery"),  # addiction-rich
    "r_replika": (40, "replika"),          # general companion + therapy
    "r_chatgptcomplaints": (40, "ChatGPTcomplaints"),  # rupture-rich
}
RANDOM_SEED = 20260513


def main():
    random.seed(RANDOM_SEED)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    T1_T3 = [c["subreddit"] for c in load_keyword_communities()]
    sub_ph = ",".join("?" * len(T1_T3))

    all_posts = []
    seen_ids = set()
    for stratum_name, (n, sub) in STRATA.items():
        if sub is None:
            rows = conn.execute(
                f"""SELECT id, subreddit, title, selftext,
                           date(created_utc, 'unixepoch') AS post_date,
                           created_utc
                    FROM posts
                    WHERE subreddit IN ({sub_ph})
                      AND created_utc IS NOT NULL
                    ORDER BY RANDOM()
                    LIMIT ?""",
                (*T1_T3, n * 3)  # Over-pull then de-dup
            ).fetchall()
        else:
            rows = conn.execute(
                """SELECT id, subreddit, title, selftext,
                          date(created_utc, 'unixepoch') AS post_date,
                          created_utc
                   FROM posts
                   WHERE subreddit = ? AND created_utc IS NOT NULL
                   ORDER BY RANDOM()
                   LIMIT ?""",
                (sub, n * 3)
            ).fetchall()
        picked = 0
        for r in rows:
            if r["id"] in seen_ids:
                continue
            seen_ids.add(r["id"])
            all_posts.append((stratum_name, dict(r)))
            picked += 1
            if picked >= n:
                break

    # Look up current tag status for each post — used in post-processing to
    # compute recall (don't reveal to the classifier).
    placeholders = ",".join("?" * len(all_posts))
    if all_posts:
        tag_rows = conn.execute(
            f"""SELECT post_id, category
                FROM post_keyword_tags
                WHERE source='post' AND post_id IN ({placeholders})""",
            [p[1]["id"] for p in all_posts]
        ).fetchall()
        tag_lookup: dict[str, set[str]] = {}
        for pid, cat in tag_rows:
            tag_lookup.setdefault(pid, set()).add(cat)
    else:
        tag_lookup = {}

    conn.close()

    out = RESULTS / f"recall_audit_sample_{date.today().isoformat()}.md"
    tag_out = RESULTS / f"recall_audit_tags_{date.today().isoformat()}.tsv"

    # Write a separate tag-status TSV (NOT included in agent prompt)
    with open(tag_out, "w") as f:
        f.write("post_id\tstratum\tsubreddit\tcurrent_tags\n")
        for stratum, post in all_posts:
            tags = ",".join(sorted(tag_lookup.get(post["id"], set()))) or "(none)"
            f.write(f"{post['id']}\t{stratum}\tr/{post['subreddit']}\t{tags}\n")

    # Write the agent prompt file (no tag information leaked)
    with open(out, "w") as f:
        f.write("# Comprehensiveness Audit — Post Sample\n\n")
        f.write(f"**Date:** {date.today().isoformat()}\n")
        f.write(f"**Sample size:** {len(all_posts)} posts (stratified)\n")
        f.write(f"**Strata:** {', '.join(STRATA.keys())}\n\n")
        f.write("## Task\n\n")
        f.write("For each post, classify whether it thematically belongs to each of six themes ")
        f.write("under the topical reading. A post can belong to MULTIPLE themes. A post can also ")
        f.write("belong to NONE.\n\n")
        f.write("**Themes:**\n\n")
        f.write("- **rupture** — loss, degradation, destruction of an AI companion due to platform updates, model changes, filters, personality resets, memory wipes, feature removal, shutdown. Grief/mourning/complaint/defense about these changes count.\n")
        f.write("- **addiction** — compulsive AI use, dependency, inability to stop, withdrawal, attempts to quit/recover. First-person framing about the author's own dependency.\n")
        f.write("- **romance** — romantic attachment with an AI (dating, love, relationship milestones, partnership, heartbreak, defense of AI romance). First-person framing about an AI partner.\n")
        f.write("- **sexual_erp** — sexual/erotic interactions with AI, ERP, NSFW chat, kink, erotic roleplay, sexting. First-person references to doing/wanting/losing access.\n")
        f.write("- **consciousness** — AI awareness, sentience, personhood, inner experience, soul. Author engages the question that their AI has (or may have) something like consciousness.\n")
        f.write("- **therapy** — using AI for mental health support, therapist substitute/supplement, emotional support, coping with anxiety/depression/loneliness/grief.\n\n")
        f.write("**When in doubt, classify YES.** The companion-community context already establishes thematic relevance. Reserve NO for: off-topic non-companion content, bot character card listings with no first-person framing, explicit rejections, pure third-party journalism with no personal stake.\n\n")
        f.write("**Output format** — one line per post:\n\n")
        f.write("```\n")
        f.write("POST <N>: themes=[rupture,romance] OR themes=[NONE]\n")
        f.write("```\n\n")
        f.write("Use exactly the six theme names (lowercase, underscores). Output `themes=[NONE]` if no themes apply. Do not add reasons or commentary — just the classification line per post.\n\n")
        f.write("---\n\n")
        f.write("## Posts\n\n")

        for i, (stratum, post) in enumerate(all_posts, 1):
            f.write(f"### POST {i}\n")
            f.write(f"**ID:** {post['id']}  **Subreddit:** r/{post['subreddit']}  **Date:** {post['post_date']}\n\n")
            f.write(f"**Title:** {post['title'] or '(no title)'}\n\n")
            body = (post['selftext'] or '').strip()
            if body:
                if len(body) > 600:
                    body = body[:600] + "..."
                f.write(f"**Body:** {body}\n\n")
            else:
                f.write("**Body:** (empty)\n\n")
            f.write("---\n\n")

    print(f"Sample posts: {len(all_posts)}")
    print(f"Prompt file: {out}")
    print(f"Tag-status TSV: {tag_out}")
    with open(out) as f:
        n_lines = sum(1 for _ in f)
    print(f"Lines: {n_lines}")
    # Stratum breakdown
    from collections import Counter
    by_stratum = Counter(s for s, _ in all_posts)
    for stratum, n in by_stratum.items():
        print(f"  {stratum}: {n}")


if __name__ == "__main__":
    main()
