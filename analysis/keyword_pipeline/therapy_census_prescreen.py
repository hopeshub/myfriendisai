#!/usr/bin/env python3
"""Pre-screen for therapy census-validation (Lever 1).

For each candidate phrase, count word-boundary matches against title+body of
posts in the active T1-T3 keyword communities (source='post' universe, the
public chart series). Reports:

  wb_hits      total word-boundary matches
  new_hits     of those, posts NOT already tagged therapy (the genuinely new
               clean volume the keyword would add)
  already      of those, posts already tagged therapy by another keyword

A candidate is a census-validation candidate when wb_hits is small enough that
the full match set can be read end-to-end (<= ~120). The 50-hit "volume floor"
in the project's n=100 method is a sampling-method artifact, not a quality bar:
a keyword with 29 hits is validated by reading all 29, not by sampling.
"""
from __future__ import annotations

import re
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT))

from src.config import load_keyword_communities  # noqa: E402
from src.db.operations import EXCLUDED_AUTHORS  # noqa: E402

DB = ROOT / "data" / "tracker.db"

# Specific AI-as-therapy phrasings surfaced by the 2026-05-15 therapy mining
# (analysis/keyword_pipeline/spotcheck_2026-05-15/therapy_mine/*_mined.md).
# Excludes: phrases subsumed by an existing therapy keyword (ai therapist,
# free therapy, ai therapy, as a therapist, therapeutic, for therapy,
# emotional support, coping mechanism) and the 4 already-failed candidates
# (therapist bot, therapy bot, psychologist bot, comfort character).
CANDIDATES = [
    "instead of therapy",
    "my psychologist",
    "my psychiatrist",
    "therapy session",
    "therapy sessions",
    "therapy tool",
    "talk therapy",
    "mental health support",
    "see a therapist",
    "seeing a therapist",
    "go to a therapist",
    "real therapist",
    "actual therapist",
    "like a therapist",
    "my own therapist",
    "better than therapy",
    "cheaper than therapy",
    "afford therapy",
    "process trauma",
    "trauma processing",
    "non-judgmental",
    "non-judgemental",
    "talked me through",
    "talk me down",
    "mental breakdown",
    "helped me heal",
    "someone to vent to",
]


def main() -> None:
    eligible = [c["subreddit"] for c in load_keyword_communities()]
    excl = list(EXCLUDED_AUTHORS)
    sub_ph = ",".join("?" * len(eligible))
    exc_ph = ",".join("?" * len(excl))

    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row

    # post_ids already tagged therapy (source='post')
    tagged = {
        r[0] for r in conn.execute(
            "SELECT DISTINCT post_id FROM post_keyword_tags "
            "WHERE category='therapy' AND source='post'")
    }

    print(f"{'candidate':24s} {'wb_hits':>8s} {'new':>6s} {'already':>8s} "
          f"{'census?':>8s}")
    print("-" * 60)
    rows_out = []
    for term in CANDIDATES:
        pat = re.compile(r"\b" + re.escape(term.replace("-", r"\-")) + r"\b",
                         re.IGNORECASE)
        like = term.lower()
        rows = conn.execute(
            f"""SELECT id, title, selftext
                FROM posts
                WHERE subreddit IN ({sub_ph})
                  AND (author IS NULL OR author NOT IN ({exc_ph}))
                  AND lower(coalesce(title,'')||' '||coalesce(selftext,''))
                      LIKE '%'||?||'%'""",
            [*eligible, *excl, like],
        ).fetchall()
        matched = [r for r in rows
                   if pat.search(f"{r['title'] or ''} {r['selftext'] or ''}")]
        wb = len(matched)
        new = sum(1 for r in matched if r["id"] not in tagged)
        already = wb - new
        census = "yes" if 0 < wb <= 130 else ("n=100" if wb > 130 else "—")
        print(f"{term:24s} {wb:8d} {new:6d} {already:8d} {census:>8s}")
        rows_out.append((term, wb, new, already))

    conn.close()
    total_new = sum(r[2] for r in rows_out if 0 < r[1] <= 130)
    print("-" * 60)
    print(f"max new clean volume available across census candidates: {total_new}")
    print("(upper bound — actual recovered volume = sum over candidates that "
          "pass the 80% census gate)")


if __name__ == "__main__":
    main()
