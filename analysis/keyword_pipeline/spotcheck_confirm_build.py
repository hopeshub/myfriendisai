#!/usr/bin/env python3
"""Confirmatory n=100 read for the spot-check audit's worst high-volume keywords.

The 2026-05-15 spot-check flagged `goodbye`, `emotional support`, and
`therapeutic` at 40-55% topical precision on an n=20 screen. n=20 has wide
CIs; this pulls n=100 per keyword for a tighter estimate before any cut/guard
decision. Same blind dual-rubric protocol as the main audit.

Outputs batches into spotcheck_2026-05-15/batches/ (batch_confirm_*.md) and a
confirm_manifest.json. Score with: parse results/batch_confirm_*_results.txt.
"""
from __future__ import annotations

import json
import random
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
TARGETS = [("rupture", "goodbye"), ("therapy", "emotional support"),
           ("therapy", "therapeutic")]


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
    sid = 3000

    for theme, term in TARGETS:
        rows = conn.execute(
            f"""SELECT DISTINCT p.id, p.subreddit, p.title, p.selftext,
                       t.post_date
                FROM post_keyword_tags t JOIN posts p ON p.id = t.post_id
                WHERE t.source='post' AND t.category=? AND t.matched_term=?
                  AND t.subreddit IN ({sub_ph})
                  AND (p.author IS NULL OR p.author NOT IN ({exc_ph}))""",
            [theme, term, *eligible, *excl],
        ).fetchall()
        picked = rows if len(rows) <= N else rng.sample(rows, N)
        rng.shuffle(picked)
        items = []
        for row in picked:
            sid += 1
            s = f"ID-{sid:04d}"
            items.append((s, row))
            manifest[s] = {"theme": theme, "term": term, "post_id": row["id"],
                           "year": str(row["post_date"])[:4]}
        slug = term.replace(" ", "_")
        chunks = [items[i:i + CHUNK] for i in range(0, len(items), CHUNK)]
        note = (f"Confirmatory n=100 read. All posts here were tagged by ONE "
                f"production keyword; code each fresh on the text alone.")
        for ci, chunk in enumerate(chunks, 1):
            name = f"batch_confirm_{slug}_{ci:02d}"
            body = precision_header(theme, tdefs, note).replace("{BATCH}", name)
            for s, row in chunk:
                body += post_entry(s, row, BODY_CHARS)
            (OUTDIR / "batches" / f"{name}.md").write_text(body, encoding="utf-8")
            batches[f"{name}.md"] = [s for s, _ in chunk]
        print(f"{theme}/{term}: {len(picked)} posts, {len(chunks)} batches")

    conn.close()
    (OUTDIR / "confirm_manifest.json").write_text(
        json.dumps({"seed": SEED, "targets": TARGETS, "batches": batches,
                    "samples": manifest}, indent=1), encoding="utf-8")
    print(f"total batches: {len(batches)}  ->  {OUTDIR/'batches'}")


if __name__ == "__main__":
    main()
