#!/usr/bin/env python3
"""Build n=100 dual-rubric validation batches for new therapy keyword candidates.

Candidates that cleared the volume pre-screen. Each is matched (word-boundary,
case-insensitive) against title+body of eligible-sub posts; up to 100 matches
are sampled and written as blind dual-rubric batches for CC agents — the same
protocol as the spot-check audit, so results are directly comparable.
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
    DB, OUTDIR, BODY_CHARS, load_theme_defs, precision_header, post_entry,
)

SEED = 20260515
N = 100
CHUNK = 40
CANDIDATES = ["therapist bot", "therapy bot", "psychologist bot", "vent to",
              "comfort character"]


def main() -> None:
    rng = random.Random(SEED)
    tdefs = load_theme_defs()
    eligible = [c["subreddit"] for c in load_keyword_communities()]
    excl = list(EXCLUDED_AUTHORS)
    sub_ph = ",".join("?" * len(eligible))
    exc_ph = ",".join("?" * len(excl))

    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row

    manifest: dict[str, dict] = {}
    batches: dict[str, list[str]] = {}
    sid = 4000

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
        # word-boundary filter
        matched = [r for r in rows
                   if pat.search(f"{r['title'] or ''} {r['selftext'] or ''}")]
        picked = matched if len(matched) <= N else rng.sample(matched, N)
        rng.shuffle(picked)
        items = []
        for r in picked:
            sid += 1
            s = f"ID-{sid:04d}"
            items.append((s, r))
            manifest[s] = {"theme": "therapy", "term": term, "post_id": r["id"],
                           "year": str(r["post_date"])[:4]}
        slug = term.replace(" ", "_")
        chunks = [items[i:i + CHUNK] for i in range(0, len(items), CHUNK)]
        note = (f"Candidate-keyword validation. All posts here matched a single "
                f"candidate phrase being tested for the therapy theme; code "
                f"each fresh on the text alone.")
        for ci, chunk in enumerate(chunks, 1):
            name = f"batch_tval_{slug}_{ci:02d}"
            body = precision_header("therapy", tdefs, note).replace("{BATCH}", name)
            for s, r in chunk:
                body += post_entry(s, r, BODY_CHARS)
            (OUTDIR / "batches" / f"{name}.md").write_text(body, encoding="utf-8")
            batches[f"{name}.md"] = [s for s, _ in chunk]
        print(f"{term:20} substring={len(rows)} word-boundary={len(matched)} "
              f"sampled={len(picked)} batches={len(chunks)}")

    conn.close()
    (OUTDIR / "therapy_validate_manifest.json").write_text(
        json.dumps({"seed": SEED, "candidates": CANDIDATES, "n": N,
                    "batches": batches, "samples": manifest}, indent=1),
        encoding="utf-8")
    print(f"total batches: {len(batches)}")


if __name__ == "__main__":
    main()
