#!/usr/bin/env python3
"""Score the human gold anchor — calibrate the LLM rounds against human truth.

Compares the human verdicts to (a) my census round and (b) the original audit
round, on the same posts. The human–LLM gap is the calibration: it says how
many points to discount each LLM round's precision numbers.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

KP = Path(__file__).parent
GA = KP / "gold_anchor_2026-05-16"


def main() -> None:
    j = json.loads((GA / "gold_anchor.json").read_text())
    items = {x["gold_id"]: x for x in j["items"]}

    # human verdicts
    human: dict[str, str] = {}
    removed = []
    for ln in (GA / "human_verdicts.txt").read_text().splitlines():
        m = re.match(r"(G\d+)\s*\|\s*(\w+)", ln)
        if not m:
            continue
        gid, v = m.group(1), m.group(2).upper()
        if v.startswith("REMOV"):
            removed.append(gid)
        else:
            human[gid] = v[:3]

    def norm(v):
        if not v:
            return None
        v = v.upper()[:3]
        return {"YES": "YES", "NO": "NO", "BOR": "BORD"}.get(v)

    def precision(verds):  # YES/(YES+NO), BORD excluded
        y = sum(v == "YES" for v in verds)
        n = sum(v == "NO" for v in verds)
        return 100.0 * y / (y + n) if (y + n) else 0.0, y, n

    print(f"coded: {len(human)}   removed: {len(removed)} {removed}\n")

    for scope, themes in [("ALL", None), ("therapy", "therapy"),
                          ("consciousness", "consciousness")]:
        gids = [g for g in human
                if themes is None or items[g]["theme"] == themes]
        h = [human[g] for g in gids]
        mine = [norm(items[g]["_my_verdict"]) for g in gids]
        hp, hy, hn = precision(h)
        mp, my_, mn = precision(mine)
        print(f"=== {scope}  (n={len(gids)}) ===")
        print(f"  human precision : {hp:5.1f}%  ({hy} YES / {hn} NO)")
        print(f"  my-census round : {mp:5.1f}%  ({my_} YES / {mn} NO)")
        print(f"  -> my round runs {mp-hp:+.1f} pts vs human")
        # agreement on shared posts
        pairs = [(a, b) for a, b in zip(h, mine) if b]
        agree = sum(a == b for a, b in pairs)
        hy_my = sum(a == "NO" and b == "YES" for a, b in pairs)
        my_hy = sum(a == "YES" and b == "NO" for a, b in pairs)
        print(f"  agreement: {agree}/{len(pairs)} ({100*agree/len(pairs):.0f}%)"
              f"   my=YES/human=NO: {hy_my}   my=NO/human=YES: {my_hy}")
        print()

    # original audit round — only the subset with an audit verdict
    aud = [(human[g], norm(items[g]["_audit_verdict"]))
           for g in human if items[g]["_audit_verdict"]]
    if aud:
        h = [a for a, _ in aud]
        a = [b for _, b in aud]
        hp, _, _ = precision(h)
        ap, _, _ = precision(a)
        agree = sum(x == y for x, y in zip(h, a))
        print(f"=== original AUDIT round overlap (n={len(aud)}) ===")
        print(f"  human precision : {hp:5.1f}%")
        print(f"  audit round     : {ap:5.1f}%")
        print(f"  -> audit round runs {ap-hp:+.1f} pts vs human")
        print(f"  agreement: {agree}/{len(aud)} ({100*agree/len(aud):.0f}%)")


if __name__ == "__main__":
    main()
