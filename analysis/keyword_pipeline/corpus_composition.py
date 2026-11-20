#!/usr/bin/env python3
"""Corpus composition measurements — Plan B.

Read-only analysis of how the curated subreddit corpus shapes the six theme
lines. Spec: docs/corpus_composition_plan.md.

Mirrors the published population, by importing it rather than restating it:
the keyword communities from config (load_keyword_communities(): T1-T3
without exclude_from_keywords, deactivated subs' history included), post-source
tags only (source='post'), measurable posts only (measurable_post_where()) and
EXCLUDED_AUTHORS dropped, in both numerator and denominator. Monthly buckets,
UTC, through LAST_COMPLETE_MONTH in every section.

History: the 2026-05-16 and first 2026-08-27 runs ignored exclude_from_keywords;
the 2026-11-19 re-run found the script still excluded one author of two,
counted shells, kept only is_active subs and let B1 run into the partial month.
Importing the definitions is what keeps it from drifting a third time.

Run from the repo root:  python3 analysis/keyword_pipeline/corpus_composition.py
"""

import json
import sqlite3
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.config import load_keyword_communities  # noqa: E402
from src.db.operations import EXCLUDED_AUTHORS, measurable_post_where  # noqa: E402

DB = ROOT / "data" / "tracker.db"
KEYWORD_TRENDS = ROOT / "data" / "keyword_trends.json"
VOLUME_FLOOR = 200                      # min posts/month for a sub to count in sub-equal

THEMES = ["romance", "sexual_erp", "consciousness", "therapy", "addiction", "rupture"]


def last_complete_month(now=None):
    """The calendar month before `now` (UTC), as 'YYYY-MM'. The in-progress
    month is left out everywhere on the site, so it is left out here."""
    now = now or datetime.now(timezone.utc)
    y, m = now.year, now.month - 1
    if m == 0:
        y, m = y - 1, 12
    return f"{y:04d}-{m:02d}"


# Values as published on 2026-11-18, used only if the export can't be read.
_COVERAGE_START_FALLBACK = {
    "romance": "2022-12", "sexual_erp": "2022-08", "consciousness": "2025-04",
    "therapy": "2023-01", "addiction": "2023-01", "rupture": "2022-12",
}


def load_coverage_start(path=KEYWORD_TRENDS):
    """Published per-theme start month, from `_coverage_start` in
    data/keyword_trends.json (authoritative; it moves as the corpus grows).
    The site shows each line only from here, so robustness is assessed over
    the same span — not over noisy pre-publication data."""
    try:
        published = json.loads(Path(path).read_text())["_coverage_start"]
        return {t: published[t][:7] for t in THEMES}
    except (OSError, ValueError, KeyError, TypeError):
        return dict(_COVERAGE_START_FALLBACK)


LAST_COMPLETE_MONTH = last_complete_month()
COVERAGE_START = load_coverage_start()


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


def load(conn):
    """Return (tier, tagged, posts) keyed by lowercased subreddit.

    tier:   sub -> tier (1/2/3), the keyword corpus
    tagged: theme -> sub -> month -> distinct tagged-post count
    posts:  sub -> month -> measurable post count (the denominator)

    The filters are the ones export_keyword_trends_json applies, so the counts
    here sum to the published post-only series and _total_posts.
    """
    communities = load_keyword_communities()
    names = [c["subreddit"] for c in communities]
    tier = {c["subreddit"].lower(): c["tier"] for c in communities}
    sub_ph = ",".join("?" * len(names))
    author_ph = ",".join("?" * len(EXCLUDED_AUTHORS))

    # Distinct tagged posts (post source only), deduped to (theme, sub, month, post).
    seen = set()
    tagged = {th: defaultdict(lambda: defaultdict(int)) for th in THEMES}
    for cat, sub, pdate, pid in conn.execute(
        f"SELECT t.category, t.subreddit, t.post_date, t.post_id "
        f"FROM post_keyword_tags t JOIN posts p ON p.id = t.post_id "
        f"WHERE t.source='post' AND t.subreddit IN ({sub_ph}) "
        f"AND {measurable_post_where('p')} "
        f"AND (p.author IS NULL OR p.author NOT IN ({author_ph}))",
        (*names, *EXCLUDED_AUTHORS),
    ):
        month = pdate[:7]
        if cat not in tagged or month > LAST_COMPLETE_MONTH:
            continue
        s = sub.lower()
        key = (cat, s, month, pid)
        if key in seen:
            continue
        seen.add(key)
        tagged[cat][s][month] += 1

    # Measurable posts per (sub, month) — the denominator population.
    posts = defaultdict(lambda: defaultdict(int))
    for sub, month, c in conn.execute(
        f"SELECT subreddit, strftime('%Y-%m', date(created_utc,'unixepoch')), COUNT(*) "
        f"FROM posts WHERE created_utc IS NOT NULL AND subreddit IN ({sub_ph}) "
        f"AND {measurable_post_where('')} "
        f"AND (author IS NULL OR author NOT IN ({author_ph})) "
        f"GROUP BY 1, 2",
        (*names, *EXCLUDED_AUTHORS),
    ):
        if month and month <= LAST_COMPLETE_MONTH:
            posts[sub.lower()][month] += c

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
    # All tagged months through LAST_COMPLETE_MONTH (load() applies the cap).
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
    print(f"Corpus: {len(tier)} T1-T3 keyword subreddits (measurable posts) | "
          f"window ends {LAST_COMPLETE_MONTH}")
    b1(tier, tagged)
    b2(tier, posts)
    b3(tier, tagged, posts)
    b4(tier, tagged, posts)
    b5(tier, tagged, posts)
    print()


if __name__ == "__main__":
    main()
