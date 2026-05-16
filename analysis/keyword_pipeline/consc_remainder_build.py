#!/usr/bin/env python3
"""Census the remaining consciousness keywords not covered by the gate census.

The gate census already covered personhood / subjective experience / tulpa /
more than code / not just an ai. This covers the other six so the consciousness
theme's volume-weighted precision can be computed entirely from full censuses
rather than n=20 screens.
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
OUTDIR = THISDIR / "consc_census_2026-05-16"
TERMS = ["selfhood", "inner life", "has a soul", "lemoine", "sapience",
         "soulbonder"]


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

    cand_posts: dict[str, list[str]] = {}
    post_rows: dict[str, sqlite3.Row] = {}
    for term in TERMS:
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

    uniq = sorted(post_rows)
    rng.shuffle(uniq)
    sid_of = {pid: f"ID-{7000 + i}" for i, pid in enumerate(uniq)}
    samples = {sid_of[pid]: {"post_id": pid, "theme": "consciousness"}
               for pid in uniq}

    note = ("Census validation of consciousness keywords. Every post here "
            "matched a consciousness keyword; the keyword is hidden. Code each "
            "post fresh on its text alone.")
    batches: dict[str, list[str]] = {}
    chunks = [uniq[i:i + CHUNK] for i in range(0, len(uniq), CHUNK)]
    for ci, chunk in enumerate(chunks, 1):
        name = f"batch_cremain_{ci:02d}"
        body = precision_header("consciousness", tdefs, note).replace(
            "{BATCH}", name)
        body = body.replace("spotcheck_2026-05-15/results",
                            "consc_census_2026-05-16/results")
        for pid in chunk:
            body += post_entry(sid_of[pid], post_rows[pid], BODY_CHARS)
        (OUTDIR / "batches" / f"{name}.md").write_text(body, encoding="utf-8")
        batches[f"{name}.md"] = [sid_of[pid] for pid in chunk]

    (OUTDIR / "consc_census_manifest.json").write_text(
        json.dumps({"seed": SEED, "audit_date": "2026-05-16",
                    "theme": "consciousness", "candidates": cand_posts,
                    "samples": samples, "batches": batches}, indent=1),
        encoding="utf-8")
    for t in TERMS:
        print(f"  {t:16s} matched={len(cand_posts[t])}")
    print(f"unique posts: {len(uniq)}  batches: {len(batches)} -> {OUTDIR}")


if __name__ == "__main__":
    main()
