#!/usr/bin/env python3
"""Score the 6-layer keyword context spot-check audit.

Inputs (under spotcheck_2026-05-15/):
  manifest.json            sample_id -> metadata
  results/*_results.txt    agent dual-rubric verdicts
  gold_sheet.md            human-filled Verdict: lines (the gold anchor)

Outputs:
  scored_stats.json        machine-readable aggregates
  scored_summary.md        human-readable tables

Computes: per-keyword precision (topical/strict), volume-weighted per-theme
precision bands, precision[theme x year] temporal series, single-keyword
fragility split, comment precision, negative-space recall-miss rate,
event-spike coherence, and gold-anchor calibration (human vs each rubric).
"""
from __future__ import annotations

import json
import math
import re
import sqlite3
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
DB = ROOT / "data" / "tracker.db"
OUTDIR = Path(__file__).parent / "spotcheck_2026-05-15"
THEMES = ["therapy", "consciousness", "addiction", "romance", "sexual_erp", "rupture"]


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float] | None:
    """Return (lower, upper) Wilson bounds for k successes in n trials."""
    if n <= 0:
        return None
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    m = z * math.sqrt((p * (1 - p) + z * z / (4 * n)) / n)
    return ((c - m) / d, (c + m) / d)


def pct(k: int, n: int) -> float | None:
    return round(100 * k / n, 1) if n else None


# ----------------------------------------------------------------------
# parse agent result files
# ----------------------------------------------------------------------
def parse_results() -> tuple[dict, dict]:
    """Return (precision_verdicts, negspace_verdicts).

    precision_verdicts[sid] = {topical, strict, fp}
    negspace_verdicts[sid]  = {themes:set, ai_referent}
    """
    prec, neg = {}, {}
    rdir = OUTDIR / "results"
    if not rdir.exists():
        return prec, neg
    for f in sorted(rdir.glob("*_results.txt")):
        for line in f.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            m_id = re.search(r"\b((?:ID|CM)-\d{4})\b", line)
            m_ns = re.search(r"\b(NS-\d{4})\b", line)
            if m_id:
                top = re.search(r"topical\s*=\s*(\w+)", line, re.I)
                strc = re.search(r"strict\s*=\s*(\w+)", line, re.I)
                fp = re.search(r"fp\s*=\s*([\w-]+)", line, re.I)
                if top and strc:
                    prec[m_id.group(1)] = {
                        "topical": top.group(1).upper()[:4],
                        "strict": strc.group(1).upper()[:4],
                        "fp": (fp.group(1) if fp else "-"),
                        "file": f.name,
                    }
            elif m_ns:
                th = re.search(r"themes\s*=\s*([a-z_,]+)", line, re.I)
                ai = re.search(r"ai_referent\s*=\s*(\w+)", line, re.I)
                themes = set()
                if th and th.group(1).lower() != "none":
                    themes = {t for t in re.split(r"[,\s]+", th.group(1).lower()) if t in THEMES}
                neg[m_ns.group(1)] = {
                    "themes": themes,
                    "ai_referent": (ai.group(1).upper() if ai else "?"),
                    "file": f.name,
                }
    return prec, neg


def parse_gold() -> dict:
    """Return {sid: verdict} from human-filled gold_sheet.md."""
    gold = {}
    path = OUTDIR / "gold_sheet.md"
    if not path.exists():
        return gold
    cur = None
    for line in path.read_text(encoding="utf-8").splitlines():
        h = re.match(r"##\s+(ID-\d{4})\s", line)
        if h:
            cur = h.group(1)
            continue
        v = re.match(r"Verdict:\s*(\w+)", line.strip())
        if v and cur:
            gold[cur] = v.group(1).upper()[:4]
            cur = None
    return gold


def is_yes(v: str) -> bool:
    return v == "YES"


# ----------------------------------------------------------------------
def main() -> None:
    manifest = json.loads((OUTDIR / "manifest.json").read_text())
    samples = manifest["samples"]
    prec, neg = parse_results()
    gold = parse_gold()

    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    vol_post = {(r["category"], r["matched_term"]): r["n"] for r in conn.execute(
        "SELECT category, matched_term, COUNT(DISTINCT post_id) n "
        "FROM post_keyword_tags WHERE source='post' GROUP BY category, matched_term")}
    conn.close()

    stats: dict = {"coverage": {}, "per_keyword": {}, "per_theme": {},
                   "per_theme_year": {}, "fragility": {}, "comments": {},
                   "negspace": {}, "event_spikes": {}, "gold": {}}

    # ---- coverage -----------------------------------------------------
    want_prec = [s for s, m in samples.items() if m["kind"] in ("precision", "event")]
    want_com = [s for s, m in samples.items() if m["kind"] == "comment"]
    want_neg = [s for s, m in samples.items() if m["kind"] == "negspace"]
    stats["coverage"] = {
        "precision_items": len(want_prec),
        "precision_coded": sum(1 for s in want_prec if s in prec),
        "comment_items": len(want_com),
        "comment_coded": sum(1 for s in want_com if s in prec),
        "negspace_items": len(want_neg),
        "negspace_coded": sum(1 for s in want_neg if s in neg),
        "gold_items": len(manifest["gold_ids"]),
        "gold_coded": len(gold),
    }

    # ---- per-keyword precision (precision-kind posts only) ------------
    kw_tot: dict = defaultdict(lambda: {"n": 0, "top": 0, "str": 0})
    for sid, m in samples.items():
        if m["kind"] != "precision" or sid not in prec:
            continue
        v = prec[sid]
        for term in m["terms"]:
            if term.startswith("("):
                continue
            key = f"{m['theme']}::{term}"
            kw_tot[key]["n"] += 1
            kw_tot[key]["top"] += is_yes(v["topical"])
            kw_tot[key]["str"] += is_yes(v["strict"])
    for key, d in sorted(kw_tot.items()):
        theme, term = key.split("::", 1)
        wl = wilson(d["top"], d["n"])
        stats["per_keyword"][key] = {
            "theme": theme, "term": term, "n": d["n"],
            "topical_pct": pct(d["top"], d["n"]),
            "strict_pct": pct(d["str"], d["n"]),
            "topical_wilson_lb": round(wl[0] * 100, 1) if wl else None,
            "prod_volume": vol_post.get((theme, term), 0),
        }

    # ---- per-theme volume-weighted precision band ---------------------
    for theme in THEMES:
        num_t = num_s = den = 0.0
        for key, ks in stats["per_keyword"].items():
            if ks["theme"] != theme or ks["topical_pct"] is None:
                continue
            w = ks["prod_volume"]
            den += w
            num_t += w * ks["topical_pct"] / 100
            num_s += w * ks["strict_pct"] / 100
        # unweighted pooled (every precision post once)
        posts = [s for s, m in samples.items()
                 if m["theme"] == theme and m["kind"] in ("precision", "event") and s in prec]
        pt = sum(is_yes(prec[s]["topical"]) for s in posts)
        ps = sum(is_yes(prec[s]["strict"]) for s in posts)
        stats["per_theme"][theme] = {
            "vol_weighted_topical": round(100 * num_t / den, 1) if den else None,
            "vol_weighted_strict": round(100 * num_s / den, 1) if den else None,
            "pooled_n": len(posts),
            "pooled_topical": pct(pt, len(posts)),
            "pooled_strict": pct(ps, len(posts)),
        }

    # ---- precision x year (temporal comparability) --------------------
    for theme in THEMES:
        for yr in ["2023", "2024", "2025", "2026"]:
            posts = [s for s, m in samples.items()
                     if m["theme"] == theme and m["kind"] in ("precision", "event")
                     and m["year"] == yr and s in prec]
            if not posts:
                continue
            pt = sum(is_yes(prec[s]["topical"]) for s in posts)
            ps = sum(is_yes(prec[s]["strict"]) for s in posts)
            stats["per_theme_year"][f"{theme}::{yr}"] = {
                "n": len(posts), "topical_pct": pct(pt, len(posts)),
                "strict_pct": pct(ps, len(posts))}

    # ---- single-keyword fragility split -------------------------------
    for theme in THEMES:
        for label, cond in (("single_kw", lambda n: n == 1), ("multi_kw", lambda n: n and n > 1)):
            posts = [s for s, m in samples.items()
                     if m["theme"] == theme and m["kind"] == "precision"
                     and cond(m.get("n_kw_theme")) and s in prec]
            if not posts:
                continue
            pt = sum(is_yes(prec[s]["topical"]) for s in posts)
            ps = sum(is_yes(prec[s]["strict"]) for s in posts)
            stats["fragility"][f"{theme}::{label}"] = {
                "n": len(posts), "topical_pct": pct(pt, len(posts)),
                "strict_pct": pct(ps, len(posts))}

    # ---- comment precision per theme ----------------------------------
    for theme in THEMES:
        posts = [s for s, m in samples.items()
                 if m["theme"] == theme and m["kind"] == "comment" and s in prec]
        if not posts:
            continue
        pt = sum(is_yes(prec[s]["topical"]) for s in posts)
        ps = sum(is_yes(prec[s]["strict"]) for s in posts)
        stats["comments"][theme] = {
            "n": len(posts), "topical_pct": pct(pt, len(posts)),
            "strict_pct": pct(ps, len(posts))}

    # ---- negative-space recall-miss rate ------------------------------
    for yr in ["2023", "2024", "2025", "2026"]:
        items = [s for s, m in samples.items()
                 if m["kind"] == "negspace" and m["year"] == yr and s in neg]
        if not items:
            continue
        missed = sum(1 for s in items if neg[s]["themes"])
        theme_ct = defaultdict(int)
        for s in items:
            for t in neg[s]["themes"]:
                theme_ct[t] += 1
        stats["negspace"][yr] = {
            "n": len(items), "with_a_theme": missed,
            "miss_rate_pct": pct(missed, len(items)),
            "by_theme": dict(theme_ct)}

    # ---- event-spike coherence ----------------------------------------
    spike_groups = defaultdict(list)
    for sid, m in samples.items():
        if m["kind"] == "event" and m.get("spike_date") and sid in prec:
            spike_groups[f"{m['theme']}::{m['spike_date']}"].append(sid)
    for key, sids in sorted(spike_groups.items()):
        pt = sum(is_yes(prec[s]["topical"]) for s in sids)
        stats["event_spikes"][key] = {"n": len(sids), "topical_pct": pct(pt, len(sids))}

    # ---- gold calibration: human vs each rubric -----------------------
    if gold:
        common = [s for s in gold if s in prec]
        n = len(common)
        agree_t = sum(1 for s in common if is_yes(gold[s]) == is_yes(prec[s]["topical"]))
        agree_s = sum(1 for s in common if is_yes(gold[s]) == is_yes(prec[s]["strict"]))
        # human-YES base rate; how each rubric deviates
        hy = sum(is_yes(gold[s]) for s in common)
        stats["gold"] = {
            "n_human_coded": len(gold), "n_overlap_with_fleet": n,
            "human_yes": hy, "human_yes_pct": pct(hy, n),
            "topical_agree_pct": pct(agree_t, n),
            "strict_agree_pct": pct(agree_s, n),
            "topical_yes_pct": pct(sum(is_yes(prec[s]["topical"]) for s in common), n),
            "strict_yes_pct": pct(sum(is_yes(prec[s]["strict"]) for s in common), n),
            "disagreements": [
                {"sid": s, "theme": samples[s]["theme"], "human": gold[s],
                 "topical": prec[s]["topical"], "strict": prec[s]["strict"]}
                for s in common
                if is_yes(gold[s]) != is_yes(prec[s]["topical"])
                or is_yes(gold[s]) != is_yes(prec[s]["strict"])],
        }

    (OUTDIR / "scored_stats.json").write_text(json.dumps(stats, indent=1), encoding="utf-8")

    # ---- markdown summary --------------------------------------------
    L = ["# Spot-check scored summary\n"]
    c = stats["coverage"]
    L.append(f"Coverage: precision {c['precision_coded']}/{c['precision_items']}, "
             f"comments {c['comment_coded']}/{c['comment_items']}, "
             f"negspace {c['negspace_coded']}/{c['negspace_items']}, "
             f"gold {c['gold_coded']}/{c['gold_items']}\n")
    L.append("\n## Per-theme precision band (volume-weighted)\n")
    L.append("| Theme | topical | strict | pooled n |")
    L.append("|---|--:|--:|--:|")
    for t in THEMES:
        d = stats["per_theme"].get(t, {})
        L.append(f"| {t} | {d.get('vol_weighted_topical')}% | "
                 f"{d.get('vol_weighted_strict')}% | {d.get('pooled_n')} |")
    L.append("\n## Precision x year (temporal comparability)\n")
    L.append("| Theme | 2023 | 2024 | 2025 | 2026 |")
    L.append("|---|--:|--:|--:|--:|")
    for t in THEMES:
        cells = []
        for yr in ["2023", "2024", "2025", "2026"]:
            d = stats["per_theme_year"].get(f"{t}::{yr}")
            cells.append(f"{d['topical_pct']}% (n{d['n']})" if d else "—")
        L.append(f"| {t} | " + " | ".join(cells) + " |")
    L.append("\n## Lowest per-keyword topical precision (n>=8)\n")
    L.append("| Theme | keyword | n | topical | strict | Wilson LB | prod vol |")
    L.append("|---|---|--:|--:|--:|--:|--:|")
    rows = [v for v in stats["per_keyword"].values() if v["n"] >= 8]
    for v in sorted(rows, key=lambda x: (x["topical_pct"] or 0))[:20]:
        L.append(f"| {v['theme']} | `{v['term']}` | {v['n']} | {v['topical_pct']}% | "
                 f"{v['strict_pct']}% | {v['topical_wilson_lb']}% | {v['prod_volume']} |")
    L.append("\n## Single-keyword fragility\n")
    L.append("| Theme | single-kw topical | multi-kw topical |")
    L.append("|---|--:|--:|")
    for t in THEMES:
        s1 = stats["fragility"].get(f"{t}::single_kw", {})
        s2 = stats["fragility"].get(f"{t}::multi_kw", {})
        L.append(f"| {t} | {s1.get('topical_pct')}% (n{s1.get('n')}) | "
                 f"{s2.get('topical_pct')}% (n{s2.get('n')}) |")
    L.append("\n## Comment precision\n| Theme | topical | strict | n |\n|---|--:|--:|--:|")
    for t in THEMES:
        d = stats["comments"].get(t, {})
        L.append(f"| {t} | {d.get('topical_pct')}% | {d.get('strict_pct')}% | {d.get('n')} |")
    L.append("\n## Negative-space recall-miss rate\n| Year | n | has-a-theme | miss rate |\n|---|--:|--:|--:|")
    for yr in ["2023", "2024", "2025", "2026"]:
        d = stats["negspace"].get(yr, {})
        L.append(f"| {yr} | {d.get('n')} | {d.get('with_a_theme')} | {d.get('miss_rate_pct')}% |")
    if stats["gold"]:
        g = stats["gold"]
        L.append("\n## Gold-anchor calibration\n")
        L.append(f"- Human coded: {g['n_human_coded']}, overlap with fleet: {g['n_overlap_with_fleet']}")
        L.append(f"- Human YES rate: {g['human_yes_pct']}%")
        L.append(f"- Topical rubric: {g['topical_yes_pct']}% YES, agrees with human {g['topical_agree_pct']}%")
        L.append(f"- Strict rubric: {g['strict_yes_pct']}% YES, agrees with human {g['strict_agree_pct']}%")
        L.append(f"- Disagreement cases: {len(g['disagreements'])}")
    (OUTDIR / "scored_summary.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("wrote scored_stats.json and scored_summary.md")
    print(f"coverage: {stats['coverage']}")


if __name__ == "__main__":
    main()
