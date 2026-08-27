#!/usr/bin/env python3
"""Corpus composition measurements — Plan B.

Read-only analysis of how the curated subreddit corpus shapes the six theme
lines. Spec: docs/corpus_composition_plan.md.

Mirrors the published methodology: post-source tags only (source='post'),
T1-T3 active subreddits, the one platform-dev author excluded. Monthly buckets.

Run from the repo root:  python3 analysis/keyword_pipeline/corpus_composition.py
"""

import re
import sqlite3
from collections import defaultdict
from pathlib import Path

DB = Path(__file__).resolve().parents[2] / "data" / "tracker.db"
COMMUNITIES_YAML = Path(__file__).resolve().parents[2] / "config" / "communities.yaml"
EXCLUDED_AUTHORS = {"SoulmateAI_Dev"}   # mirrors src/db/operations.py
LAST_COMPLETE_MONTH = "2026-07"         # August 2026 is still in progress
VOLUME_FLOOR = 200                      # min posts/month for a sub to count in sub-equal

THEMES = ["romance", "sexual_erp", "consciousness", "therapy", "addiction", "rupture"]

# Published per-theme start month (coverage_start in data/keyword_trends.json).
# The site shows each line only from here, so robustness is assessed over the
# same span — not over noisy pre-publication data.
COVERAGE_START = {
    "romance": "2022-12", "sexual_erp": "2022-08", "consciousness": "2025-04",
    "therapy": "2023-01", "addiction": "2023-01", "rupture": "2022-12",
}


def pearson(xs, ys):
    n = len(xs)
    if n < 3:
        return float("nan")
    mx, my = sum(xs) / n, sum(ys) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    dx = sum((x - mx) ** 2 for x in xs) ** 0.5
    dy = sum((y - my) ** 2 for y in ys) ** 0.5
    return float("nan") if dx == 0 or dy == 0 else num / (dx * dy)


def months_between(start, end):
    y, m = int(start[:4]), int(start[5:7])
    ey, em = int(end[:4]), int(end[5:7])
    out = []
    while (y, m) <= (ey, em):
        out.append(f"{y:04d}-{m:02d}")
        m += 1
        if m == 13:
            m, y = 1, y + 1
    return out


def keyword_excluded_subs():
    """Subs flagged exclude_from_keywords in communities.yaml, lowercased.

    subreddit_config has no exclusion column, so without this filter the
    corpus silently included r/AIGirlfriend, r/SpicyChatAI and r/ChatGPTNSFW's
    pre-2026-05-18 tags — which the published exports exclude. (Found and
    fixed 2026-08-27; the 2026-05-16 run had the same inflation.) Light line
    parser instead of pyyaml so the script stays dependency-free.
    """
    excluded, current = set(), None
    for line in COMMUNITIES_YAML.read_text().splitlines():
        m = re.match(r"\s*-\s*subreddit:\s*[\"']?([A-Za-z0-9_]+)", line)
        if m:
            current = m.group(1).lower()
        elif re.match(r"\s*exclude_from_keywords:\s*true", line) and current:
            excluded.add(current)
    return excluded


def load(conn):
    """Return (tier, tagged, posts) keyed by lowercased subreddit.

    tier:   sub -> tier (1/2/3), the T1-T3 active corpus
    tagged: theme -> sub -> month -> distinct tagged-post count
    posts:  sub -> month -> total post count
    """
    excluded = keyword_excluded_subs()
    tier = {}
    for sub, t in conn.execute(
        "SELECT subreddit, tier FROM subreddit_config "
        "WHERE is_active=1 AND tier BETWEEN 1 AND 3"
    ):
        if sub.lower() not in excluded:
            tier[sub.lower()] = t
    corpus = set(tier)

    # Distinct tagged posts (post source only), deduped to (theme, sub, month, post).
    seen = set()
    tagged = {th: defaultdict(lambda: defaultdict(int)) for th in THEMES}
    for cat, sub, pdate, pid, author in conn.execute(
        "SELECT t.category, t.subreddit, t.post_date, t.post_id, p.author "
        "FROM post_keyword_tags t JOIN posts p ON p.id = t.post_id "
        "WHERE t.source='post'"
    ):
        s = (sub or "").lower()
        if s not in corpus or cat not in tagged or author in EXCLUDED_AUTHORS:
            continue
        month = pdate[:7]
        key = (cat, s, month, pid)
        if key in seen:
            continue
        seen.add(key)
        tagged[cat][s][month] += 1

    # Total posts per (sub, month) — the denominator population.
    posts = defaultdict(lambda: defaultdict(int))
    for sub, month, c in conn.execute(
        "SELECT subreddit, strftime('%Y-%m', date(created_utc,'unixepoch')), COUNT(*) "
        "FROM posts WHERE created_utc IS NOT NULL GROUP BY 1, 2"
    ):
        s = (sub or "").lower()
        if s in corpus and month and month <= LAST_COMPLETE_MONTH:
            posts[s][month] += c

    return tier, tagged, posts


def theme_window(theme):
    """The theme's published span: coverage_start month to last complete month."""
    return months_between(COVERAGE_START[theme], LAST_COMPLETE_MONTH)


def vol_weighted(tagged_theme, posts, subs, window):
    """Monthly per-1k rate, volume-weighted (current published method)."""
    series = []
    for m in window:
        tag = sum(tagged_theme[s].get(m, 0) for s in subs)
        tot = sum(posts[s].get(m, 0) for s in subs)
        series.append(1000 * tag / tot if tot else 0.0)
    return series


# ── B1: composition matrix ───────────────────────────────────────────────────
def b1(tier, tagged):
    print("\n=== B1. Composition matrix — where each theme's posts come from ===")
    for th in THEMES:
        per_sub = defaultdict(int)
        per_tier = defaultdict(int)
        for s, months in tagged[th].items():
            n = sum(months.values())
            per_sub[s] += n
            per_tier[tier[s]] += n
        total = sum(per_sub.values()) or 1
        top = sorted(per_sub.items(), key=lambda kv: -kv[1])
        top3 = sum(c for _, c in top[:3])
        tiers = " ".join(f"T{t}:{100*per_tier.get(t,0)/total:4.1f}%" for t in (1, 2, 3))
        print(f"\n  {th:13s} {total:5d} posts | {tiers}")
        print(f"    top-1 {100*top[0][1]/total:4.1f}%  top-3 {100*top3/total:4.1f}%")
        for s, c in top[:3]:
            print(f"      r/{s:24s} {c:5d}  {100*c/total:4.1f}%  (T{tier[s]})")


# ── B2: composition drift over time ──────────────────────────────────────────
def b2(tier, posts):
    print("\n\n=== B2. Composition drift — each tier's share of corpus posts ===")
    print("  year     T1      T2      T3")
    by_year = defaultdict(lambda: defaultdict(int))
    for s, months in posts.items():
        for m, c in months.items():
            by_year[m[:4]][tier[s]] += c
    for year in sorted(by_year):
        tot = sum(by_year[year].values()) or 1
        row = "  ".join(f"{100*by_year[year].get(t,0)/tot:5.1f}%" for t in (1, 2, 3))
        print(f"  {year}   {row}")


# ── B3: leave-one-subreddit-out sensitivity ──────────────────────────────────
def b3(tier, tagged, posts):
    print("\n\n=== B3. Leave-one-sub-out — does a line lean on one room? ===")
    for th in THEMES:
        window = theme_window(th)
        if len(window) < 6:
            print(f"\n  {th:13s} window too short ({len(window)} mo) — skipped")
            continue
        subs = list(tier)
        full = vol_weighted(tagged[th], posts, subs, window)
        worst_corr = (1.0, None)
        worst_level = (0.0, None)
        for drop in subs:
            kept = [s for s in subs if s != drop]
            red = vol_weighted(tagged[th], posts, kept, window)
            corr = pearson(full, red)
            if corr == corr and corr < worst_corr[0]:
                worst_corr = (corr, drop)
            mf = sum(full) / len(full)
            mr = sum(red) / len(red)
            drop_pct = (mf - mr) / mf if mf else 0.0
            if drop_pct > worst_level[0]:
                worst_level = (drop_pct, drop)
        print(f"\n  {th:13s} window {window[0]}..{window[-1]} ({len(window)} mo)")
        print(f"    most shape-fragile to: r/{worst_corr[1]}  "
              f"(corr drops to {worst_corr[0]:.3f} when removed)")
        print(f"    biggest level dependence: r/{worst_level[1]}  "
              f"(level falls {100*worst_level[0]:.0f}% when removed)")


# ── B4: tier decomposition ───────────────────────────────────────────────────
def b4(tier, tagged, posts):
    print("\n\n=== B4. Tier decomposition — does a theme rise everywhere? ===")
    for th in THEMES:
        window = theme_window(th)
        if len(window) < 8:
            print(f"\n  {th:13s} window too short — skipped")
            continue
        half = len(window) // 2
        print(f"\n  {th:13s} {window[0]}..{window[-1]}   "
              f"(rate per 1k: first half -> second half)")
        for t in (1, 2, 3):
            subs = [s for s in tier if tier[s] == t]
            ser = vol_weighted(tagged[th], posts, subs, window)
            early = sum(ser[:half]) / half if half else 0.0
            late = sum(ser[half:]) / (len(ser) - half) if len(ser) - half else 0.0
            arrow = "rising" if late > early * 1.15 else (
                "flat/▼" if late < early * 0.87 else "flat")
            print(f"    T{t}: {early:6.2f} -> {late:6.2f}   {arrow}")


# ── B5: normalization comparison (the main test) ─────────────────────────────
def b5(tier, tagged, posts):
    print("\n\n=== B5. Normalization comparison — does shape survive reweighting? ===")
    print(f"  (Pearson corr vs the current volume-weighted line. sub-equal and")
    print(f"   tier-equal count only subs/tiers with >= {VOLUME_FLOOR} posts that month.)")
    subs = list(tier)
    for th in THEMES:
        vw, sub_eq, tier_eq = [], [], []
        for m in theme_window(th):
            tag = sum(tagged[th][s].get(m, 0) for s in subs)
            tot = sum(posts[s].get(m, 0) for s in subs)
            active = [s for s in subs if posts[s].get(m, 0) >= VOLUME_FLOOR]
            trates = []
            for t in (1, 2, 3):
                ts = [s for s in subs if tier[s] == t]
                ttot = sum(posts[s].get(m, 0) for s in ts)
                if ttot >= VOLUME_FLOOR:
                    ttag = sum(tagged[th][s].get(m, 0) for s in ts)
                    trates.append(1000 * ttag / ttot)
            # keep only months where both alternative measures are well-defined
            if tot and len(active) >= 5 and len(trates) >= 2:
                vw.append(1000 * tag / tot)
                sub_eq.append(sum(1000 * tagged[th][s].get(m, 0) / posts[s][m]
                                  for s in active) / len(active))
                tier_eq.append(sum(trates) / len(trates))
        if len(vw) < 6:
            print(f"\n  {th:13s} too few valid months ({len(vw)}) — skipped")
            continue
        c_sub = pearson(vw, sub_eq)
        c_tier = pearson(vw, tier_eq)
        flag = "  <-- BELOW 0.9" if min(c_sub, c_tier) < 0.9 else "  robust"
        print(f"  {th:13s} n={len(vw):2d}mo   vs sub-equal {c_sub:.3f}   "
              f"vs tier-equal {c_tier:.3f}{flag}")


def main():
    conn = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    try:
        tier, tagged, posts = load(conn)
    finally:
        conn.close()
    print(f"Corpus: {len(tier)} T1-T3 active subreddits | "
          f"window ends {LAST_COMPLETE_MONTH}")
    b1(tier, tagged)
    b2(tier, posts)
    b3(tier, tagged, posts)
    b4(tier, tagged, posts)
    b5(tier, tagged, posts)
    print()


if __name__ == "__main__":
    main()
