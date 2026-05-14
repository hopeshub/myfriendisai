#!/usr/bin/env python3
"""Paired comparison: Haiku v2 vs Sonnet on the n=900 v2 sample.

Inputs:
  - Agent gold (calibration_v2_2026-05-14_results.txt)
  - Haiku verdicts (llm_verdicts_v2_claude-haiku-4-5-20251001_2026-05-14.json)
  - Sonnet verdicts (llm_verdicts_v2_claude-sonnet-4-6_2026-05-14.json)

Output: per-model agreement, McNemar's test for paired comparison,
recommendation.
"""

import json
import math
import re
from collections import defaultdict
from pathlib import Path

RESULTS = Path("/Users/walker/Projects/myfriendisai/analysis/keyword_pipeline/results")
DATE = "2026-05-14"


def wilson(k, n, z=1.96):
    """Wilson 95% CI for a proportion."""
    if n == 0:
        return (0, 0, 0)
    p = k / n
    denom = 1 + z**2 / n
    center = (p + z**2 / (2 * n)) / denom
    margin = z * math.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / denom
    return p, center - margin, center + margin


def mcnemar(b, c):
    """McNemar's chi-squared. b = A wrong & B right, c = A right & B wrong.
    Returns chi^2 statistic and approximate p-value."""
    if b + c == 0:
        return 0.0, 1.0
    # Continuity-corrected
    chi2 = (abs(b - c) - 1) ** 2 / (b + c)
    # p-value from chi^2 with 1 df
    p = math.erfc(math.sqrt(chi2 / 2))
    return chi2, p


def main():
    # Load agent gold
    line_re = re.compile(r"^\s*(\d+)\s*[\.\)]?\s*(TP|FP)\b", re.IGNORECASE)
    agent = {}
    with open(RESULTS / f"calibration_v2_{DATE}_results.txt") as f:
        for line in f:
            m = line_re.match(line)
            if m:
                agent[int(m.group(1))] = m.group(2).upper()

    # Load truth (idx → theme)
    truth = {}
    with open(RESULTS / f"calibration_v2_{DATE}_llm_truth.json") as f:
        for line in f:
            if line.strip():
                e = json.loads(line)
                truth[e["idx"]] = e

    # Load Haiku and Sonnet verdicts
    def load(model):
        path = RESULTS / f"llm_verdicts_v2_{model}_{DATE}.json"
        if not path.exists():
            print(f"MISSING: {path}")
            return {}
        items = json.loads(path.read_text())
        return {it["idx"]: it["verdict"] for it in items}

    haiku = load("claude-haiku-4-5-20251001")
    sonnet = load("claude-sonnet-4-6")

    print(f"Agent verdicts:  {len(agent)}")
    print(f"Haiku verdicts:  {len(haiku)}")
    print(f"Sonnet verdicts: {len(sonnet)}")
    print()

    # Pair up
    common = set(agent) & set(haiku) & set(sonnet) & set(truth)
    print(f"Items with all four verdicts: {len(common)}\n")

    haiku_correct = sonnet_correct = 0
    h_only_correct = s_only_correct = both_correct = both_wrong = 0
    per_theme_haiku = defaultdict(lambda: {"agree": 0, "total": 0})
    per_theme_sonnet = defaultdict(lambda: {"agree": 0, "total": 0})
    h_conf = defaultdict(int)
    s_conf = defaultdict(int)

    for idx in common:
        a = agent[idx]
        h = haiku[idx]
        s = sonnet[idx]
        theme = truth[idx]["theme"]
        per_theme_haiku[theme]["total"] += 1
        per_theme_sonnet[theme]["total"] += 1
        h_conf[(h, a)] += 1
        s_conf[(s, a)] += 1
        h_correct = h == a
        s_correct = s == a
        if h_correct:
            haiku_correct += 1
            per_theme_haiku[theme]["agree"] += 1
        if s_correct:
            sonnet_correct += 1
            per_theme_sonnet[theme]["agree"] += 1
        if h_correct and s_correct:
            both_correct += 1
        elif h_correct and not s_correct:
            s_only_correct += 1  # Sonnet wrong here (note: this is s WRONG)
        elif s_correct and not h_correct:
            h_only_correct += 1  # Haiku wrong here
        else:
            both_wrong += 1

    n = len(common)
    print(f"=== Overall agreement ===\n")
    h_p, h_lo, h_hi = wilson(haiku_correct, n)
    s_p, s_lo, s_hi = wilson(sonnet_correct, n)
    print(f"  Haiku v2:  {haiku_correct}/{n} = {h_p:.1%}  CI95 [{h_lo:.1%}, {h_hi:.1%}]")
    print(f"  Sonnet v2: {sonnet_correct}/{n} = {s_p:.1%}  CI95 [{s_lo:.1%}, {s_hi:.1%}]")
    print(f"  Δ = {(s_p - h_p) * 100:+.1f} pp\n")

    # Paired (McNemar)
    # b = Haiku wrong & Sonnet right = h_only_correct (i.e., only Sonnet correct)
    # c = Haiku right & Sonnet wrong = s_only_correct (i.e., only Haiku correct)
    # Wait — I named these wrong. Re-derive:
    # When h_correct=True and s_correct=False, "Sonnet wrong here" — this is c (Haiku right, Sonnet wrong)
    # When s_correct=True and h_correct=False, "Haiku wrong here" — this is b (Sonnet right, Haiku wrong)
    # So my counters need re-mapping:
    # h_only_correct above counts (h_correct=False, s_correct=True) → that's b
    # s_only_correct above counts (h_correct=True, s_correct=False) → that's c
    b = h_only_correct  # Sonnet correct, Haiku wrong
    c = s_only_correct  # Haiku correct, Sonnet wrong
    chi2, p_val = mcnemar(b, c)
    print(f"=== Paired comparison (McNemar's test) ===\n")
    print(f"  Both correct:        {both_correct}")
    print(f"  Only Haiku correct:  {c}")
    print(f"  Only Sonnet correct: {b}")
    print(f"  Both wrong:          {both_wrong}")
    print(f"  Chi-squared (continuity-corrected): {chi2:.2f}")
    print(f"  p-value: {p_val:.4f}")
    sig = "SIGNIFICANT" if p_val < 0.05 else "NOT significant"
    print(f"  Difference is {sig} at alpha=0.05\n")

    print(f"=== Per-theme agreement ===\n")
    themes = sorted(per_theme_haiku.keys())
    print(f"  {'theme':14s}  {'Haiku v2':>14s}  {'Sonnet v2':>14s}  {'Δ':>6s}")
    for theme in themes:
        ht = per_theme_haiku[theme]
        st = per_theme_sonnet[theme]
        h_p_t = ht["agree"] / ht["total"] if ht["total"] else 0
        s_p_t = st["agree"] / st["total"] if st["total"] else 0
        print(f"  {theme:14s}  {ht['agree']:>4d}/{ht['total']:<4d} {h_p_t:>5.1%}  "
              f"{st['agree']:>4d}/{st['total']:<4d} {s_p_t:>5.1%}  "
              f"{(s_p_t - h_p_t) * 100:>+5.1f}pp")

    print(f"\n=== Confusion (model verdict × agent verdict) ===\n")
    print(f"  Haiku v2:                              Sonnet v2:")
    print(f"             agent=TP  agent=FP            agent=TP  agent=FP")
    for v in ("TP", "FP"):
        h_tp = h_conf[(v, "TP")]
        h_fp = h_conf[(v, "FP")]
        s_tp = s_conf[(v, "TP")]
        s_fp = s_conf[(v, "FP")]
        print(f"  m={v}     {h_tp:>7d}  {h_fp:>7d}             {s_tp:>7d}  {s_fp:>7d}")

    # FRR and FKR
    h_fp_total = sum(h_conf[("FP", v)] for v in ("TP", "FP"))
    h_tp_total = sum(h_conf[("TP", v)] for v in ("TP", "FP"))
    s_fp_total = sum(s_conf[("FP", v)] for v in ("TP", "FP"))
    s_tp_total = sum(s_conf[("TP", v)] for v in ("TP", "FP"))
    h_frr = h_conf[("FP", "TP")] / h_fp_total if h_fp_total else 0
    h_fkr = h_conf[("TP", "FP")] / h_tp_total if h_tp_total else 0
    s_frr = s_conf[("FP", "TP")] / s_fp_total if s_fp_total else 0
    s_fkr = s_conf[("TP", "FP")] / s_tp_total if s_tp_total else 0
    print(f"\n  FRR (FP-but-actually-TP):  Haiku {h_frr:.1%}    Sonnet {s_frr:.1%}    Δ {(s_frr - h_frr) * 100:+.1f}pp")
    print(f"  FKR (TP-but-actually-FP):  Haiku {h_fkr:.1%}    Sonnet {s_fkr:.1%}    Δ {(s_fkr - h_fkr) * 100:+.1f}pp")

    # Precision on kept items
    h_kept_correct = h_conf[("TP", "TP")]
    h_kept_total = sum(h_conf[("TP", v)] for v in ("TP", "FP"))
    s_kept_correct = s_conf[("TP", "TP")]
    s_kept_total = sum(s_conf[("TP", v)] for v in ("TP", "FP"))
    print(f"\n  Precision on kept items:")
    print(f"    Haiku:  {h_kept_correct}/{h_kept_total} = {h_kept_correct / h_kept_total:.1%}")
    print(f"    Sonnet: {s_kept_correct}/{s_kept_total} = {s_kept_correct / s_kept_total:.1%}")

    # Save
    out = {
        "n": n,
        "haiku_agreement": h_p,
        "sonnet_agreement": s_p,
        "delta_pp": (s_p - h_p) * 100,
        "mcnemar_chi2": chi2,
        "mcnemar_p_value": p_val,
        "significant_at_0.05": p_val < 0.05,
        "haiku_frr": h_frr,
        "sonnet_frr": s_frr,
        "haiku_fkr": h_fkr,
        "sonnet_fkr": s_fkr,
        "haiku_kept_precision": h_kept_correct / h_kept_total if h_kept_total else None,
        "sonnet_kept_precision": s_kept_correct / s_kept_total if s_kept_total else None,
    }
    out_path = RESULTS / f"haiku_vs_sonnet_n900_{DATE}.json"
    out_path.write_text(json.dumps(out, indent=2))
    print(f"\nWrote {out_path}")

    # Decision
    print(f"\n=== RECOMMENDATION ===\n")
    if p_val < 0.05 and (s_p - h_p) > 0.02:
        print(f"  USE SONNET. Significant improvement ({(s_p - h_p) * 100:+.1f}pp, p={p_val:.4f}).")
    elif (s_p - h_p) > 0.03:
        print(f"  Marginal: Sonnet is {(s_p - h_p) * 100:+.1f}pp better but not significant (p={p_val:.4f}).")
        print(f"  Sonnet may still be worth it for FRR improvement ({h_frr:.1%} → {s_frr:.1%}).")
    elif (h_p - s_p) > 0.02:
        print(f"  USE HAIKU. Sonnet shows no improvement ({(s_p - h_p) * 100:+.1f}pp).")
    else:
        print(f"  EITHER. Models are statistically indistinguishable ({(s_p - h_p) * 100:+.1f}pp, p={p_val:.4f}).")
        print(f"  Default to Haiku for cost ($13 vs $39 per backfill).")


if __name__ == "__main__":
    main()
