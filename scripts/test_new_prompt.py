#!/usr/bin/env python3
"""Re-run the 270-item calibration sample under the current LLMClassifier
prompt, compare against the agent gold standard. Does NOT write to DB —
just measures agreement.

Usage:
  set -a && source .env && set +a
  .venv/bin/python scripts/test_new_prompt.py
"""

import json
import re
import sqlite3
import sys
from collections import defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import argparse
from src.llm_classifier import LLMClassifier

DB_PATH = PROJECT_ROOT / "data" / "tracker.db"
RESULTS = PROJECT_ROOT / "analysis" / "keyword_pipeline" / "results"
DATE = "2026-05-14"

LLM_TRUTH = RESULTS / f"calibration_{DATE}_llm_truth.json"
AGENT_RESULTS = RESULTS / f"calibration_{DATE}_results.txt"

LLM_TRUTH_V2 = RESULTS / f"calibration_v2_{DATE}_llm_truth.json"
AGENT_RESULTS_V2 = RESULTS / f"calibration_v2_{DATE}_results.txt"  # may not exist yet (agents running)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="claude-haiku-4-5-20251001")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--v2", action="store_true", help="Use n=900 v2 sample")
    parser.add_argument("--no-agent-compare", action="store_true",
                        help="Skip agent-comparison (for v2 where agents may not be done)")
    args = parser.parse_args()

    truth_path = LLM_TRUTH_V2 if args.v2 else LLM_TRUTH
    agent_results_path = AGENT_RESULTS_V2 if args.v2 else AGENT_RESULTS

    # Load ground truth (idx → item metadata)
    truth = {}
    with open(truth_path) as f:
        for line in f:
            if not line.strip():
                continue
            e = json.loads(line)
            truth[e["idx"]] = e

    # Load agent verdicts (may not exist yet for v2 — skip-compare mode)
    line_re = re.compile(r"^\s*(\d+)\s*[\.\)]?\s*(TP|FP)\b", re.IGNORECASE)
    agent = {}
    if not args.no_agent_compare and agent_results_path.exists():
        with open(agent_results_path) as f:
            for line in f:
                m = line_re.match(line)
                if m:
                    agent[int(m.group(1))] = m.group(2).upper()

    print(f"Loaded {len(truth)} ground-truth items, {len(agent)} agent verdicts.\n")

    conn = sqlite3.connect(DB_PATH, timeout=60.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA busy_timeout = 60000")

    clf = LLMClassifier(model=args.model)
    print(f"Model: {args.model}\n")
    new_verdicts = {}
    agree = total = 0
    per_theme = defaultdict(lambda: {"agree": 0, "total": 0})
    confusion = defaultdict(int)
    false_reject = 0  # new=FP, agent=TP
    false_keep = 0  # new=TP, agent=FP

    indices = sorted(truth.keys())
    if args.limit:
        indices = indices[:args.limit]

    # In skip-compare mode, just classify and save without comparing.
    # Save INCREMENTALLY (JSONL) so a crash doesn't lose work.
    classify_only = args.no_agent_compare or not agent
    per_item_results = []
    safe_model = args.model.replace("/", "_")
    sample_tag = "v2" if args.v2 else "v1"
    jsonl_path = RESULTS / f"llm_verdicts_{sample_tag}_{safe_model}_{DATE}.jsonl"
    # Resume: load already-classified indices
    done_idx = set()
    if jsonl_path.exists():
        with open(jsonl_path) as f:
            for line in f:
                if line.strip():
                    try:
                        done_idx.add(json.loads(line)["idx"])
                    except Exception:
                        pass
        print(f"Resuming: {len(done_idx)} already classified, will skip.\n")
    jsonl_out = open(jsonl_path, "a")

    for idx in indices:
        if idx in done_idx:
            continue
        if not classify_only and idx not in agent:
            continue
        e = truth[idx]
        # Fetch item from DB
        if e["tag_type"] == "post":
            row = conn.execute(
                "SELECT subreddit, title, selftext FROM posts WHERE id=?",
                (e["tag_id"],),
            ).fetchone()
            if not row:
                continue
            v = clf.classify(
                title=row["title"] or "", body=row["selftext"] or "",
                theme=e["theme"], keyword=e["keyword"],
                subreddit=row["subreddit"], is_comment=False,
            )
        else:
            row = conn.execute(
                """SELECT c.body, c.subreddit, p.title, p.selftext
                   FROM comments c JOIN posts p ON p.id=c.post_id
                   WHERE c.id=?""",
                (e["tag_id"],),
            ).fetchone()
            if not row:
                continue
            v = clf.classify(
                title="", body=row["body"] or "",
                theme=e["theme"], keyword=e["keyword"],
                subreddit=row["subreddit"], is_comment=True,
                parent_title=row["title"], parent_body=row["selftext"],
            )
        new_v = "TP" if v.verdict in ("TP", "AMBIGUOUS") else "FP"
        new_verdicts[idx] = (new_v, v.verdict, v.reason)
        item_record = {
            "idx": idx, "theme": e["theme"], "keyword": e["keyword"],
            "verdict": new_v, "raw_verdict": v.verdict, "reason": v.reason,
        }
        per_item_results.append(item_record)
        # Write JSONL incrementally so crashes don't lose work
        jsonl_out.write(json.dumps(item_record) + "\n")
        jsonl_out.flush()

        if classify_only:
            if len(per_item_results) % 50 == 0:
                print(f"  {len(per_item_results)} done")
            continue

        agent_v = agent[idx]
        total += 1
        per_theme[e["theme"]]["total"] += 1
        if new_v == agent_v:
            agree += 1
            per_theme[e["theme"]]["agree"] += 1
        confusion[(new_v, agent_v)] += 1
        if new_v == "FP" and agent_v == "TP":
            false_reject += 1
        elif new_v == "TP" and agent_v == "FP":
            false_keep += 1
        if total % 20 == 0:
            print(f"  {total} done, agreement {agree}/{total} = {agree/total:.1%}")

    jsonl_out.close()
    if classify_only:
        all_items = []
        with open(jsonl_path) as f:
            for line in f:
                if line.strip():
                    all_items.append(json.loads(line))
        safe_model_local = args.model.replace("/", "_")
        sample_tag_local = "v2" if args.v2 else "v1"
        items_path = RESULTS / f"llm_verdicts_{sample_tag_local}_{safe_model_local}_{DATE}.json"
        items_path.write_text(json.dumps(all_items, indent=2))
        print(f"\nClassified {len(per_item_results)} this run, total {len(all_items)} in {items_path}")
        conn.close()
        return

    print(f"\n=== Final ===")
    print(f"Overall: {agree}/{total} = {agree/total:.1%}")
    print(f"\nPer-theme:")
    for theme, s in sorted(per_theme.items()):
        print(f"  {theme:14s}  {s['agree']:3d}/{s['total']:3d} = {s['agree']/s['total']:.1%}")
    print(f"\nConfusion (new × agent):")
    print(f"  new=TP, agent=TP: {confusion[('TP','TP')]}")
    print(f"  new=TP, agent=FP: {confusion[('TP','FP')]}")
    print(f"  new=FP, agent=TP: {confusion[('FP','TP')]}")
    print(f"  new=FP, agent=FP: {confusion[('FP','FP')]}")
    new_fp_total = sum(confusion[("FP", v)] for v in ("TP", "FP"))
    new_tp_total = sum(confusion[("TP", v)] for v in ("TP", "FP"))
    if new_fp_total:
        frr = confusion[("FP", "TP")] / new_fp_total
        print(f"\nFalse-rejection rate: {frr:.1%} (new=FP but agent=TP)")
    if new_tp_total:
        fkr = confusion[("TP", "FP")] / new_tp_total
        print(f"False-keep rate:      {fkr:.1%} (new=TP but agent=FP)")

    # Save
    out = {
        "agreement": agree / total if total else None,
        "total": total,
        "false_reject_rate": false_reject / new_fp_total if new_fp_total else 0,
        "false_keep_rate": false_keep / new_tp_total if new_tp_total else 0,
        "per_theme": {
            theme: {"agree": s["agree"], "total": s["total"]}
            for theme, s in per_theme.items()
        },
        "confusion": {f"{k[0]}|{k[1]}": v for k, v in confusion.items()},
    }
    jsonl_out.close()
    if classify_only:
        # Convert JSONL → JSON array for compare script
        all_items = []
        with open(jsonl_path) as f:
            for line in f:
                if line.strip():
                    all_items.append(json.loads(line))
        items_path = RESULTS / f"llm_verdicts_{sample_tag}_{safe_model}_{DATE}.json"
        items_path.write_text(json.dumps(all_items, indent=2))
        print(f"\nClassified {len(per_item_results)} this run, total {len(all_items)} in {items_path}")
        conn.close()
        return
    else:
        save_path = RESULTS / f"calibration_new_prompt_{DATE}_{safe_model}.json"
        save_path.write_text(json.dumps(out, indent=2))
        # Also save per-item
        sample_tag = "v2" if args.v2 else "v1"
        items_path = RESULTS / f"llm_verdicts_{sample_tag}_{safe_model}_{DATE}.json"
        items_path.write_text(json.dumps(per_item_results, indent=2))
        print(f"\nWrote {save_path}")
        print(f"Wrote per-item verdicts to {items_path}")

    conn.close()


if __name__ == "__main__":
    main()
