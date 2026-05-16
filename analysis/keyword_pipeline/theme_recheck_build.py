#!/usr/bin/env python3
"""Re-measure the four un-rechecked themes by direct theme-level sampling.

The 2026-05-15 audit built each theme's precision by volume-weighting ~20-post
per-keyword screens — and those screens were shown (by the therapy/consciousness
census + gold anchor) to carry ±10-25-pt error that ran systematically low.
The clean fix is not more per-keyword sampling: it is to draw a random sample
directly from each theme's tagged posts and classify it. That measures the
chart line itself, with one honest confidence interval, no reconstruction.

For romance / rupture / sexual_erp / addiction: random N posts from the unique
post-source tags in active keyword communities, blind dual-rubric batches.
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
    DB, BODY_CHARS, load_theme_defs, precision_header, post_entry,
)

SEED = 20260516
N = 240
CHUNK = 40
OUTDIR = THISDIR / "theme_recheck_2026-05-16"
THEMES = ["romance", "rupture", "sexual_erp", "addiction"]


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

    manifest = {"seed": SEED, "audit_date": "2026-05-16", "n_per_theme": N,
                "themes": THEMES, "samples": {}, "batches": {}, "pool": {}}
    sid_n = 8000
    all_batches: dict[str, list[str]] = {}

    for theme in THEMES:
        pool = [r[0] for r in conn.execute(
            f"""SELECT DISTINCT t.post_id
                FROM post_keyword_tags t
                JOIN posts p ON p.id = t.post_id
                WHERE t.category = ?
                  AND t.source = 'post'
                  AND p.subreddit IN ({sub_ph})
                  AND (p.author IS NULL OR p.author NOT IN ({exc_ph}))""",
            [theme, *eligible, *excl])]
        manifest["pool"][theme] = len(pool)
        pool = sorted(pool)
        rng.shuffle(pool)
        picked = pool[:N]

        rows = {}
        for pid in picked:
            r = conn.execute(
                "SELECT id, subreddit, title, selftext, "
                "date(created_utc,'unixepoch') post_date FROM posts WHERE id=?",
                (pid,)).fetchone()
            if r:
                rows[pid] = r
        picked = [p for p in picked if p in rows]
        rng.shuffle(picked)

        sid_of = {}
        for pid in picked:
            s = f"ID-{sid_n}"
            sid_n += 1
            sid_of[pid] = s
            manifest["samples"][s] = {"post_id": pid, "theme": theme}

        note = (f"Theme-level re-measurement. Every post here is currently "
                f"tagged {theme}; you are checking, blind, whether that tag is "
                f"right. Code each post fresh on its text alone.")
        chunks = [picked[i:i + CHUNK] for i in range(0, len(picked), CHUNK)]
        for ci, chunk in enumerate(chunks, 1):
            name = f"batch_recheck_{theme[:4]}_{ci:02d}"
            body = precision_header(theme, tdefs, note).replace("{BATCH}", name)
            body = body.replace("spotcheck_2026-05-15/results",
                                "theme_recheck_2026-05-16/results")
            for pid in chunk:
                body += post_entry(sid_of[pid], rows[pid], BODY_CHARS)
            (OUTDIR / "batches" / f"{name}.md").write_text(body, encoding="utf-8")
            all_batches[f"{name}.md"] = [sid_of[pid] for pid in chunk]
        print(f"[{theme:11s}] pool={len(pool):5d}  sampled={len(picked)}  "
              f"batches={len(chunks)}")

    conn.close()
    manifest["batches"] = all_batches
    (OUTDIR / "theme_recheck_manifest.json").write_text(
        json.dumps(manifest, indent=1), encoding="utf-8")
    print(f"total batches: {len(all_batches)} -> {OUTDIR}/batches")


if __name__ == "__main__":
    main()
