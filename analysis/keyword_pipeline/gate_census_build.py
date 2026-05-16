#!/usr/bin/env python3
"""Build census-classification batches for Lever 2 — co-occurrence gating.

To design and measure a co-occurrence gate for a weak keyword, every post the
keyword currently matches must be labelled (so the gated-in subset's precision
can be computed). This pulls the full census for each target keyword and writes
blind dual-rubric batches, separated by theme so each post is judged against the
correct theme definition.

Targets: therapy `coping mechanism` (the biggest drag left after the
therapeutic/emotional-support cut) and the weak consciousness keywords.
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
OUTDIR = THISDIR / "gate_census_2026-05-16"

TARGETS = {
    "therapy": ["coping mechanism"],
    "consciousness": ["personhood", "subjective experience", "tulpa",
                      "more than code", "not just an ai"],
}


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

    manifest = {"seed": SEED, "audit_date": "2026-05-16", "targets": TARGETS,
                "candidates": {}, "samples": {}, "batches": {}}
    sid_n = 6000
    all_batches: dict[str, list[str]] = {}

    for theme, terms in TARGETS.items():
        cand_posts: dict[str, list[str]] = {}
        post_rows: dict[str, sqlite3.Row] = {}
        for term in terms:
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
        manifest["candidates"][theme] = cand_posts

        uniq = sorted(post_rows)
        rng.shuffle(uniq)
        sid_of = {}
        for pid in uniq:
            s = f"ID-{sid_n}"
            sid_n += 1
            sid_of[pid] = s
            manifest["samples"][s] = {"post_id": pid, "theme": theme}

        note = (f"Gate-design census. Every post here matched a weak "
                f"{theme} keyword being considered for a co-occurrence gate; "
                f"the keyword is hidden. Code each post fresh on its text alone.")
        chunks = [uniq[i:i + CHUNK] for i in range(0, len(uniq), CHUNK)]
        for ci, chunk in enumerate(chunks, 1):
            name = f"batch_gate_{theme[:4]}_{ci:02d}"
            body = precision_header(theme, tdefs, note).replace("{BATCH}", name)
            body = body.replace("spotcheck_2026-05-15/results",
                                "gate_census_2026-05-16/results")
            for pid in chunk:
                body += post_entry(sid_of[pid], post_rows[pid], BODY_CHARS)
            (OUTDIR / "batches" / f"{name}.md").write_text(body, encoding="utf-8")
            all_batches[f"{name}.md"] = [sid_of[pid] for pid in chunk]

        print(f"[{theme}] {len(uniq)} unique posts, {len(chunks)} batches")
        for t in terms:
            print(f"    {t:24s} matched={len(cand_posts[t])}")

    conn.close()
    manifest["batches"] = all_batches
    (OUTDIR / "gate_census_manifest.json").write_text(
        json.dumps(manifest, indent=1), encoding="utf-8")
    print(f"total batches: {len(all_batches)} -> {OUTDIR}/batches")


if __name__ == "__main__":
    main()
