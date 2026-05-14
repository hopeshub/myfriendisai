#!/usr/bin/env python3
"""Build a larger calibration sample (n=900) excluding items in the
original 2026-05-14 sample. Used to make a paired Haiku-vs-Sonnet
comparison statistically robust.

Stratified: 100 FP + 50 TP per theme. Random ordering, fresh seed.
"""

import json
import random
import sqlite3
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

DB_PATH = PROJECT_ROOT / "data" / "tracker.db"
RESULTS = PROJECT_ROOT / "analysis" / "keyword_pipeline" / "results"
DATE = "2026-05-14"
SEED = 20260515  # different from original sample (which used 20260514)
THEMES = ['rupture', 'addiction', 'romance', 'sexual_erp', 'consciousness', 'therapy']

# Exclude IDs already in original sample
ORIG_TRUTH = RESULTS / f"calibration_{DATE}_llm_truth.json"


def truncate(s, n):
    s = (s or "").strip()
    return s if len(s) <= n else s[:n] + "..."


def main():
    random.seed(SEED)
    conn = sqlite3.connect(DB_PATH, timeout=60.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA busy_timeout = 60000")

    exclude_ids = set()
    if ORIG_TRUTH.exists():
        with open(ORIG_TRUTH) as f:
            for line in f:
                if line.strip():
                    e = json.loads(line)
                    exclude_ids.add(e["tag_id"])

    print(f"Excluding {len(exclude_ids)} items already in original sample.\n")

    sample_rows = []
    model = "claude-haiku-4-5-20251001"

    for theme in THEMES:
        for verdict_kind, target in [("FP", 100), ("TP", 50)]:
            rows = conn.execute(
                """SELECT c.tag_type, c.post_id, c.comment_id, c.theme,
                          c.keyword, c.verdict, c.reason,
                          p.subreddit AS post_sub, p.title AS post_title,
                          p.selftext AS post_body,
                          cm.body AS comment_body, cm.subreddit AS comment_sub,
                          cm.id AS cm_id
                   FROM llm_classifications c
                   JOIN posts p ON p.id = c.post_id
                   LEFT JOIN comments cm ON cm.id = c.comment_id
                   WHERE c.model=? AND c.theme=? AND c.verdict=?
                   ORDER BY RANDOM()
                   LIMIT ?""",
                (model, theme, verdict_kind, target * 3),  # over-pull
            ).fetchall()
            picked = 0
            for r in rows:
                tag_id = r["comment_id"] or r["post_id"]
                if tag_id in exclude_ids:
                    continue
                sample_rows.append({
                    "tag_type": r["tag_type"],
                    "post_id": r["post_id"],
                    "comment_id": r["comment_id"],
                    "theme": r["theme"],
                    "keyword": r["keyword"],
                    "llm_verdict_v1": r["verdict"],
                    "subreddit": r["comment_sub"] or r["post_sub"],
                    "title": r["post_title"],
                    "post_body": r["post_body"],
                    "comment_body": r["comment_body"],
                })
                exclude_ids.add(tag_id)  # avoid dupes within new sample
                picked += 1
                if picked >= target:
                    break

    conn.close()

    # Shuffle so verdict order doesn't reveal labels
    random.shuffle(sample_rows)
    print(f"Built sample with {len(sample_rows)} items.\n")

    sample_path = RESULTS / f"calibration_v2_{DATE}.md"
    truth_path = RESULTS / f"calibration_v2_{DATE}_llm_truth.json"

    with open(sample_path, "w") as f:
        f.write(f"# Calibration v2 sample — {DATE} (n=900)\n\n")
        f.write("Larger paired-comparison sample for Haiku-vs-Sonnet decision.\n\n")
        f.write("You are the independent classifier. For each item, decide TP or FP under the **topical-reading** rubric.\n\n")
        f.write("Rubric: a match is **TP** if the {item_type} is thematically about the theme in a companion-community context. Use **FP** for: polysemy (different sense of the word), explicit negation by the author, sarcasm/irony, verbatim quoted speech (AI roleplay output / quoting other users) not representing author stake, off-topic content even in on-topic thread, metaphorical use without theme content, mod-template boilerplate, platform-dev promotional content.\n\n")
        f.write("**When in doubt under topical reading, default TP.** A companion-sub post or comment that touches the theme — even briefly, indirectly, via metaphor, humor, defense, or first-person stream-of-consciousness — counts as TP.\n\n")
        f.write("**Output format** — one line per item:\n\n```\n1. TP\n2. FP\n...\n900. TP\n```\n\n")
        f.write(f"Write your output using the Write tool to: `{sample_path.parent}/{sample_path.stem}_results.txt`\n\n")
        f.write("After writing, respond with a single confirmation line.\n\n")
        f.write("---\n\n")
        for i, item in enumerate(sample_rows, 1):
            f.write(f"### {i}\n")
            f.write(f"**Theme:** {item['theme']}  **Keyword:** `{item['keyword']}`  ")
            f.write(f"**Surface:** {item['tag_type']}  **r/{item['subreddit']}**\n\n")
            if item['tag_type'] == 'comment':
                f.write(f"**Parent post title:** {item['title'] or '(no title)'}\n\n")
                f.write(f"**Parent body:** {truncate(item['post_body'], 200)}\n\n")
                f.write(f"**Comment:** {truncate(item['comment_body'], 500)}\n\n")
            else:
                f.write(f"**Title:** {item['title'] or '(no title)'}\n\n")
                f.write(f"**Body:** {truncate(item['post_body'], 500)}\n\n")
            f.write("---\n\n")

    with open(truth_path, "w") as f:
        for i, item in enumerate(sample_rows, 1):
            f.write(json.dumps({
                "idx": i,
                "tag_type": item["tag_type"],
                "tag_id": item["comment_id"] or item["post_id"],
                "theme": item["theme"],
                "keyword": item["keyword"],
                "llm_verdict_v1": item["llm_verdict_v1"],
            }) + "\n")

    print(f"Wrote {sample_path}")
    print(f"Wrote {truth_path}")


if __name__ == "__main__":
    main()
