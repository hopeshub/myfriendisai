#!/usr/bin/env python3
"""Score the theme-level re-measurement (romance, rupture, sexual_erp, addiction).

Each theme was sampled directly from its tagged posts, so YES/(YES+NO) over the
sample IS the theme line's topical precision — no per-keyword reconstruction.
Reports topical + strict precision with a Wilson 95% CI, vs the 2026-05-15
audit's volume-weighted (n=20-screen) figure.
"""
from __future__ import annotations

import json
import math
import re
from pathlib import Path

DIR = Path(__file__).parent / "theme_recheck_2026-05-16"
LINE = re.compile(r"(ID-\d+)\s*\|\s*topical=(\w+)\s*\|\s*strict=(\w+)")

# 2026-05-15 audit volume-weighted topical precision (for comparison)
AUDIT = {"romance": 75, "rupture": 78, "sexual_erp": 93, "addiction": 90}


def wilson(y: int, n: int) -> tuple[float, float]:
    if n == 0:
        return (0.0, 0.0)
    p, z = y / n, 1.96
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (100 * (c - h), 100 * (c + h))


def main() -> None:
    man = json.loads((DIR / "theme_recheck_manifest.json").read_text())
    v = {}
    for f in sorted((DIR / "results").glob("*_results.txt")):
        for ln in f.read_text(errors="replace").splitlines():
            m = LINE.search(ln)
            if m:
                v[m.group(1)] = (m.group(2)[:3].upper(), m.group(3)[:3].upper())

    by_theme: dict[str, list] = {}
    for sid, s in man["samples"].items():
        if sid in v:
            by_theme.setdefault(s["theme"], []).append(v[sid])

    print(f"{'theme':12s} {'n':>4s} {'topical':>8s} {'95% CI':>13s} "
          f"{'strict':>7s}   audit-2026-05-15")
    print("-" * 64)
    for theme in man["themes"]:
        verds = by_theme.get(theme, [])
        ty = sum(t == "YES" for t, _ in verds)
        tn = sum(t == "NO" for t, _ in verds)
        sy = sum(s == "YES" for _, s in verds)
        sn = sum(s == "NO" for _, s in verds)
        tp = 100 * ty / (ty + tn) if (ty + tn) else 0
        sp = 100 * sy / (sy + sn) if (sy + sn) else 0
        lo, hi = wilson(ty, ty + tn)
        au = AUDIT[theme]
        delta = tp - au
        print(f"{theme:12s} {len(verds):4d} {tp:7.1f}% {lo:5.1f}-{hi:4.1f}% "
              f"{sp:6.1f}%   was {au}%  ({delta:+.0f})")


if __name__ == "__main__":
    main()
