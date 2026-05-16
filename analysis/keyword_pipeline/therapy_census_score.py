#!/usr/bin/env python3
"""Score the therapy census validation (Lever 1).

Reads the census manifest + the agents' results, computes per-candidate
precision over the FULL match population (census — no sampling error), and
tallies the clean new therapy volume recoverable from candidates that clear
the 80% topical KEEP gate.
"""
from __future__ import annotations

import json
import re
import sqlite3
import sys
from pathlib import Path

THISDIR = Path(__file__).parent
DIR = THISDIR / "therapy_census_2026-05-16"
ROOT = THISDIR.parent.parent
DB = ROOT / "data" / "tracker.db"
GATE = 80.0

LINE = re.compile(r"(ID-\d+)\s*\|\s*topical=(\w+)\s*\|\s*strict=(\w+)")


def load_verdicts() -> dict[str, tuple[str, str]]:
    v: dict[str, tuple[str, str]] = {}
    for f in sorted((DIR / "results").glob("*_results.txt")):
        for ln in f.read_text(errors="replace").splitlines():
            m = LINE.search(ln)
            if m:
                v[m.group(1)] = (m.group(2)[:3].upper(), m.group(3)[:3].upper())
    return v


def pct(yes: int, no: int) -> float:
    return 100.0 * yes / (yes + no) if (yes + no) else 0.0


def main() -> None:
    man = json.loads((DIR / "census_manifest.json").read_text())
    verdicts = load_verdicts()
    # post_id -> sample_id
    sid_of = {s["post_id"]: sid for sid, s in man["samples"].items()}
    new_vol = man["new_volume_by_candidate"]

    # which posts already carry a therapy tag
    conn = sqlite3.connect(DB)
    tagged = {r[0] for r in conn.execute(
        "SELECT DISTINCT post_id FROM post_keyword_tags "
        "WHERE category='therapy' AND source='post'")}
    conn.close()

    print(f"{'candidate':22s} {'n':>4s} {'topYES':>6s} {'top%':>6s} "
          f"{'strict%':>7s} {'newY':>5s} {'verdict':>9s}")
    print("-" * 70)

    keep_new_posts: set[str] = set()       # union of new clean posts (KEEP cands)
    review_new_posts: set[str] = set()
    rows = []
    for term, post_ids in man["candidates"].items():
        ty = tn = tb = sy = sn = 0
        new_yes = []  # new (untagged) posts coded topical YES
        for pid in post_ids:
            sid = sid_of.get(pid)
            vd = verdicts.get(sid) if sid else None
            if not vd:
                continue
            top, strict = vd
            if top == "YES":
                ty += 1
                if pid not in tagged:
                    new_yes.append(pid)
            elif top == "NO":
                tn += 1
            else:
                tb += 1
            if strict == "YES":
                sy += 1
            elif strict == "NO":
                sn += 1
        topp, strictp = pct(ty, tn), pct(sy, sn)
        n = len(post_ids)
        if topp >= GATE:
            verdict = "KEEP"
            keep_new_posts.update(new_yes)
        elif topp >= 60:
            verdict = "REVIEW"
            review_new_posts.update(new_yes)
        else:
            verdict = "CUT"
        rows.append((term, n, ty, topp, strictp, len(new_yes), verdict))

    for term, n, ty, topp, strictp, ny, verdict in sorted(
            rows, key=lambda r: -r[3]):
        print(f"{term:22s} {n:4d} {ty:6d} {topp:5.0f}% {strictp:6.0f}% "
              f"{ny:5d} {verdict:>9s}")

    print("-" * 70)
    keep = [r for r in rows if r[6] == "KEEP"]
    review = [r for r in rows if r[6] == "REVIEW"]
    print(f"KEEP   (>= {GATE:.0f}% topical): {len(keep)} candidates "
          f"-> {sorted(r[0] for r in keep)}")
    print(f"REVIEW (60-79% topical):    {len(review)} candidates "
          f"-> {sorted(r[0] for r in review)}")
    print(f"CUT    (< 60% topical):     "
          f"{len([r for r in rows if r[6]=='CUT'])} candidates")
    print()
    print(f"Clean NEW therapy volume from KEEP candidates "
          f"(dedup union): {len(keep_new_posts)} posts")
    print(f"  + if REVIEW candidates also admitted (dedup union, KEEP+REVIEW): "
          f"{len(keep_new_posts | review_new_posts)} posts")
    print()
    print("Context: therapy currently carries ~1,426 post-only tags. Recovered "
          "clean volume offsets the volume lost when cutting noisy keywords.")


if __name__ == "__main__":
    main()
