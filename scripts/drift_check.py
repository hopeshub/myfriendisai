#!/usr/bin/env python3
"""Monthly drift check for keyword precision (cadence updated 2026-05-13;
older quarterly labels remain accepted).

Three subcommands:

  build [--quarter YYYY-MM-or-YYYY-Qn] [--n 50] [--surface post|comment|both] [--keywords k1,k2]
      Pulls N random hits per keyword from the database and writes
      Markdown sample files to analysis/keyword_pipeline/results/.
      Each file is ready to be read by a CC subagent for classification.

  record --files <result_file> [<result_file> ...]
      Parses agent-produced result files (line-per-comment TP/FP format),
      updates analysis/keyword_pipeline/drift_history.json with new
      precision data points, and aggregates per-theme rollups.

  report
      Prints current drift status to stdout: every keyword's latest
      precision, change vs. previous measurement, and an alarm list of
      keywords below 0.70 precision.

Usage example (monthly cadence):

  # 1. Build samples (every month, or on demand)
  .venv/bin/python scripts/drift_check.py build --quarter 2026-06

  # 2. Dispatch agents OR use the LLM classifier directly
  #    Each generated file has its own classification prompt in the header.
  #    Results go to *_results.txt files in the same directory.

  # 3. Parse results back into the tracker
  .venv/bin/python scripts/drift_check.py record \\
      --files analysis/keyword_pipeline/results/drift_2026-06_*_results.txt

  # 4. Inspect current status
  .venv/bin/python scripts/drift_check.py report
"""

import argparse
import json
import re
import sqlite3
import sys
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path
from typing import Optional

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import load_keyword_communities, load_keywords  # noqa: E402

DB_PATH = PROJECT_ROOT / "data" / "tracker.db"
RESULTS_DIR = PROJECT_ROOT / "analysis" / "keyword_pipeline" / "results"
DRIFT_HISTORY = PROJECT_ROOT / "analysis" / "keyword_pipeline" / "drift_history.json"
ALARM_PRECISION = 0.70


# ── BUILD ─────────────────────────────────────────────────────────────────
def truncate(s: Optional[str], n: int) -> str:
    s = (s or "").strip()
    return s if len(s) <= n else s[:n] + "..."


def current_period() -> str:
    """Default period label = YYYY-MM (monthly cadence as of 2026-05-13).
    Older quarterly labels like 2026-Q3 are still accepted via --quarter."""
    today = date.today()
    return today.strftime("%Y-%m")


# Backward-compat alias for older invocations.
current_quarter = current_period


def cmd_build(args):
    quarter = args.quarter or current_period()
    n_per_keyword = args.n
    surface = args.surface
    target_keywords = set(args.keywords.split(",")) if args.keywords else None

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    T1_T3 = [c["subreddit"] for c in load_keyword_communities()]
    sub_ph = ",".join("?" * len(T1_T3))

    # Iterate all keywords from current config
    keyword_categories = load_keywords()
    counter = 0
    for cat in keyword_categories:
        theme = cat["name"]
        for term in cat.get("terms", []):
            if target_keywords and term not in target_keywords:
                continue
            for level in (["post", "comment"] if surface == "both" else [surface]):
                if level == "post":
                    rows = conn.execute(
                        f"""SELECT p.id, p.subreddit, p.title, p.selftext,
                                  date(p.created_utc,'unixepoch') AS post_date
                           FROM post_keyword_tags t
                           JOIN posts p ON p.id = t.post_id
                           WHERE t.matched_term = ? AND t.category = ?
                             AND t.source='post' AND p.subreddit IN ({sub_ph})
                           ORDER BY RANDOM()
                           LIMIT ?""",
                        (term, theme, *T1_T3, n_per_keyword),
                    ).fetchall()
                else:
                    rows = conn.execute(
                        f"""SELECT h.matched_term, h.subreddit, h.post_date,
                                  c.id AS cid, c.body AS comment_body,
                                  p.id AS pid, p.title, p.selftext
                           FROM comment_keyword_hits h
                           JOIN comments c ON c.id = h.comment_id
                           JOIN posts p ON p.id = h.post_id
                           WHERE h.matched_term = ? AND h.category = ?
                             AND h.subreddit IN ({sub_ph})
                           GROUP BY h.comment_id
                           ORDER BY RANDOM()
                           LIMIT ?""",
                        (term, theme, *T1_T3, n_per_keyword),
                    ).fetchall()
                if not rows:
                    continue
                slug = re.sub(r"[^a-zA-Z0-9_-]", "_", term)
                out = RESULTS_DIR / f"drift_{quarter}_{theme}_{slug}_{level}.md"
                write_sample_file(out, rows, term, theme, level, quarter)
                counter += 1
    conn.close()
    print(f"Wrote {counter} sample files under {RESULTS_DIR}")
    print(f"Next step: dispatch agents to classify each file.")
    print(f"  Each agent's output goes to <samefile-name>_results.txt with lines: 'N. TP' or 'N. FP'")
    print(f"  Then run: scripts/drift_check.py record --files {RESULTS_DIR}/drift_{quarter}_*_results.txt")


def write_sample_file(path: Path, rows, term: str, theme: str, level: str, quarter: str):
    is_comment = level == "comment"
    with open(path, "w") as f:
        f.write(f"# Drift check — {quarter} — `{term}` ({theme}) [{level}-level]\n\n")
        f.write(f"{len(rows)} random {level} hits for keyword `{term}` in theme `{theme}`.\n\n")
        f.write(f"**Task:** classify each {'comment' if is_comment else 'post'} as TP or FP under the topical reading.\n\n")
        f.write(f"A TP requires the {'comment' if is_comment else 'post'} to genuinely be about the {theme} theme.\n")
        f.write("FP rules (strict):\n")
        f.write("- Polysemy (keyword used in unrelated sense)\n")
        f.write("- Negation (\"I am NOT in a relationship with it\")\n")
        f.write("- Sarcasm / irony\n")
        f.write("- Quoted speech (quoting another user, or AI roleplay output)\n")
        f.write("- Off-topic content even in on-topic thread\n")
        f.write("- Keyword used metaphorically without theme content\n\n")
        f.write("**Output format** — one line per entry:\n\n")
        f.write("```\n1. TP\n2. FP\n3. TP\n...\n```\n\n")
        f.write("Write your output to a sibling file with name `" + path.stem + "_results.txt`.\n\n")
        f.write("---\n\n")
        for i, r in enumerate(rows, 1):
            if is_comment:
                comment_body = truncate(r["comment_body"], 500) or "(empty)"
                f.write(f"### {i}\n")
                f.write(f"**r/{r['subreddit']}**  **Date:** {r['post_date']}\n\n")
                f.write(f"**Parent title:** {r['title'] or '(no title)'}\n\n")
                f.write(f"**Comment:** {comment_body}\n\n---\n\n")
            else:
                f.write(f"### {i}\n")
                f.write(f"**r/{r['subreddit']}**  **Date:** {r['post_date']}\n\n")
                f.write(f"**Title:** {r['title'] or '(no title)'}\n\n")
                f.write(f"**Body:** {truncate(r['selftext'], 500) or '(empty)'}\n\n---\n\n")


# ── RECORD ────────────────────────────────────────────────────────────────
# Theme is matched against the six known theme names explicitly — a greedy
# [a-z_]+ split is ambiguous for multi-word keyword slugs (e.g.
# drift_2026-06_therapy_for_therapy_post parsed as theme "therapy_for",
# slug "therapy"), which silently skipped every multi-word keyword in the
# 2026-08-08 record run before this fix.
RESULT_FILENAME_RE = re.compile(
    r"drift_(?P<quarter>\d{4}-(?:Q\d|\d{2}))_(?P<theme>therapy|consciousness|addiction|romance|sexual_erp|rupture)_(?P<slug>[A-Za-z0-9_-]+)_(?P<level>post|comment)_results\.txt$"
)
RESULT_LINE_RE = re.compile(r"^\s*(\d+)\s*[\.\)]?\s*(TP|FP)\b", re.IGNORECASE)


def parse_result_file(path: Path) -> Optional[dict]:
    m = RESULT_FILENAME_RE.search(path.name)
    if not m:
        print(f"  SKIP {path.name}: filename doesn't match drift_YYYY-Qn_<theme>_<slug>_<level>_results.txt")
        return None
    text = path.read_text()
    tp = fp = 0
    for line in text.splitlines():
        m2 = RESULT_LINE_RE.match(line)
        if m2:
            verdict = m2.group(2).upper()
            if verdict == "TP":
                tp += 1
            else:
                fp += 1
    n = tp + fp
    if n == 0:
        print(f"  SKIP {path.name}: no TP/FP lines parsed")
        return None
    return {
        "quarter": m.group("quarter"),
        "theme": m.group("theme"),
        "slug": m.group("slug"),
        "level": m.group("level"),
        "n": n,
        "tp": tp,
        "fp": fp,
        "precision": tp / n,
    }


def load_drift_history() -> dict:
    if not DRIFT_HISTORY.exists():
        return {"version": 1, "themes": {}, "keywords": {}}
    return json.loads(DRIFT_HISTORY.read_text())


def slug_to_term(slug: str, theme: str) -> Optional[str]:
    """Reverse the slug to find the original keyword. Slug replaces non-alnum with _."""
    candidates = []
    for cat in load_keywords():
        if cat["name"] == theme:
            for term in cat.get("terms", []):
                if re.sub(r"[^a-zA-Z0-9_-]", "_", term) == slug:
                    return term
                candidates.append(term)
    # Fallback: case-insensitive
    for term in candidates:
        if re.sub(r"[^a-zA-Z0-9_-]", "_", term).lower() == slug.lower():
            return term
    return None


# Theme-level rollups use POOLED aggregation: precision = ΣTP / ΣN across
# every keyword sample file for that theme+level+quarter, rather than a mean
# of per-keyword precisions. Because `build` draws a fixed N per keyword
# (~26/keyword in practice, regardless of that keyword's corpus volume),
# pooling is already ≈ equal-keyword weighting — it is *not* volume-weighted
# toward high-frequency keywords. This matches how the June/July 2026
# theme-level figures quoted in CLAUDE.md §2.3 and the project docs were
# computed by hand, so the recorded numbers stay comparable to those.
def _upsert_theme_entry(history: dict, theme: str, level: str, entry: dict):
    """Append (or replace, keyed on quarter) a theme-level history entry.

    Idempotent: re-running `record` for the same quarter overwrites the
    existing entry for that quarter+level instead of appending a duplicate.
    """
    t = history.setdefault("themes", {}).setdefault(theme, {})
    lvl = t.setdefault(f"{level}_level", {})
    hist = lvl.setdefault("history", [])
    for i, existing in enumerate(hist):
        if existing.get("quarter") == entry.get("quarter"):
            hist[i] = entry
            return "replaced"
    hist.append(entry)
    return "added"


def aggregate_theme_rollups(history: dict, results: list, today: str):
    """Pool TP/N per (theme, level, quarter) and write theme-level entries."""
    pooled = defaultdict(lambda: {"tp": 0, "n": 0, "keywords": 0})
    for r in results:
        acc = pooled[(r["theme"], r["level"], r["quarter"])]
        acc["tp"] += r["tp"]
        acc["n"] += r["n"]
        acc["keywords"] += 1

    for (theme, level, quarter), acc in sorted(pooled.items()):
        if acc["n"] == 0:
            continue
        precision = acc["tp"] / acc["n"]
        action = _upsert_theme_entry(history, theme, level, {
            "date": today,
            "quarter": quarter,
            "n": acc["n"],
            "tp": acc["tp"],
            "precision": round(precision, 3),
            "audit": "quarterly_drift",
        })
        print(f"  THEME {theme:14s} {level:7s} {quarter}: "
              f"{acc['tp']}/{acc['n']} = {precision:.1%} "
              f"({acc['keywords']} keywords, {action})")


def backfill_theme_rollups(history: dict, quarters: list, entry_date: str):
    """One-time reconstruction of theme-level rollups from keyword history.

    The 2026-06 / 2026-07 cycles were recorded before cmd_record wrote
    theme-level rollups, so their pooled figures are rebuilt here from the
    per-keyword n/tp already stored in history["keywords"].
    """
    results = []
    for term, kw in history.get("keywords", {}).items():
        theme = kw.get("theme")
        for e in kw.get("history", []):
            if e.get("quarter") in quarters and theme:
                results.append({
                    "theme": theme,
                    "level": e["level"],
                    "quarter": e["quarter"],
                    "n": e["n"],
                    "tp": e["tp"],
                })
    if not results:
        print(f"  No keyword history found for quarters {quarters}")
        return
    aggregate_theme_rollups(history, results, entry_date)


def cmd_record(args):
    history = load_drift_history()
    history.setdefault("themes", {})
    history.setdefault("keywords", {})

    if args.backfill_themes:
        quarters = [q.strip() for q in args.backfill_themes.split(",") if q.strip()]
        print(f"Backfilling theme-level rollups for quarters: {', '.join(quarters)}")
        backfill_theme_rollups(history, quarters, args.backfill_date)
        history["last_updated"] = history.get("last_updated") or date.today().isoformat()
        DRIFT_HISTORY.write_text(json.dumps(history, indent=2))
        print(f"\nUpdated {DRIFT_HISTORY}")
        return

    if not args.files:
        print("record: nothing to do — pass --files or --backfill-themes")
        return

    today = date.today().isoformat()
    parsed_count = 0
    parsed_results = []
    for fpath in args.files:
        p = Path(fpath)
        if not p.exists():
            print(f"  MISSING: {p}")
            continue
        parsed = parse_result_file(p)
        if not parsed:
            continue
        term = slug_to_term(parsed["slug"], parsed["theme"])
        if not term:
            print(f"  WARN {p.name}: couldn't reverse slug '{parsed['slug']}' to a keyword in theme '{parsed['theme']}'. Skipping.")
            continue
        # Record into per-keyword history
        kw = history["keywords"].setdefault(term, {"theme": parsed["theme"], "history": [], "status": "unknown", "notes": ""})
        kw["history"].append({
            "date": today,
            "quarter": parsed["quarter"],
            "level": parsed["level"],
            "n": parsed["n"],
            "tp": parsed["tp"],
            "precision": round(parsed["precision"], 3),
            "audit": "quarterly_drift",
        })
        # Update status based on latest precision
        if parsed["precision"] < 0.60:
            kw["status"] = "inverted_" + parsed["level"]
        elif parsed["precision"] < 0.80:
            kw["status"] = "noisy_" + parsed["level"]
        else:
            kw["status"] = "healthy_" + parsed["level"]
        parsed_count += 1
        parsed_results.append(parsed)
        print(f"  OK {term} ({parsed['level']}): {parsed['tp']}/{parsed['n']} = {parsed['precision']:.1%}")

    # Pooled per-theme rollups from this run's files (see comment above).
    if parsed_results:
        print("")
        aggregate_theme_rollups(history, parsed_results, today)

    history["last_updated"] = today
    DRIFT_HISTORY.write_text(json.dumps(history, indent=2))
    print(f"\nRecorded {parsed_count} keyword measurements.")
    print(f"Updated {DRIFT_HISTORY}")


# ── REPORT ────────────────────────────────────────────────────────────────
def cmd_report(args):
    history = load_drift_history()
    print(f"=== Drift report ({history.get('last_updated', 'unknown')}) ===\n")
    print("Per-theme latest precision (post / comment):\n")
    for theme, t in sorted(history.get("themes", {}).items()):
        post_h = t.get("post_level", {}).get("history", [])
        comm_h = t.get("comment_level", {}).get("history", [])
        post_str = f"{post_h[-1]['precision']:.0%} (n={post_h[-1]['n']}, {post_h[-1]['date']})" if post_h else "(no data)"
        comm_str = f"{comm_h[-1]['precision']:.0%} (n={comm_h[-1]['n']}, {comm_h[-1]['date']})" if comm_h else "(no data)"
        alarm_post = " ⚠️" if post_h and post_h[-1]['precision'] < ALARM_PRECISION else ""
        alarm_comm = " ⚠️" if comm_h and comm_h[-1]['precision'] < ALARM_PRECISION else ""
        print(f"  {theme:14s}  post: {post_str}{alarm_post}    comment: {comm_str}{alarm_comm}")

    print("\nPer-keyword drift (sorted by latest precision):\n")
    keyword_rows = []
    for term, kw in history.get("keywords", {}).items():
        if not kw["history"]:
            continue
        latest = kw["history"][-1]
        keyword_rows.append((latest["precision"], term, kw["theme"], latest))
    for prec, term, theme, latest in sorted(keyword_rows):
        alarm = " ⚠️" if prec < ALARM_PRECISION else ""
        change = ""
        prior = [h for h in history["keywords"][term]["history"][:-1] if h["level"] == latest["level"]]
        if prior:
            delta = prec - prior[-1]["precision"]
            sign = "+" if delta >= 0 else ""
            change = f"  ({sign}{delta:.0%} since {prior[-1]['date']})"
        print(f"  {term:30s}  [{theme:14s}]  {latest['level']:7s}  {prec:>5.0%}{alarm}{change}")

    # Alarm summary
    alarms = [
        term for term, kw in history.get("keywords", {}).items()
        if kw["history"] and kw["history"][-1]["precision"] < ALARM_PRECISION
    ]
    print(f"\nAlarm threshold: precision < {ALARM_PRECISION:.0%}")
    print(f"Keywords below threshold: {len(alarms)}")
    if alarms:
        for term in alarms:
            print(f"  - {term}")


# ── MAIN ──────────────────────────────────────────────────────────────────
def main():
    p = argparse.ArgumentParser(description="Quarterly drift check for keyword precision.")
    sub = p.add_subparsers(dest="cmd", required=True)

    b = sub.add_parser("build", help="Build sample files for agent classification.")
    b.add_argument("--quarter", default=None, help="e.g. 2026-Q3 (default: current)")
    b.add_argument("--n", type=int, default=50, help="Hits per keyword (default 50)")
    b.add_argument("--surface", choices=["post", "comment", "both"], default="both")
    b.add_argument("--keywords", default=None, help="Comma-separated subset of keywords")
    b.set_defaults(func=cmd_build)

    r = sub.add_parser("record", help="Parse agent classification result files.")
    r.add_argument("--files", nargs="+", default=None, help="Result .txt files")
    r.add_argument(
        "--backfill-themes",
        default=None,
        metavar="QUARTERS",
        help="One-time: rebuild pooled theme-level rollups for these comma-separated "
             "quarters (e.g. 2026-06,2026-07) from existing per-keyword history. "
             "Does not read result files.",
    )
    r.add_argument(
        "--backfill-date",
        default="2026-08-08",
        help="Date stamped on backfilled theme entries (default: 2026-08-08, when "
             "the June/July cycles were recorded).",
    )
    r.set_defaults(func=cmd_record)

    rep = sub.add_parser("report", help="Print current drift status.")
    rep.set_defaults(func=cmd_report)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
