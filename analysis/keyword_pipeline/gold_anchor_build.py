#!/usr/bin/env python3
"""Build the 72-post human gold-anchor sample.

Purpose: the overlap test found my census round codes ~11 points more lenient
than the original audit round, on identical posts. Neither round has ground
truth. This draws a stratified random sample of MY census posts (therapy +
consciousness) for a human to code blind. Human verdicts then calibrate my
round directly; for the subset also in the original audit, both rounds at once.

Output: gold_anchor_2026-05-16/gold_anchor.json — carries the post text plus,
hidden, each round's verdict. The human coder must not see the hidden verdicts.
"""
from __future__ import annotations

import json
import random
import re
import sqlite3
from pathlib import Path

KP = Path(__file__).parent
ROOT = KP.parent.parent
DB = ROOT / "data" / "tracker.db"
OUT = KP / "gold_anchor_2026-05-16"
SEED = 20260516
PER_THEME = 36
LINE = re.compile(r"(ID-\d+)\s*\|\s*topical=(\w+)")


def verds(rdir: Path) -> dict[str, str]:
    v = {}
    for f in sorted(rdir.glob("*_results.txt")):
        for ln in f.read_text(errors="replace").splitlines():
            m = LINE.search(ln)
            if m:
                v[m.group(1)] = m.group(2)[:3].upper()
    return v


def main() -> None:
    rng = random.Random(SEED)
    OUT.mkdir(parents=True, exist_ok=True)

    # my census rounds: post_id -> (theme, my topical verdict)
    mine: dict[str, tuple[str, str]] = {}
    for d, mf in [("therapy_census_2026-05-16", "census_manifest.json"),
                  ("gate_census_2026-05-16", "gate_census_manifest.json"),
                  ("consc_census_2026-05-16", "consc_census_manifest.json")]:
        man = json.loads((KP / d / mf).read_text())
        mv = verds(KP / d / "results")
        for sid, s in man["samples"].items():
            if sid in mv:
                mine.setdefault(s["post_id"], (s["theme"], mv[sid]))

    # original audit: post_id -> topical verdict
    sc = KP / "spotcheck_2026-05-15"
    ov = verds(sc / "results")
    audit: dict[str, str] = {}
    for mf in ["manifest.json", "confirm_manifest.json"]:
        p = sc / mf
        if not p.exists():
            continue
        man = json.loads(p.read_text())
        for sid, s in man["samples"].items():
            if sid in ov:
                audit.setdefault(s["post_id"], ov[sid])

    by_theme: dict[str, list[str]] = {"therapy": [], "consciousness": []}
    for pid, (theme, _) in mine.items():
        if theme in by_theme:
            by_theme[theme].append(pid)

    picked: list[tuple[str, str]] = []  # (post_id, theme)
    for theme, pids in by_theme.items():
        pids = sorted(pids)
        rng.shuffle(pids)
        picked += [(p, theme) for p in pids[:PER_THEME]]
    rng.shuffle(picked)

    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    items = []
    for i, (pid, theme) in enumerate(picked, 1):
        r = conn.execute(
            "SELECT subreddit, title, selftext, "
            "date(created_utc,'unixepoch') d FROM posts WHERE id=?",
            (pid,)).fetchone()
        if not r:
            continue
        items.append({
            "gold_id": f"G{i:02d}",
            "post_id": pid,
            "theme": theme,
            "subreddit": r["subreddit"],
            "date": r["d"],
            "title": r["title"] or "(no title)",
            "body": r["selftext"] or "(no body — image/link/removed)",
            "_my_verdict": mine[pid][1],
            "_audit_verdict": audit.get(pid, None),
            "human_verdict": None,
        })
    conn.close()

    (OUT / "gold_anchor.json").write_text(
        json.dumps({"seed": SEED, "n": len(items),
                    "in_audit": sum(1 for x in items if x["_audit_verdict"]),
                    "items": items}, indent=1), encoding="utf-8")
    print(f"gold sample: {len(items)} posts "
          f"({sum(1 for x in items if x['theme']=='therapy')} therapy, "
          f"{sum(1 for x in items if x['theme']=='consciousness')} consciousness)")
    print(f"also in original audit (calibrates both rounds): "
          f"{sum(1 for x in items if x['_audit_verdict'])}")
    print(f"-> {OUT / 'gold_anchor.json'}")


if __name__ == "__main__":
    main()
