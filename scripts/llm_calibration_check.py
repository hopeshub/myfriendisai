#!/usr/bin/env python3
"""Independent calibration check for LLM verdicts.

After the Haiku backfill runs, this script samples LLM verdicts (both TP and
FP) and writes them to a Markdown file that an independent CC agent can
classify. The agent's verdicts are then compared against the LLM's to
compute inter-rater agreement.

Three subcommands:

  build [--n-fp 100] [--n-tp 50] [--model claude-haiku-4-5-20251001]
      Sample LLM verdicts (stratified across themes) and build a sample
      file at analysis/keyword_pipeline/results/calibration_<date>.md.

  parse --results-file <path>
      Parse an agent's per-line TP/FP verdicts from a results file and
      compute agreement vs the LLM, with per-theme breakdown.

  decide [--threshold 0.85]
      Look at the parse output and recommend whether to flip the chart
      default to count_llm_verified.

Usage:
  .venv/bin/python scripts/llm_calibration_check.py build
  # Then dispatch a CC agent to classify the file
  .venv/bin/python scripts/llm_calibration_check.py parse --results-file <path>
  .venv/bin/python scripts/llm_calibration_check.py decide
"""

import argparse
import json
import re
import sqlite3
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

DB_PATH = PROJECT_ROOT / "data" / "tracker.db"
RESULTS_DIR = PROJECT_ROOT / "analysis" / "keyword_pipeline" / "results"


def truncate(s, n):
    s = (s or "").strip()
    return s if len(s) <= n else s[:n] + "..."


def cmd_build(args):
    """Build a calibration sample file: N_FP per theme + N_TP per theme."""
    conn = sqlite3.connect(DB_PATH, timeout=60.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA busy_timeout = 60000")

    THEMES = ['rupture', 'addiction', 'romance', 'sexual_erp', 'consciousness', 'therapy']
    sample_rows = []  # (idx_in_file, tag_type, tag_id, theme, keyword, llm_verdict, llm_reason)

    for theme in THEMES:
        for verdict_kind, n in [('FP', args.n_fp), ('TP', args.n_tp)]:
            # Posts
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
                (args.model, theme, verdict_kind, n // 2),
            ).fetchall()
            for r in rows:
                sample_rows.append({
                    "tag_type": r["tag_type"],
                    "post_id": r["post_id"],
                    "comment_id": r["comment_id"],
                    "theme": r["theme"],
                    "keyword": r["keyword"],
                    "llm_verdict": r["verdict"],
                    "llm_reason": r["reason"],
                    "subreddit": r["comment_sub"] or r["post_sub"],
                    "title": r["post_title"],
                    "post_body": r["post_body"],
                    "comment_body": r["comment_body"],
                })
    conn.close()

    if not sample_rows:
        print("ERROR: no LLM verdicts found. Has the backfill produced anything yet?", file=sys.stderr)
        sys.exit(1)

    today = date.today().isoformat()
    sample_path = RESULTS_DIR / f"calibration_{today}.md"
    ground_path = RESULTS_DIR / f"calibration_{today}_llm_truth.json"

    # Shuffle so verdict order doesn't reveal LLM's label
    import random
    random.seed(20260514)
    random.shuffle(sample_rows)

    with open(sample_path, "w") as f:
        f.write(f"# Calibration sample — {today}\n\n")
        f.write(f"{len(sample_rows)} items where the production LLM produced a verdict.\n\n")
        f.write("**You are the independent classifier.** Read each item and decide whether the keyword match is a true positive for the theme under topical reading. The LLM's verdict is hidden from you.\n\n")
        f.write("**Rubric:** under topical reading, a match is TP if the item is thematically about the theme in a companion-community context. A match is FP if any of these apply: polysemy (different sense of the word), negation, sarcasm, quoted speech (AI roleplay output / quoting another user), off-topic content even in on-topic thread, metaphorical use without theme content.\n\n")
        f.write("**Output format** — one line per item:\n\n```\n1. TP\n2. FP\n3. TP\n...\n```\n\n")
        f.write(f"Write results to: `{sample_path.stem}_results.txt` in the same directory.\n\n")
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

    # Save the LLM ground truth (NOT included in agent prompt)
    with open(ground_path, "w") as f:
        for i, item in enumerate(sample_rows, 1):
            f.write(json.dumps({
                "idx": i,
                "tag_type": item["tag_type"],
                "tag_id": item["comment_id"] or item["post_id"],
                "theme": item["theme"],
                "keyword": item["keyword"],
                "llm_verdict": item["llm_verdict"],
            }) + "\n")

    print(f"Wrote {sample_path}")
    print(f"Wrote {ground_path}")
    print(f"Total items: {len(sample_rows)}")
    print("\nNext: dispatch a CC agent to read the sample file and write per-line verdicts.")
    print(f"After agent completes, parse with: python {Path(__file__).name} parse --results-file <path>")


RESULT_LINE_RE = re.compile(r"^\s*(\d+)\s*[\.\)]?\s*(TP|FP)\b", re.IGNORECASE)


def cmd_parse(args):
    """Parse agent verdicts and compute agreement with LLM."""
    results_path = Path(args.results_file)
    if not results_path.exists():
        print(f"ERROR: results file not found: {results_path}", file=sys.stderr)
        sys.exit(1)

    # Find the matching ground truth file
    ground_path = results_path.parent / results_path.name.replace("_results.txt", "_llm_truth.json")
    if not ground_path.exists():
        # Try a date-based fallback
        date_match = re.search(r"calibration_(\d{4}-\d{2}-\d{2})", results_path.name)
        if date_match:
            ground_path = RESULTS_DIR / f"calibration_{date_match.group(1)}_llm_truth.json"
    if not ground_path.exists():
        print(f"ERROR: ground truth file not found: {ground_path}", file=sys.stderr)
        sys.exit(1)

    # Load LLM verdicts
    ground = {}
    with open(ground_path) as f:
        for line in f:
            if not line.strip():
                continue
            entry = json.loads(line)
            ground[entry["idx"]] = entry

    # Parse agent verdicts
    agent_verdicts = {}
    with open(results_path) as f:
        for line in f:
            m = RESULT_LINE_RE.match(line)
            if m:
                agent_verdicts[int(m.group(1))] = m.group(2).upper()

    # Compute agreement
    overall_total = 0
    overall_agree = 0
    per_theme_total = defaultdict(int)
    per_theme_agree = defaultdict(int)
    confusion = defaultdict(int)  # (llm_v, agent_v) -> count
    disagreements = []

    for idx, agent_v in agent_verdicts.items():
        if idx not in ground:
            continue
        llm_v = ground[idx]["llm_verdict"]
        theme = ground[idx]["theme"]
        overall_total += 1
        per_theme_total[theme] += 1
        if llm_v == agent_v:
            overall_agree += 1
            per_theme_agree[theme] += 1
        else:
            disagreements.append({
                "idx": idx, "theme": theme,
                "keyword": ground[idx]["keyword"],
                "llm_verdict": llm_v, "agent_verdict": agent_v,
            })
        confusion[(llm_v, agent_v)] += 1

    print(f"\n=== Calibration result ===")
    print(f"Overall agreement: {overall_agree}/{overall_total} = {overall_agree/overall_total:.1%}\n")

    print("Per-theme agreement:")
    for theme in sorted(per_theme_total.keys()):
        a = per_theme_agree[theme]
        t = per_theme_total[theme]
        print(f"  {theme:14s}  {a:3d}/{t:3d} = {a/t:.1%}")

    print("\nConfusion matrix (LLM verdict × agent verdict):")
    print(f"            agent=TP   agent=FP")
    for llm_v in ("TP", "FP"):
        print(f"  llm={llm_v}    {confusion[(llm_v, 'TP')]:>7d}    {confusion[(llm_v, 'FP')]:>7d}")

    # Direction-specific: when LLM said FP, how often was agent TP?
    # (this is the most important number — false rejections)
    llm_fp_total = sum(confusion[("FP", v)] for v in ("TP", "FP"))
    agent_says_tp_on_llm_fp = confusion[("FP", "TP")]
    false_reject_rate = agent_says_tp_on_llm_fp / llm_fp_total if llm_fp_total else 0
    print(f"\nFalse-rejection rate (LLM said FP but agent said TP): {false_reject_rate:.1%}")
    print("(High false-rejection rate means LLM is too strict.)\n")

    # Write parsed result for decide command
    out = {
        "overall_agreement": overall_agree / overall_total if overall_total else None,
        "overall_total": overall_total,
        "per_theme": {
            theme: {"agree": per_theme_agree[theme], "total": per_theme_total[theme]}
            for theme in per_theme_total
        },
        "confusion": {f"{k[0]}|{k[1]}": v for k, v in confusion.items()},
        "false_reject_rate": false_reject_rate,
        "n_disagreements": len(disagreements),
        "disagreements": disagreements[:20],
    }
    decision_path = results_path.parent / f"calibration_decision_{date.today().isoformat()}.json"
    decision_path.write_text(json.dumps(out, indent=2))
    print(f"Wrote {decision_path}")


def cmd_decide(args):
    """Read the most recent calibration decision file and recommend an action."""
    today = date.today().isoformat()
    decision_path = RESULTS_DIR / f"calibration_decision_{today}.json"
    if not decision_path.exists():
        candidates = sorted(RESULTS_DIR.glob("calibration_decision_*.json"))
        if not candidates:
            print("ERROR: no calibration_decision_*.json file found.", file=sys.stderr)
            sys.exit(1)
        decision_path = candidates[-1]
        print(f"Using most recent: {decision_path}")
    data = json.loads(decision_path.read_text())
    agreement = data["overall_agreement"]
    false_reject = data["false_reject_rate"]

    print(f"Overall agreement:     {agreement:.1%}")
    print(f"False-rejection rate:  {false_reject:.1%}")
    print(f"Threshold:             {args.threshold:.0%}")

    if agreement >= args.threshold and false_reject < 0.2:
        print(f"\nRECOMMENDATION: FLIP chart default to count_llm_verified.")
        print("Agreement is above threshold and the LLM is not over-rejecting.")
        sys.exit(0)
    elif agreement >= 0.65:
        print(f"\nRECOMMENDATION: DEFER. Agreement is plausible but below threshold.")
        print("Document the disagreement zones and reconsider after prompt tuning.")
        sys.exit(2)
    else:
        print(f"\nRECOMMENDATION: BLOCK. Agreement is too low to ship.")
        print("Tune the LLM prompt or revisit the classification rubric.")
        sys.exit(3)


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)

    b = sub.add_parser("build")
    b.add_argument("--n-fp", type=int, default=100, help="Per-theme FP sample count")
    b.add_argument("--n-tp", type=int, default=50, help="Per-theme TP sample count")
    b.add_argument("--model", default="claude-haiku-4-5-20251001")
    b.set_defaults(func=cmd_build)

    pa = sub.add_parser("parse")
    pa.add_argument("--results-file", required=True)
    pa.set_defaults(func=cmd_parse)

    de = sub.add_parser("decide")
    de.add_argument("--threshold", type=float, default=0.85)
    de.set_defaults(func=cmd_decide)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
