#!/usr/bin/env python3
"""Score the Lever 2 gate-design census — raw per-keyword precision.

Computes full-census topical/strict precision for each target keyword. This is
the 'before' number: if the census precision already clears 80% topical, the
n=20 audit screen mis-drew and the keyword needs no gate at all.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

THISDIR = Path(__file__).parent
DIR = THISDIR / "gate_census_2026-05-16"
LINE = re.compile(r"(ID-\d+)\s*\|\s*topical=(\w+)\s*\|\s*strict=(\w+)")


def load_verdicts() -> dict[str, tuple[str, str]]:
    v = {}
    for f in sorted((DIR / "results").glob("*_results.txt")):
        for ln in f.read_text(errors="replace").splitlines():
            m = LINE.search(ln)
            if m:
                v[m.group(1)] = (m.group(2)[:3].upper(), m.group(3)[:3].upper())
    return v


def pct(y: int, n: int) -> float:
    return 100.0 * y / (y + n) if (y + n) else 0.0


def main() -> None:
    man = json.loads((DIR / "gate_census_manifest.json").read_text())
    verdicts = load_verdicts()
    sid_of = {s["post_id"]: sid for sid, s in man["samples"].items()}

    print(f"{'keyword':24s} {'theme':13s} {'n':>4s} {'top%':>6s} "
          f"{'strict%':>7s} {'topYES':>7s}")
    print("-" * 64)
    for theme, cands in man["candidates"].items():
        for term, post_ids in cands.items():
            ty = tn = sy = sn = 0
            for pid in post_ids:
                vd = verdicts.get(sid_of.get(pid, ""))
                if not vd:
                    continue
                top, strict = vd
                if top == "YES":
                    ty += 1
                elif top == "NO":
                    tn += 1
                if strict == "YES":
                    sy += 1
                elif strict == "NO":
                    sn += 1
            print(f"{term:24s} {theme:13s} {len(post_ids):4d} "
                  f"{pct(ty,tn):5.0f}% {pct(sy,sn):6.0f}% {ty:7d}")


if __name__ == "__main__":
    main()
