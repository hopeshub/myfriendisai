#!/usr/bin/env python3
"""Recompute therapy + consciousness volume-weighted precision from censuses.

Pulls per-keyword topical precision, preferring (in order): full census from
this program's runs > n=100 confirmatory read > n=20 audit screen. Reports each
theme's volume-weighted topical precision under that best-available data, and
the projected rebuilt therapy line after the recommended keyword changes.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

KP = Path(__file__).parent
LINE = re.compile(r"(ID-\d+)\s*\|\s*topical=(\w+)\s*\|\s*strict=(\w+)")


def verds(results_dir: Path) -> dict[str, tuple[str, str]]:
    v = {}
    for f in sorted(results_dir.glob("*_results.txt")):
        for ln in f.read_text(errors="replace").splitlines():
            m = LINE.search(ln)
            if m:
                v[m.group(1)] = (m.group(2)[:3].upper(), m.group(3)[:3].upper())
    return v


def census_precision(manifest_path: Path, results_dir: Path) -> dict:
    """term -> (n, topical_pct, strict_pct) from a census run."""
    man = json.loads(manifest_path.read_text())
    v = verds(results_dir)
    sid_of = {s["post_id"]: sid for sid, s in man["samples"].items()}
    cands = man["candidates"]
    # candidates may be {theme: {term: ids}} or {term: ids}
    flat = {}
    for k, val in cands.items():
        if isinstance(val, dict):
            flat.update(val)
        else:
            flat[k] = val
    out = {}
    for term, pids in flat.items():
        ty = tn = sy = sn = 0
        for pid in pids:
            vd = v.get(sid_of.get(pid, ""))
            if not vd:
                continue
            t, s = vd
            ty += t == "YES"; tn += t == "NO"
            sy += s == "YES"; sn += s == "NO"
        tp = 100.0 * ty / (ty + tn) if (ty + tn) else 0.0
        sp = 100.0 * sy / (sy + sn) if (sy + sn) else 0.0
        out[term] = (len(pids), round(tp, 1), round(sp, 1))
    return out


# best-available per-keyword topical precision
# census = this program; conf = original n=100 confirmatory; screen = n=20 audit
gate = census_precision(
    KP / "gate_census_2026-05-16" / "gate_census_manifest.json",
    KP / "gate_census_2026-05-16" / "results")
cremain = census_precision(
    KP / "consc_census_2026-05-16" / "consc_census_manifest.json",
    KP / "consc_census_2026-05-16" / "results")

CONSC_VOL = {"personhood": 124, "selfhood": 96, "subjective experience": 72,
             "inner life": 40, "has a soul": 37, "more than code": 34,
             "tulpa": 29, "lemoine": 19, "not just an ai": 17,
             "sapience": 14, "soulbonder": 14}
THER_VOL = {"emotional support": 571, "therapeutic": 328, "coping mechanism": 252,
            "for therapy": 109, "as a therapist": 66, "ai therapist": 53,
            "free therapy": 29, "ai therapy": 24}
# therapy keywords with no census this program — n=20 audit screen
THER_SCREEN = {"for therapy": 90, "as a therapist": 75, "ai therapist": 90,
               "free therapy": 90, "ai therapy": 65}
THER_CONF = {"emotional support": 56, "therapeutic": 55}  # original n=100


def wvg(vols: dict, prec: dict) -> float:
    tv = sum(vols.values())
    return sum(vols[k] * prec[k] for k in vols) / tv


def main() -> None:
    print("=== CONSCIOUSNESS — all 11 keywords, full census ===")
    cp = {}
    for k in CONSC_VOL:
        src = gate.get(k) or cremain.get(k)
        cp[k] = src[1]
        print(f"  {k:24s} vol={CONSC_VOL[k]:4d}  census topical={src[1]:5.1f}% "
              f"(n={src[0]})")
    print(f"  -> volume-weighted topical precision: {wvg(CONSC_VOL, cp):.1f}%")
    cut = {k: v for k, v in CONSC_VOL.items() if k != "not just an ai"}
    cpc = {k: cp[k] for k in cut}
    print(f"  -> after cutting 'not just an ai' (47%): {wvg(cut, cpc):.1f}%")

    print()
    print("=== THERAPY — best-available per-keyword topical precision ===")
    tp = {}
    for k in THER_VOL:
        if k == "coping mechanism":
            tp[k] = gate["coping mechanism"][1]; src = "census n=253"
        elif k in THER_CONF:
            tp[k] = THER_CONF[k]; src = "n=100 confirm"
        else:
            tp[k] = THER_SCREEN[k]; src = "n=20 screen"
        print(f"  {k:24s} vol={THER_VOL[k]:4d}  topical={tp[k]:5.1f}%  ({src})")
    print(f"  -> current volume-weighted topical precision: {wvg(THER_VOL, tp):.1f}%")

    # rebuilt: cut emotional support + therapeutic, add 15 census KEEP keywords
    keep = {k: v for k, v in THER_VOL.items()
            if k not in ("emotional support", "therapeutic")}
    keepp = {k: tp[k] for k in keep}
    base_v = sum(keep.values()); base_clean = sum(keep[k] * keepp[k] / 100
                                                  for k in keep)
    NEW_VOL, NEW_PREC = 170, 84.0  # 15 KEEP census candidates (Lever 1)
    reb_v = base_v + NEW_VOL
    reb_clean = base_clean + NEW_VOL * NEW_PREC / 100
    print(f"  -> REBUILT line (cut emotional support + therapeutic, add 15 "
          f"Lever-1 census keywords):")
    print(f"     volume {reb_v:.0f} (~{reb_v/sum(THER_VOL.values())*100:.0f}% "
          f"of current), volume-weighted topical precision "
          f"{reb_clean/reb_v*100:.1f}%")


if __name__ == "__main__":
    main()
