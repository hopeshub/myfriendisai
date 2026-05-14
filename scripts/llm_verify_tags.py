#!/usr/bin/env python3
"""LLM verification of keyword-tagged items. Hybrid gating CLI.

Subcommands:

  backfill --keywords <k1,k2,...> [--limit N] [--surface post|comment|both]
           [--model MODEL] [--mock] [--dry-run]
      Classify existing tagged items for the given keywords. Writes verdicts
      to llm_classifications. Idempotent — skips already-classified items
      for the same (tag, model) tuple.

  daily [--since-days N] [--model MODEL] [--mock]
      Classify recently-tagged items not yet verified. Intended to run as
      part of the daily collection pipeline.

  recheck --model NEW_MODEL [--sample N] [--mock]
      Re-classify a sample of items already classified under a different
      model. Used to detect model-version drift.

  report [--model MODEL]
      Print per-theme and per-keyword precision based on current LLM
      verdicts. No API calls.

  calibration --verdicts-file PATH [--model MODEL] [--mock]
      Replay LLM classification against a ground-truth set (e.g. today's
      adversarial audit verdicts) and report accuracy. Used for drift
      detection and model selection.

Environment:
  ANTHROPIC_API_KEY must be set for non-mock runs.

Cost reference (Haiku 4.5):
  ~$0.001 per item. 1,000 items ≈ $1. Backfill of all noisy-keyword tags
  is ~5,000 items ≈ $5.
"""

import argparse
import json
import os
import sqlite3
import sys
import time
from pathlib import Path
from typing import Optional

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.llm_classifier import LLMClassifier, DEFAULT_MODEL  # noqa: E402

DB_PATH = PROJECT_ROOT / "data" / "tracker.db"

# Currently-flagged noisy keywords (from drift_history.json defaults).
# Backfill targets these first.
NOISY_KEYWORDS_DEFAULT = [
    "therapeutic", "emotional support",
    "honeymoon", "wedding", "we broke up", "love my ai",
    "sex with",
    "hours a day", "screen time", "neglecting my",
    "mourning", "mourn", "goodbye", "nerfed", "gutted",
    "selfhood", "has a soul", "inner life", "more than code", "personhood",
]


def connect() -> sqlite3.Connection:
    # 60s busy_timeout — multiple backfill processes can run concurrently
    # without locking each other out. WAL journal mode lets readers and
    # one writer overlap; busy_timeout handles contention between writers.
    conn = sqlite3.connect(DB_PATH, timeout=60.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA busy_timeout = 60000")
    return conn


# ── BACKFILL ──────────────────────────────────────────────────────────────
def fetch_post_candidates(conn, keyword: str, model: str, limit: Optional[int]):
    """Posts tagged with `keyword` and not yet classified under `model`."""
    cur = conn.execute(
        """SELECT p.id, p.subreddit, p.title, p.selftext, t.matched_term, t.category
           FROM post_keyword_tags t
           JOIN posts p ON p.id = t.post_id
           LEFT JOIN llm_classifications c
               ON c.tag_type='post' AND c.post_id=p.id
                  AND c.theme=t.category AND c.keyword=t.matched_term
                  AND c.model=?
           WHERE t.matched_term=? AND t.source='post' AND c.post_id IS NULL
           LIMIT ?""",
        (model, keyword, limit or -1),
    )
    return cur.fetchall()


def fetch_comment_candidates(conn, keyword: str, model: str, limit: Optional[int]):
    """Comments tagged with `keyword` not yet classified under `model`."""
    cur = conn.execute(
        """SELECT h.comment_id, h.subreddit, h.matched_term, h.category,
                  c.body AS comment_body,
                  p.id AS post_id, p.title AS parent_title, p.selftext AS parent_body
           FROM comment_keyword_hits h
           JOIN comments c ON c.id = h.comment_id
           JOIN posts p ON p.id = h.post_id
           LEFT JOIN llm_classifications cl
               ON cl.tag_type='comment' AND cl.comment_id=h.comment_id
                  AND cl.theme=h.category AND cl.keyword=h.matched_term
                  AND cl.model=?
           WHERE h.matched_term=? AND cl.comment_id IS NULL
           LIMIT ?""",
        (model, keyword, limit or -1),
    )
    return cur.fetchall()


def insert_verdict(conn, *, tag_type, tag_id, post_id, comment_id, theme, keyword, verdict, model):
    """Upsert a verdict row. Conflict target = idx_llm_class_unique_v2:
    (tag_type, COALESCE(comment_id, post_id), theme, keyword, model)."""
    # Check existence first (SQLite ON CONFLICT with expression-based indexes is
    # finicky; do the check explicitly).
    coalesced = comment_id or post_id
    existing = conn.execute(
        """SELECT id FROM llm_classifications
           WHERE tag_type=? AND COALESCE(comment_id, post_id)=?
             AND theme=? AND keyword=? AND model=?""",
        (tag_type, coalesced, theme, keyword, model),
    ).fetchone()
    if existing:
        conn.execute(
            """UPDATE llm_classifications
               SET verdict=?, reason=?, confidence=?, classification=?,
                   classified_at=strftime('%Y-%m-%dT%H:%M:%SZ', 'now')
               WHERE id=?""",
            (verdict.verdict, verdict.reason, verdict.confidence, verdict.verdict, existing[0]),
        )
    else:
        conn.execute(
            """INSERT INTO llm_classifications
                   (post_id, comment_id, tag_type, theme, keyword,
                    classification, verdict, reason, confidence, model)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (post_id, comment_id, tag_type, theme, keyword,
             verdict.verdict, verdict.verdict, verdict.reason, verdict.confidence, model),
        )


def cmd_backfill(args):
    keywords = args.keywords.split(",") if args.keywords else NOISY_KEYWORDS_DEFAULT
    model = args.model
    clf = LLMClassifier(model=model, mock=args.mock)
    conn = connect()
    try:
        total = ok = err = skip = 0
        for kw in keywords:
            kw = kw.strip()
            print(f"\n=== {kw} ===")
            if args.surface in ("post", "both"):
                rows = fetch_post_candidates(conn, kw, model, args.limit)
                print(f"  posts: {len(rows)} candidates")
                for row in rows:
                    total += 1
                    if args.dry_run:
                        continue
                    try:
                        v = clf.classify(
                            title=row["title"], body=row["selftext"] or "",
                            theme=row["category"], keyword=row["matched_term"],
                            subreddit=row["subreddit"], is_comment=False,
                        )
                        insert_verdict(
                            conn, tag_type="post", tag_id=row["id"],
                            post_id=row["id"], comment_id=None,
                            theme=row["category"], keyword=row["matched_term"],
                            verdict=v, model=model,
                        )
                        ok += 1
                        if ok % 25 == 0:
                            conn.commit()
                            print(f"    {ok} classified so far")
                    except Exception as e:
                        err += 1
                        print(f"    ERR post {row['id']}: {e}")
            if args.surface in ("comment", "both"):
                rows = fetch_comment_candidates(conn, kw, model, args.limit)
                print(f"  comments: {len(rows)} candidates")
                for row in rows:
                    total += 1
                    if args.dry_run:
                        continue
                    try:
                        v = clf.classify(
                            title="", body=row["comment_body"] or "",
                            theme=row["category"], keyword=row["matched_term"],
                            subreddit=row["subreddit"], is_comment=True,
                            parent_title=row["parent_title"],
                            parent_body=row["parent_body"],
                        )
                        insert_verdict(
                            conn, tag_type="comment", tag_id=row["comment_id"],
                            post_id=row["post_id"], comment_id=row["comment_id"],
                            theme=row["category"], keyword=row["matched_term"],
                            verdict=v, model=model,
                        )
                        ok += 1
                        if ok % 25 == 0:
                            conn.commit()
                            print(f"    {ok} classified so far")
                    except Exception as e:
                        err += 1
                        print(f"    ERR comment {row['comment_id']}: {e}")
            conn.commit()
        print(f"\nDone. Considered {total}, ok {ok}, err {err}, skipped {skip}.")
        if args.dry_run:
            print("(dry-run: no inserts performed)")
    finally:
        conn.close()


# ── DAILY ─────────────────────────────────────────────────────────────────
def cmd_daily(args):
    """Classify recently-tagged items not yet verified for noisy keywords."""
    model = args.model
    clf = LLMClassifier(model=model, mock=args.mock)
    conn = connect()
    try:
        cutoff = f"-{args.since_days} days"
        # Posts: created_utc within window
        for kw in NOISY_KEYWORDS_DEFAULT:
            rows = conn.execute(
                """SELECT p.id, p.subreddit, p.title, p.selftext, t.matched_term, t.category
                   FROM post_keyword_tags t
                   JOIN posts p ON p.id = t.post_id
                   LEFT JOIN llm_classifications c
                       ON c.tag_type='post' AND c.post_id=p.id
                          AND c.theme=t.category AND c.keyword=t.matched_term
                          AND c.model=?
                   WHERE t.matched_term=? AND t.source='post' AND c.post_id IS NULL
                     AND date(p.created_utc, 'unixepoch') >= date('now', ?)""",
                (model, kw, cutoff),
            ).fetchall()
            for row in rows:
                try:
                    v = clf.classify(
                        title=row["title"], body=row["selftext"] or "",
                        theme=row["category"], keyword=row["matched_term"],
                        subreddit=row["subreddit"], is_comment=False,
                    )
                    insert_verdict(
                        conn, tag_type="post", tag_id=row["id"],
                        post_id=row["id"], comment_id=None,
                        theme=row["category"], keyword=row["matched_term"],
                        verdict=v, model=model,
                    )
                except Exception as e:
                    print(f"    ERR: {e}")
            conn.commit()
        print("daily verification complete.")
    finally:
        conn.close()


# ── RECHECK ───────────────────────────────────────────────────────────────
def cmd_recheck(args):
    """Re-classify already-classified items under a new model."""
    new_model = args.model
    clf = LLMClassifier(model=new_model, mock=args.mock)
    conn = connect()
    try:
        # Sample items classified under the OTHER model but not yet under this one
        rows = conn.execute(
            f"""SELECT DISTINCT c.post_id, c.comment_id, c.tag_type,
                     c.theme, c.keyword, c.verdict AS prior_verdict
              FROM llm_classifications c
              WHERE c.model != ? AND c.verdict IN ('TP', 'FP')
              ORDER BY RANDOM()
              LIMIT ?""",
            (new_model, args.sample),
        ).fetchall()
        agree = 0
        total = 0
        for r in rows:
            if r["tag_type"] == "post":
                post = conn.execute(
                    "SELECT subreddit, title, selftext FROM posts WHERE id=?",
                    (r["post_id"],),
                ).fetchone()
                if not post:
                    continue
                v = clf.classify(
                    title=post["title"], body=post["selftext"] or "",
                    theme=r["theme"], keyword=r["keyword"],
                    subreddit=post["subreddit"], is_comment=False,
                )
            else:
                row = conn.execute(
                    """SELECT c.body, c.subreddit, p.title, p.selftext
                       FROM comments c JOIN posts p ON p.id=c.post_id
                       WHERE c.id=?""",
                    (r["comment_id"],),
                ).fetchone()
                if not row:
                    continue
                v = clf.classify(
                    title="", body=row["body"] or "",
                    theme=r["theme"], keyword=r["keyword"],
                    subreddit=row["subreddit"], is_comment=True,
                    parent_title=row["title"], parent_body=row["selftext"],
                )
            insert_verdict(
                conn, tag_type=r["tag_type"],
                tag_id=r["post_id"] or r["comment_id"],
                post_id=r["post_id"], comment_id=r["comment_id"],
                theme=r["theme"], keyword=r["keyword"],
                verdict=v, model=new_model,
            )
            total += 1
            if v.verdict == r["prior_verdict"]:
                agree += 1
            if total % 25 == 0:
                conn.commit()
                print(f"  {total} recheck, agreement {agree}/{total} = {agree/total:.1%}")
        conn.commit()
        if total:
            print(f"\nFinal: {agree}/{total} = {agree/total:.1%} agreement with prior model")
    finally:
        conn.close()


# ── REPORT ────────────────────────────────────────────────────────────────
def cmd_report(args):
    conn = connect()
    try:
        model_filter = ""
        params = []
        if args.model:
            model_filter = " AND model=?"
            params = [args.model]

        print("=== Per-theme LLM precision (TP / classified items) ===\n")
        rows = conn.execute(
            f"""SELECT theme, tag_type,
                     SUM(CASE WHEN verdict='TP' THEN 1 ELSE 0 END) AS tp,
                     SUM(CASE WHEN verdict='FP' THEN 1 ELSE 0 END) AS fp,
                     SUM(CASE WHEN verdict='AMBIGUOUS' THEN 1 ELSE 0 END) AS amb,
                     COUNT(*) AS n
                 FROM llm_classifications
                 WHERE 1=1{model_filter}
                 GROUP BY theme, tag_type
                 ORDER BY theme, tag_type""",
            params,
        ).fetchall()
        for r in rows:
            n = r["n"]
            prec = r["tp"] / n if n else 0
            print(f"  {r['theme']:14s} {r['tag_type']:7s}  TP={r['tp']:4d}  FP={r['fp']:4d}  AMB={r['amb']:3d}  prec={prec:.1%}  (n={n})")

        print("\n=== Worst keywords by FP count ===\n")
        rows = conn.execute(
            f"""SELECT keyword, theme,
                     SUM(CASE WHEN verdict='FP' THEN 1 ELSE 0 END) AS fp,
                     COUNT(*) AS n
                 FROM llm_classifications
                 WHERE 1=1{model_filter}
                 GROUP BY keyword, theme
                 HAVING n >= 5
                 ORDER BY (fp * 1.0 / n) DESC, fp DESC
                 LIMIT 20""",
            params,
        ).fetchall()
        for r in rows:
            fp_rate = r["fp"] / r["n"] if r["n"] else 0
            print(f"  {r['keyword']:30s} [{r['theme']:14s}]  FP={r['fp']:3d}/{r['n']:4d} = {fp_rate:.0%}")
    finally:
        conn.close()


# ── CALIBRATION ───────────────────────────────────────────────────────────
def cmd_calibration(args):
    """Replay LLM against a ground-truth verdicts file (one JSONL per line:
    {tag_type, post_id_or_comment_id, theme, keyword, gold_verdict}).
    Reports accuracy of LLM verdicts vs. ground truth."""
    if not Path(args.verdicts_file).exists():
        print(f"ERROR: verdicts file not found: {args.verdicts_file}", file=sys.stderr)
        sys.exit(1)
    clf = LLMClassifier(model=args.model, mock=args.mock)
    conn = connect()
    try:
        agree = total = 0
        with open(args.verdicts_file) as f:
            for line in f:
                if not line.strip():
                    continue
                entry = json.loads(line)
                if entry.get("tag_type") == "post":
                    row = conn.execute(
                        "SELECT subreddit, title, selftext FROM posts WHERE id=?",
                        (entry["post_id"],),
                    ).fetchone()
                    if not row:
                        continue
                    v = clf.classify(
                        title=row["title"], body=row["selftext"] or "",
                        theme=entry["theme"], keyword=entry["keyword"],
                        subreddit=row["subreddit"], is_comment=False,
                    )
                else:
                    row = conn.execute(
                        """SELECT c.body, c.subreddit, p.title, p.selftext
                           FROM comments c JOIN posts p ON p.id=c.post_id
                           WHERE c.id=?""",
                        (entry["comment_id"],),
                    ).fetchone()
                    if not row:
                        continue
                    v = clf.classify(
                        title="", body=row["body"] or "",
                        theme=entry["theme"], keyword=entry["keyword"],
                        subreddit=row["subreddit"], is_comment=True,
                        parent_title=row["title"], parent_body=row["selftext"],
                    )
                total += 1
                if v.verdict == entry["gold_verdict"]:
                    agree += 1
                else:
                    print(f"  DISAGREE  gold={entry['gold_verdict']}  llm={v.verdict}  "
                          f"theme={entry['theme']}  kw={entry['keyword']}  "
                          f"reason={v.reason[:80]}")
        print(f"\nCalibration: {agree}/{total} = {agree/total:.1%}" if total else "no items")
    finally:
        conn.close()


# ── MAIN ──────────────────────────────────────────────────────────────────
def main():
    p = argparse.ArgumentParser(description="LLM verification of keyword-tagged items.")
    sub = p.add_subparsers(dest="cmd", required=True)

    bf = sub.add_parser("backfill")
    bf.add_argument("--keywords", default=None, help="Comma-separated; default = noisy set")
    bf.add_argument("--surface", choices=["post", "comment", "both"], default="both")
    bf.add_argument("--limit", type=int, default=None)
    bf.add_argument("--model", default=DEFAULT_MODEL)
    bf.add_argument("--mock", action="store_true")
    bf.add_argument("--dry-run", action="store_true")
    bf.set_defaults(func=cmd_backfill)

    dl = sub.add_parser("daily")
    dl.add_argument("--since-days", type=int, default=7)
    dl.add_argument("--model", default=DEFAULT_MODEL)
    dl.add_argument("--mock", action="store_true")
    dl.set_defaults(func=cmd_daily)

    rc = sub.add_parser("recheck")
    rc.add_argument("--model", required=True, help="New model to recheck under")
    rc.add_argument("--sample", type=int, default=200)
    rc.add_argument("--mock", action="store_true")
    rc.set_defaults(func=cmd_recheck)

    rp = sub.add_parser("report")
    rp.add_argument("--model", default=None)
    rp.set_defaults(func=cmd_report)

    cb = sub.add_parser("calibration")
    cb.add_argument("--verdicts-file", required=True)
    cb.add_argument("--model", default=DEFAULT_MODEL)
    cb.add_argument("--mock", action="store_true")
    cb.set_defaults(func=cmd_calibration)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
