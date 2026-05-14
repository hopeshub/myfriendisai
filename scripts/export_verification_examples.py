#!/usr/bin/env python3
"""Pick a small set of compelling LLM verdicts to surface on the About page.

Strategy: from llm_classifications, pick the highest-impact examples
— FPs where the LLM caught what pure keyword matching couldn't (negation,
sarcasm, polysemy, quoted speech) and TPs where the LLM confirmed
a noisy keyword's match in unambiguous context.

Output: data/verification_examples.json + copy to web/data/.
"""

import json
import sqlite3
import sys
from collections import defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
DB_PATH = PROJECT_ROOT / "data" / "tracker.db"
DATA_DIR = PROJECT_ROOT / "data"
WEB_DATA_DIR = PROJECT_ROOT / "web" / "data"

# Target ~2 FPs and ~1 TP per theme. The visual story is "look how LLM
# catches FPs that would otherwise distort the trend lines."
N_FP_PER_THEME = 2
N_TP_PER_THEME = 1
MAX_BODY_CHARS = 360

# Theme display labels
THEME_LABELS = {
    "rupture": "Rupture",
    "addiction": "Addiction",
    "romance": "Romance",
    "sexual_erp": "Sex / ERP",
    "consciousness": "Consciousness",
    "therapy": "Therapy",
}

# Prefer FP examples that match these structural failure patterns
# (the LLM reason often mentions one of these — substring match used as a hint)
COMPELLING_FP_PATTERNS = [
    "negation",
    "sarcasm",
    "quoted",
    "roleplay output",
    "human",  # "had sex with a real person" / "human partner"
    "marketing",
    "platform-dev",
    "metaphor",
    "feature-label",
    "style descriptor",
    "preachy",
    "literal",
    "polysem",
]


def truncate(s, n):
    s = (s or "").strip()
    return s if len(s) <= n else s[:n] + "..."


def fp_score(reason: str) -> int:
    """Higher score = more compelling FP example to surface."""
    if not reason:
        return 0
    r = reason.lower()
    return sum(1 for p in COMPELLING_FP_PATTERNS if p in r)


def main():
    conn = sqlite3.connect(DB_PATH, timeout=60.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA busy_timeout = 60000")

    examples_by_theme = defaultdict(lambda: {"fp": [], "tp": []})

    for theme in THEME_LABELS:
        # Get FP candidates with reasons (post + comment)
        fp_rows = conn.execute(
            """SELECT c.tag_type, c.post_id, c.comment_id, c.theme,
                      c.keyword, c.verdict, c.reason,
                      p.subreddit AS post_sub, p.title AS post_title,
                      p.selftext AS post_body,
                      cm.body AS comment_body, cm.subreddit AS comment_sub
                 FROM llm_classifications c
                 JOIN posts p ON p.id = c.post_id
                 LEFT JOIN comments cm ON cm.id = c.comment_id
                 WHERE c.model='claude-haiku-4-5-20251001'
                   AND c.theme=? AND c.verdict='FP'
                   AND c.reason IS NOT NULL AND LENGTH(c.reason) > 30
                 ORDER BY RANDOM()
                 LIMIT 200""",
            (theme,),
        ).fetchall()
        # Score and pick top by FP compellingness
        scored = sorted(
            ((fp_score(r["reason"]), r) for r in fp_rows),
            key=lambda x: -x[0],
        )[:N_FP_PER_THEME]
        for _, r in scored:
            examples_by_theme[theme]["fp"].append(build_example(r))

        # Get TP candidates — random pick
        tp_rows = conn.execute(
            """SELECT c.tag_type, c.post_id, c.comment_id, c.theme,
                      c.keyword, c.verdict, c.reason,
                      p.subreddit AS post_sub, p.title AS post_title,
                      p.selftext AS post_body,
                      cm.body AS comment_body, cm.subreddit AS comment_sub
                 FROM llm_classifications c
                 JOIN posts p ON p.id = c.post_id
                 LEFT JOIN comments cm ON cm.id = c.comment_id
                 WHERE c.model='claude-haiku-4-5-20251001'
                   AND c.theme=? AND c.verdict='TP'
                   AND c.reason IS NOT NULL AND LENGTH(c.reason) > 30
                 ORDER BY RANDOM()
                 LIMIT ?""",
            (theme, N_TP_PER_THEME),
        ).fetchall()
        for r in tp_rows:
            examples_by_theme[theme]["tp"].append(build_example(r))

    conn.close()

    # Build the result
    output = {
        "generated_at": __import__("datetime").date.today().isoformat(),
        "themes": {
            theme: {
                "label": THEME_LABELS[theme],
                "fp": examples_by_theme[theme]["fp"],
                "tp": examples_by_theme[theme]["tp"],
            }
            for theme in THEME_LABELS
            if examples_by_theme[theme]["fp"] or examples_by_theme[theme]["tp"]
        },
    }

    out_path = DATA_DIR / "verification_examples.json"
    out_path.write_text(json.dumps(output, indent=2))
    web_path = WEB_DATA_DIR / "verification_examples.json"
    web_path.write_text(json.dumps(output, indent=2))
    n_themes = len(output["themes"])
    n_total = sum(len(v["fp"]) + len(v["tp"]) for v in output["themes"].values())
    print(f"Wrote {out_path} ({n_themes} themes, {n_total} examples)")
    print(f"Wrote {web_path}")


def build_example(r) -> dict:
    is_comment = r["tag_type"] == "comment"
    if is_comment:
        body = r["comment_body"]
        sub = r["comment_sub"] or r["post_sub"]
    else:
        body = r["post_body"]
        sub = r["post_sub"]
    return {
        "subreddit": sub,
        "title": r["post_title"] or "",
        "body": truncate(body, MAX_BODY_CHARS),
        "keyword": r["keyword"],
        "tag_type": r["tag_type"],
        "verdict": r["verdict"],
        "llm_reason": (r["reason"] or "")[:200],
    }


if __name__ == "__main__":
    main()
