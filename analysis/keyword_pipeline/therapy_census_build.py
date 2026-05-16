#!/usr/bin/env python3
"""Build census-validation batches for therapy keyword candidates (Lever 1).

Census validation: instead of sampling n=100, read EVERY word-boundary match of
a candidate phrase. For a sub-100-hit keyword this is a full population census —
the resulting precision has no sampling error, and a clean-but-rare phrase
(dismissed by the n=100 method's 50-hit floor) can be admitted on its merits.

Each candidate's matches are pooled, deduplicated across candidates, and written
as blind dual-rubric batches in the spot-check audit format (agents code each
post fresh for the therapy theme, blind to the keyword). Scoring later
attributes each post's verdict to every candidate it matched.
"""
from __future__ import annotations

import json
import random
import re
import sqlite3
import sys
from pathlib import Path

THISDIR = Path(__file__).parent
sys.path.insert(0, str(THISDIR.parent.parent))
sys.path.insert(0, str(THISDIR))

from src.config import load_keyword_communities  # noqa: E402
from src.db.operations import EXCLUDED_AUTHORS  # noqa: E402
from spotcheck_v2_build import (  # noqa: E402
    DB, BODY_CHARS, load_theme_defs, precision_header, post_entry,
)

SEED = 20260516
CHUNK = 40
OUTDIR = THISDIR / "therapy_census_2026-05-16"

# Census candidates — specific AI-as-therapy phrasings below the n=100 volume
# floor (or just over it but still fully readable). From the 2026-05-15
# pre-screen; drops dead phrases (instead of therapy: 1 hit), above-floor
# phrases (mental breakdown: 217 -> normal n=100), and near-fully-redundant
# ones (trauma processing: only 2 new). Counts are 2026-05-16 wb_hits.
CANDIDATES = [
    "my psychologist", "my psychiatrist", "therapy session", "therapy sessions",
    "therapy tool", "talk therapy", "mental health support", "see a therapist",
    "seeing a therapist", "go to a therapist", "real therapist",
    "actual therapist", "like a therapist", "my own therapist",
    "better than therapy", "cheaper than therapy", "afford therapy",
    "process trauma", "talked me through", "talk me down", "helped me heal",
    "someone to vent to",
]


def main() -> None:
    rng = random.Random(SEED)
    tdefs = load_theme_defs()
    eligible = [c["subreddit"] for c in load_keyword_communities()]
    excl = list(EXCLUDED_AUTHORS)
    sub_ph = ",".join("?" * len(eligible))
    exc_ph = ",".join("?" * len(excl))

    (OUTDIR / "batches").mkdir(parents=True, exist_ok=True)
    (OUTDIR / "results").mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row

    tagged = {
        r[0] for r in conn.execute(
            "SELECT DISTINCT post_id FROM post_keyword_tags "
            "WHERE category='therapy' AND source='post'")
    }

    cand_posts: dict[str, list[str]] = {}   # term -> matched post_ids
    post_rows: dict[str, sqlite3.Row] = {}  # post_id -> row (unique)
    for term in CANDIDATES:
        pat = re.compile(r"\b" + re.escape(term) + r"\b", re.IGNORECASE)
        rows = conn.execute(
            f"""SELECT id, subreddit, title, selftext,
                       date(created_utc,'unixepoch') post_date
                FROM posts
                WHERE subreddit IN ({sub_ph})
                  AND (author IS NULL OR author NOT IN ({exc_ph}))
                  AND lower(coalesce(title,'')||' '||coalesce(selftext,''))
                      LIKE '%'||?||'%'""",
            [*eligible, *excl, term.lower()],
        ).fetchall()
        matched = [r for r in rows
                   if pat.search(f"{r['title'] or ''} {r['selftext'] or ''}")]
        cand_posts[term] = [r["id"] for r in matched]
        for r in matched:
            post_rows.setdefault(r["id"], r)
    conn.close()

    # unique posts -> stable sample ids
    uniq = sorted(post_rows)
    rng.shuffle(uniq)
    sid_of = {pid: f"ID-{5000 + i}" for i, pid in enumerate(uniq)}
    samples = {sid_of[pid]: {"post_id": pid, "theme": "therapy"} for pid in uniq}

    note = ("Candidate-keyword census validation. Every post here matched a "
            "phrase being tested for the therapy theme; the keyword is hidden. "
            "Code each post fresh on its text alone.")
    batches: dict[str, list[str]] = {}
    chunks = [uniq[i:i + CHUNK] for i in range(0, len(uniq), CHUNK)]
    for ci, chunk in enumerate(chunks, 1):
        name = f"batch_tcensus_{ci:02d}"
        body = precision_header("therapy", tdefs, note).replace("{BATCH}", name)
        body = body.replace("spotcheck_2026-05-15/results",
                            "therapy_census_2026-05-16/results")
        for pid in chunk:
            body += post_entry(sid_of[pid], post_rows[pid], BODY_CHARS)
        (OUTDIR / "batches" / f"{name}.md").write_text(body, encoding="utf-8")
        batches[f"{name}.md"] = [sid_of[pid] for pid in chunk]

    new_counts = {t: sum(1 for p in ps if p not in tagged)
                  for t, ps in cand_posts.items()}
    manifest = {
        "seed": SEED, "audit_date": "2026-05-16", "theme": "therapy",
        "method": "census (read every word-boundary match)",
        "candidates": cand_posts,
        "new_volume_by_candidate": new_counts,
        "samples": samples, "batches": batches,
    }
    (OUTDIR / "census_manifest.json").write_text(
        json.dumps(manifest, indent=1), encoding="utf-8")

    print(f"candidates: {len(CANDIDATES)}")
    for t in CANDIDATES:
        print(f"  {t:22s} matched={len(cand_posts[t]):4d}  new={new_counts[t]:4d}")
    print(f"unique posts to classify: {len(uniq)}")
    print(f"batches: {len(batches)} (CHUNK={CHUNK}) -> {OUTDIR}/batches")


if __name__ == "__main__":
    main()
