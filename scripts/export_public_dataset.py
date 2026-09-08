#!/usr/bin/env python3
"""Export the versioned public aggregate dataset to web/public/dataset/v1/.

Part of the durability bundle: a self-contained, citable snapshot of the
numbers behind the charts, served statically by the site at
https://myfriendisai.com/dataset/v1/ and committed to the repo, so the
research survives the loss of the collection host, the SQLite corpus, or
the upstream archive.

Contents are DERIVED NUMBERS ONLY — monthly per-theme counts and monthly
per-community post volumes. No post text, no titles, no usernames, no
post IDs, no raw Reddit content of any kind.

Design notes
------------
* **Derived from the exports, not the DB.** The theme table is computed
  from ``data/keyword_trends.json`` using the same daily→monthly
  aggregation the site performs in ``web/app/themeData.ts``. Re-querying
  SQLite would let the dataset drift out of agreement with the published
  chart; reading the same file it reads makes that impossible.
* **Deterministic.** Stable ordering everywhere, fixed float rounding, and
  ``generated_at`` in the manifest is carried forward unchanged when every
  file hash matches the previous run. A daily regeneration therefore
  produces no git diff unless a number actually moved.

Usage:
    python3 scripts/export_public_dataset.py [--output-dir PATH]
"""

import argparse
import csv
import hashlib
import io
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.config import _load_all_communities  # noqa: E402

DATA_DIR = REPO_ROOT / "data"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "web" / "public" / "dataset" / "v1"
METHODOLOGY_SRC = REPO_ROOT / "docs" / "METHODOLOGY.md"

DATASET_VERSION = "v1"
DATASET_NAME = "myfriendisai-aggregates"
DATASET_URL = "https://myfriendisai.com/dataset/v1/"

# The six published themes, in the order the site lists them.
THEMES = ["romance", "sexual_erp", "consciousness", "therapy", "addiction", "rupture"]

# Theme → source categories in keyword_trends.json, mirroring THEME_CATEGORIES
# in web/app/themeData.ts. Every theme is a single category today, but the site
# sums merged categories and takes the earliest coverage_start across them, so
# the export must do the same or it would silently diverge the day a theme gains
# a second category.
THEME_CATEGORIES = {
    "romance": ["romance"],
    "sexual_erp": ["sexual_erp"],
    "consciousness": ["consciousness"],
    "therapy": ["therapy"],
    "addiction": ["addiction"],
    "rupture": ["rupture"],
}

TIER_LABELS = {
    0: "T0 — General AI (context)",
    1: "T1 — Primary Companionship",
    2: "T2 — Platform-Specific",
    3: "T3 — Recovery & Dependency",
    4: "T4 — Ambient / Discourse Climate (context)",
}


# ── helpers ──────────────────────────────────────────────────────────────

def _load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _current_month():
    """The in-progress calendar month, which is clipped from both tables.

    Mirrors themeData.ts, which drops the partial month so the last point
    on every chart is a complete month. UTC, because themeData.ts uses
    ``new Date().toISOString()`` — on a host west of UTC a local-time
    ``date.today()`` would clip a month the site still shows for a few hours
    at every month boundary.
    """
    return datetime.now(timezone.utc).strftime("%Y-%m")


# The 2026-05-16 census values, LLM-graded against a 72-post human anchor.
# The therapy figure is the as-is v8 set (~68%); the ~80%/~87% sometimes quoted
# were projections for a rebuilt v9 set that has not shipped. See
# docs/METHODOLOGY.md §4.4.
CENSUS_PRECISION_2026_05 = {
    "addiction": 97, "sexual_erp": 96, "consciousness": 87,
    "romance": 86, "therapy": 68, "rupture": 77,
}


def precision_paragraph():
    """The README's per-theme precision paragraph.

    Pairs the fixed May 2026 census with the latest drift-cycle post precision
    from data/theme_health.json (regenerated on every collection run), so the
    README never quotes a superseded number as current. Falls back to the
    census alone if theme_health.json is unavailable.
    """
    latest = {}
    stamp = None
    try:
        health = _load_json(DATA_DIR / "theme_health.json")
        for theme, t in (health.get("themes") or {}).items():
            pp = t.get("post_precision") or {}
            if pp.get("precision") is not None and pp.get("n"):
                latest[theme] = (round(pp["precision"] * 100), pp["n"])
                stamp = max(stamp or "", pp.get("date") or "") or None
    except (OSError, ValueError):
        latest = {}
    parts = []
    for theme in THEMES:
        census = CENSUS_PRECISION_2026_05.get(theme)
        if theme in latest:
            parts.append(f"{theme} ~{census}% / {latest[theme][0]}% (n={latest[theme][1]:,})")
        else:
            parts.append(f"{theme} ~{census}%")
    if latest:
        head = (
            "**Measured per-theme precision** (share of matched posts judged on-theme),\n"
            "as the 2026-05-16 census (post-weighted) / the latest drift cycle\n"
            f"({stamp}; sampled matches pooled with equal weight per keyword rather than\n"
            "by hit volume), both LLM-graded (the census against a 72-post human anchor): "
        )
    else:
        head = (
            "**Measured per-theme precision** (share of matched posts genuinely about the\n"
            "theme, 2026-05-16 census, LLM-graded against a 72-post human anchor): "
        )
    return (
        head + ", ".join(parts) + ". The therapy line is published below the\n"
        "project's 80% keep gate, with that caveat stated rather than hidden."
    )


def _round(x, places=4):
    return round(x + 0.0, places)


# ── monthly theme counts ─────────────────────────────────────────────────

def build_theme_rows(trends):
    """Monthly per-theme counts, aggregated exactly as themeData.ts does.

    For each theme the walk runs over the CORPUS calendar (the dates present
    in ``_total_posts``) from that theme's ``_coverage_start`` up to the last
    complete month. Walking the corpus calendar rather than the theme's
    hit-days matters: the trends export omits zero-hit days, and averaging
    over hit-days only would bias sparse months upward.

    The smoothing window is defined once, for both sides of the rate:
    ``W(d)`` = the last 7 entries of the corpus calendar up to and including
    ``d``. The numerator is the mean over ``W(d)`` of the theme's daily
    ``count_post_only`` (a corpus day with no theme hits is a real 0); the
    denominator is the mean over ``W(d)`` of total posts. The export
    deliberately re-rolls the numerator here instead of reading the trends
    file's ``count_post_only_7d_avg``: before 2026-09 that field was a mean
    over the last 7 entries of the theme's own hit-day series, a "7-day"
    window that could span months.
    """
    total_entries = sorted(trends.get("_total_posts", []), key=lambda e: e["date"])
    totals = {e["date"]: e["count"] for e in total_entries}

    # Trailing 7-entry mean of the denominator over the corpus calendar.
    total_7d = {}
    for i, entry in enumerate(total_entries):
        window = total_entries[max(0, i - 6): i + 1]
        total_7d[entry["date"]] = sum(e["count"] for e in window) / len(window)

    # Corpus-calendar days per month, for days_observed. Counted over the whole
    # calendar, not just the walked stretch: the column reports collection
    # coverage of the month, so it must not shrink because a theme's
    # coverage_start lands mid-month.
    corpus_days = {}
    for e in total_entries:
        m = e["date"][:7]
        corpus_days[m] = corpus_days.get(m, 0) + 1

    coverage_start = trends.get("_coverage_start", {}) or {}
    current_month = _current_month()

    rows = []
    for theme in THEMES:
        # count_post_only is the PUBLISHED series. The combined post+comment
        # `count` carries a step artifact at 2026-03-18 (when comment tagging
        # began) and is not longitudinally comparable. Fall back to `count`
        # for older export vintages that predate the post-only split.
        # Accumulate across every category mapping to this theme, and take the
        # earliest of their coverage starts — both mirroring themeData.ts.
        by_date = {}
        cs = None
        for cat in THEME_CATEGORIES.get(theme, [theme]):
            for e in trends.get(cat) or []:
                post_only = e.get("count_post_only", e["count"])
                by_date[e["date"]] = by_date.get(e["date"], 0) + post_only
            cat_cs = coverage_start.get(cat)
            if cat_cs and (cs is None or cat_cs < cs):
                cs = cat_cs

        # The numerator's 7-day trailing mean, over the same corpus-calendar
        # slice the denominator uses.
        num_7d = {}
        for i, entry in enumerate(total_entries):
            window = total_entries[max(0, i - 6): i + 1]
            num_7d[entry["date"]] = (
                sum(by_date.get(e["date"], 0) for e in window) / len(window)
            )

        if cs:
            dates = [
                e["date"] for e in total_entries
                if e["date"] >= cs and e["date"][:7] < current_month
            ]
        else:
            # No reliable coverage yet: fall back to hit-days rather than
            # emitting years of zeros.
            dates = sorted(d for d in by_date if d[:7] < current_month)

        monthly = {}
        for d in dates:
            denom = total_7d.get(d, 0)
            rate = (num_7d.get(d, 0) / denom) * 1000 if denom > 0 else 0.0
            m = d[:7]
            bucket = monthly.setdefault(
                m, {"count": 0, "eligible": 0, "rate_sum": 0.0, "days": 0}
            )
            bucket["count"] += by_date.get(d, 0)
            bucket["eligible"] += totals.get(d, 0)
            bucket["rate_sum"] += rate
            bucket["days"] += 1

        for m in sorted(monthly):
            b = monthly[m]
            simple = (b["count"] / b["eligible"] * 1000) if b["eligible"] else 0.0
            rows.append({
                "theme": theme,
                "month": m,
                "post_only_count": b["count"],
                "eligible_posts": b["eligible"],
                "rate_per_1k": _round(simple),
                "rate_per_1k_charted": _round(b["rate_sum"] / b["days"]) if b["days"] else 0.0,
                "days_observed": corpus_days.get(m, b["days"]),
                "coverage_start": cs or "",
            })
    return rows


def charted_vs_plain_stats(rows):
    """How far `rate_per_1k_charted` sits from `rate_per_1k`, for the README.

    The charted value is an unweighted mean of daily rates, so it diverges from
    the plain monthly ratio in months whose daily post volume is uneven. The
    README quotes these numbers so the claim cannot go stale.
    """
    n_over_10pct = 0
    worst = {"pct": 0.0, "theme": "", "month": ""}
    for r in rows:
        plain = r["rate_per_1k"]
        if not plain:
            continue
        rel = abs(r["rate_per_1k_charted"] - plain) / plain
        if rel > 0.10:
            n_over_10pct += 1
        if rel > worst["pct"]:
            worst = {"pct": rel, "theme": r["theme"], "month": r["month"]}
    return {
        "n_rows": len(rows),
        "n_over_10pct": n_over_10pct,
        "max_pct": round(worst["pct"] * 100),
        "max_theme": worst["theme"],
        "max_month": worst["month"],
    }


# ── monthly community volumes ────────────────────────────────────────────

def build_community_rows(activity):
    """Monthly post volume per live tracked community, tier-labelled.

    Source is ``data/community_activity.json`` — the same per-community
    monthly series that draws the sparklines on /communities. It covers the
    currently-active communities only, from 2023-01 (where monthly volume
    becomes reliable) through the last complete month.
    """
    months = activity.get("months", [])
    series = activity.get("activity", {})
    current_month = _current_month()

    meta = {}
    for c in _load_all_communities():
        meta[c["subreddit"].lower()] = c

    rows = []
    for sub in sorted(series, key=lambda s: (s.lower(), s)):
        c = meta.get(sub.lower(), {})
        tier = c.get("tier")
        in_measurement = (
            tier in (1, 2, 3) and not c.get("exclude_from_keywords", False)
        )
        counts = series.get(sub) or []
        for i, m in enumerate(months):
            if m >= current_month:
                continue
            rows.append({
                "subreddit": sub,
                "month": m,
                "posts": counts[i] if i < len(counts) else 0,
                "tier": tier if tier is not None else "",
                "tier_label": TIER_LABELS.get(tier, ""),
                "category": c.get("category", ""),
                # A real JSON boolean, not the string "true"/"false": a string
                # is truthy either way, so `rows.filter(r => r.in_theme_
                # measurement)` silently kept every row. _csv_bytes renders it
                # back to lowercase true/false so the CSV is unchanged.
                "in_theme_measurement": bool(in_measurement),
            })
    return rows


# ── writers ──────────────────────────────────────────────────────────────

def _csv_cell(value):
    """CSV rendering of one field.

    Python's csv writer would stringify a bool as "True"/"False"; the CSV has
    always carried lowercase JSON-style `true`/`false`, and reproducers diff
    against it, so keep that rendering byte-for-byte.
    """
    if isinstance(value, bool):
        return "true" if value else "false"
    return value


def _csv_bytes(rows, columns):
    buf = io.StringIO(newline="")
    writer = csv.DictWriter(buf, fieldnames=columns, lineterminator="\n")
    writer.writeheader()
    for r in rows:
        writer.writerow({c: _csv_cell(r.get(c)) for c in columns})
    return buf.getvalue().encode("utf-8")


def _json_bytes(rows, columns, description):
    payload = {
        "dataset": DATASET_NAME,
        "version": DATASET_VERSION,
        "description": description,
        "columns": columns,
        "row_count": len(rows),
        "rows": rows,
    }
    return (json.dumps(payload, indent=2, sort_keys=False) + "\n").encode("utf-8")


def _write_if_changed(path, content):
    """Write only when the bytes differ, so mtimes stay stable across runs."""
    if path.exists() and path.read_bytes() == content:
        return False
    path.write_bytes(content)
    return True


def _sha256(content):
    return hashlib.sha256(content).hexdigest()


README_TEMPLATE = """\
# My Friend Is AI — public aggregate dataset ({version})

The numbers behind the charts at <https://myfriendisai.com>, as plain CSV
and JSON. This bundle is regenerated by the daily pipeline and is meant to
be self-contained: `METHODOLOGY.md` in this directory is the full statement
of how the numbers were made, so the dataset stays interpretable even if the
site goes away.

- **Version:** {version}
- **Data through:** {data_through} (the in-progress calendar month is excluded)
- **Generated at:** see `manifest.json`. `generated_at` is the time the
  bundle's *content* last changed, not the time of the last run: a
  regeneration whose files are byte-identical carries the previous timestamp
  forward unchanged, so a daily rebuild over unmoved numbers leaves no diff.
  A `generated_at` older than the last collection day means nothing published
  here has moved since then.
- **Canonical location:** <{url}>

Every figure here is a **derived count**. The bundle contains no post text,
no titles, no usernames, no post IDs — no raw Reddit content of any kind.

---

## Files

| File | Rows | What it is |
|---|---|---|
| `monthly_theme_counts.csv` / `.json` | {theme_rows} | Per theme per month: the published keyword-hit count, the corpus denominator, and the rate per 1,000 posts. |
| `monthly_community_volumes.csv` / `.json` | {community_rows} | Per tracked community per month: post volume, with its tier. |
| `METHODOLOGY.md` | — | Standalone statement of scope, method, validation, and limits. |
| `manifest.json` | — | Version, generation timestamp, per-file row counts and SHA-256 hashes. |
| `index.html` | — | Directory listing, so the bundle URL opens in a browser. |

The `.csv` and `.json` forms of each table carry identical data; the JSON
wraps the same rows in an object with a `columns` list and a `row_count`.

---

## `monthly_theme_counts`

One row per theme per month. Themes are not mutually exclusive — a post can
be counted under several themes — so the theme rows do not sum to anything
meaningful.

| Column | Provenance | Meaning |
|---|---|---|
| `theme` | Direct | One of `romance`, `sexual_erp`, `consciousness`, `therapy`, `addiction`, `rupture`. |
| `month` | Direct | Calendar month, `YYYY-MM`. |
| `post_only_count` | Derived | Distinct posts in that month whose **own title or body** matched at least one validated keyword for the theme. This is the published series. Keyword hits found only in a post's *comments* are deliberately excluded — comment tagging began 2026-03-18, so including them puts a step artifact in the series at that date. |
| `eligible_posts` | Derived | All posts collected that month across the communities in the theme-measurement scope (T1–T3, minus the communities excluded from keyword tracking). This is the per-1k denominator. Posts by one platform-developer account (the r/SoulmateAI creator, 89 posts) are excluded from every theme numerator but remain in this denominator. |
| `rate_per_1k` | Derived | `post_only_count / eligible_posts * 1000`. The plain monthly rate. |
| `rate_per_1k_charted` | Derived | The value the site's chart plots: the mean over the month's days of the daily rate, where both numerator and denominator are 7-day trailing means over the same window. That window is the last 7 days of the corpus calendar up to and including the day in question — a day on which posts were collected but the theme was not mentioned counts as a zero in the numerator, not as a missing day. Because it is an unweighted mean of daily rates, it can differ from `rate_per_1k` in months whose daily post volume is uneven: {n_over_10pct} of {n_rows} rows differ by more than 10%, the largest gap being {max_pct}% ({max_theme} {max_month}). Use `rate_per_1k` for analysis and `rate_per_1k_charted` to reproduce the chart. |
| `days_observed` | Derived | The number of corpus-calendar days in that month — days on which at least one post was collected from the theme-measurement scope. It is not clipped at `coverage_start`. Below ~28 means the collector missed days. |
| `coverage_start` | Derived | The theme's first reliably-measurable month (see below). Constant per theme; repeated on each row for convenience. |

**Coverage gating.** Each theme's rows begin at its `coverage_start` — the
first calendar month where the post-only count is at least 5 and every later
completed month is also at least 5. Before that point a theme's vocabulary is
too sparse in the corpus to chart honestly, so those months are omitted here
exactly as they are omitted from the site. The corpus itself reaches back to
2017; the theme lines do not.

**Partial months.** The in-progress calendar month is excluded entirely, so
the last row for each theme is always a complete month.

---

## `monthly_community_volumes`

One row per tracked community per month, from 2023-01 (where monthly volume
becomes reliable) through the last complete month.

| Column | Provenance | Meaning |
|---|---|---|
| `subreddit` | Direct | Subreddit name, without the `r/` prefix. |
| `month` | Direct | Calendar month, `YYYY-MM`. |
| `posts` | Derived | Posts collected from that community with a creation timestamp in that month. |
| `tier` | Direct | 0–4. See `METHODOLOGY.md` for what each tier is and why it exists. |
| `tier_label` | Direct | Human-readable tier name. |
| `category` | Direct | The community's category label as shown on the site. |
| `in_theme_measurement` | Derived | A boolean — `true`/`false` in the JSON, the same words in the CSV (before September 2026 the JSON carried the strings `"true"`/`"false"`). `true` when the community counts toward `monthly_theme_counts` — i.e. tier 1–3 and not excluded from keyword tracking. T0 general-AI and T4 ambient communities are tracked for context only and are always `false`, as are the three explicitness-scope exclusions. |

This table covers the communities currently being collected. Two communities
that were tracked and later deactivated — r/HeavenGF (removed from Reddit —
deleted or renamed — ~May 2026) and r/MySentientAI (moribund) — keep their historical posts in the
corpus and in the theme denominator, but do not appear here.

---

## Reading these numbers honestly

**The counts are a floor, not a ceiling.** The keyword instrument is
precision-first: it would rather miss a real post than admit a false one. An
audit of 400 posts — classified by a language model, with the missed posts
spot-checked by hand — put per-theme recall between 0% and 32%.
Shape and timing are approximately honest; absolute magnitude is a clear
undercount, and the undercount is uneven across themes.

**Do not compare theme heights.** A theme written in blunt, distinctive
vocabulary (addiction: "relapse", "cold turkey") reads higher than one
written in ordinary language (romance: "I love him") whatever the truth
beneath. Read each theme against itself — direction, timing, spikes.

{precision_paragraph}

**It counts language, not people.** A rising line means the theme's
vocabulary appeared more often in these communities. It does not establish
that more people are in AI relationships, addicted, helped, or harmed.

`METHODOLOGY.md` states all of this in full, along with the community
selection rules, the keyword validation protocol, and the data-source
timeline.

---

## License

Creative Commons Attribution 4.0 International (CC BY 4.0) —
<https://creativecommons.org/licenses/by/4.0/>. This matches the license
already applied to the project's aggregate data exports (`LICENSE-DATA` in
the repository). The project's source code is MIT-licensed separately.

Suggested citation:

> Bockley, W. (2026). *My Friend Is AI: Reddit discourse tracker for AI
> companionship communities* — public aggregate dataset {version}.
> myfriendisai.com. <{url}>

## More

- Method and limits, in the site's own words: <https://myfriendisai.com/about>
- Full standalone methodology: `METHODOLOGY.md` (also at
  `docs/METHODOLOGY.md` in the repository)
- Code, keyword lists, and validation records:
  <https://github.com/hopeshub/myfriendisai>
"""


# A static directory listing, so /dataset/v1/ resolves in a browser: Next.js
# serves public/ by exact path, and a bare directory URL needs an index.html.
INDEX_TEMPLATE = """\
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>My Friend Is AI — public aggregate dataset ({version})</title>
<meta name="description" content="Downloadable aggregate dataset behind the charts at myfriendisai.com: monthly per-theme keyword counts and monthly per-community post volumes.">
<style>
  :root {{ color-scheme: dark; }}
  body {{ background:#0F1117; color:#C4CEDB; margin:0;
         font:16px/1.65 ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif; }}
  main {{ max-width:720px; margin:0 auto; padding:40px 20px 64px; }}
  h1 {{ color:#F8FAFC; font-size:26px; font-weight:600; margin:0 0 6px; }}
  .eyebrow {{ color:#F59E0B; font-size:12px; letter-spacing:.08em;
             text-transform:uppercase; margin-bottom:10px; }}
  p {{ margin:0 0 16px; }}
  a {{ color:#F1F4F8; }}
  table {{ border-collapse:collapse; width:100%; margin:0 0 24px; font-size:15px; }}
  th, td {{ text-align:left; padding:9px 10px; border-bottom:1px solid #1E293B;
           vertical-align:top; }}
  th {{ color:#9AA7B8; font-weight:500; font-size:13px; }}
  td.n {{ font-variant-numeric:tabular-nums; white-space:nowrap; color:#9AA7B8; }}
  .note {{ color:#7E8B9E; font-size:14px; }}
  hr {{ border:0; border-top:1px solid #1E293B; margin:28px 0; }}
</style>
</head>
<body>
<main>
  <div class="eyebrow">Public dataset {version}</div>
  <h1>My Friend Is AI — aggregate dataset</h1>
  <p>The numbers behind the charts at <a href="https://myfriendisai.com/">myfriendisai.com</a>, as plain
  CSV and JSON. Data through <strong>{data_through}</strong>; the in-progress
  calendar month is excluded.</p>
  <p>Derived counts only — no post text, no titles, no usernames, no post IDs.</p>

  <!-- File links are root-absolute (/dataset/{version}/…), not relative:
       Next redirects /dataset/{version}/ to /dataset/{version} (308) before the
       rewrite serves this file, so a relative href would resolve one directory
       up and 404. In a downloaded copy of the bundle these links will not
       resolve, but the files sit next to this page under the same names and
       README.md lists them. The two site links are full URLs so a downloaded
       copy still reaches the site. -->
  <div style="overflow-x:auto">
  <table>
    <thead><tr><th>File</th><th>Rows</th><th>What it is</th></tr></thead>
    <tbody>
      <tr><td><a href="/dataset/{version}/monthly_theme_counts.csv">monthly_theme_counts.csv</a> ·
              <a href="/dataset/{version}/monthly_theme_counts.json">.json</a></td>
          <td class="n">{theme_rows}</td>
          <td>Per theme per month: published keyword count, denominator, rate per 1,000.</td></tr>
      <tr><td><a href="/dataset/{version}/monthly_community_volumes.csv">monthly_community_volumes.csv</a> ·
              <a href="/dataset/{version}/monthly_community_volumes.json">.json</a></td>
          <td class="n">{community_rows}</td>
          <td>Per tracked community per month: post volume, with tier.</td></tr>
      <tr><td><a href="/dataset/{version}/README.md">README.md</a></td><td class="n">—</td>
          <td>Column-by-column schema, provenance, and how to read the numbers.</td></tr>
      <tr><td><a href="/dataset/{version}/METHODOLOGY.md">METHODOLOGY.md</a></td><td class="n">—</td>
          <td>Standalone statement of scope, method, validation, and limits.</td></tr>
      <tr><td><a href="/dataset/{version}/manifest.json">manifest.json</a></td><td class="n">—</td>
          <td>Version, generation timestamp, row counts, SHA-256 hashes.</td></tr>
    </tbody>
  </table>
  </div>

  <hr>
  <p class="note"><strong>Read these as a floor, not a ceiling.</strong> The
  keyword instrument is precision-first: an audit of 400 posts (classified by a
  language model, spot-checked by hand) put per-theme recall between 0% and 32%.
  Shape and timing are approximately honest; magnitude
  is an undercount, and it is uneven across themes, so theme heights are not
  comparable to each other. <a href="/dataset/{version}/METHODOLOGY.md">METHODOLOGY.md</a> and the
  site's <a href="https://myfriendisai.com/about">About page</a> state the limits in full.</p>
  <p class="note">Licensed <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a>.
  Cite as: Bockley, W. (2026). <em>My Friend Is AI: Reddit discourse tracker for
  AI companionship communities</em> — public aggregate dataset {version}.
  myfriendisai.com. Code and validation records:
  <a href="https://github.com/hopeshub/myfriendisai">github.com/hopeshub/myfriendisai</a>.</p>
</main>
</body>
</html>
"""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir", default=str(DEFAULT_OUTPUT_DIR),
        help="Destination directory (default: web/public/dataset/v1)",
    )
    args = parser.parse_args()

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    trends = _load_json(DATA_DIR / "keyword_trends.json")
    activity = _load_json(DATA_DIR / "community_activity.json")

    theme_rows = build_theme_rows(trends)
    community_rows = build_community_rows(activity)

    if not theme_rows:
        raise RuntimeError("No theme rows produced — keyword_trends.json looks empty.")
    if not community_rows:
        raise RuntimeError("No community rows produced — community_activity.json looks empty.")

    theme_cols = [
        "theme", "month", "post_only_count", "eligible_posts",
        "rate_per_1k", "rate_per_1k_charted", "days_observed", "coverage_start",
    ]
    community_cols = [
        "subreddit", "month", "posts", "tier", "tier_label",
        "category", "in_theme_measurement",
    ]

    data_through = max(r["month"] for r in theme_rows + community_rows)

    contents = {}
    contents["monthly_theme_counts.csv"] = _csv_bytes(theme_rows, theme_cols)
    contents["monthly_theme_counts.json"] = _json_bytes(
        theme_rows, theme_cols,
        "Monthly per-theme validated-keyword post counts and per-1k rates.",
    )
    contents["monthly_community_volumes.csv"] = _csv_bytes(community_rows, community_cols)
    contents["monthly_community_volumes.json"] = _json_bytes(
        community_rows, community_cols,
        "Monthly post volume per tracked community, with tier.",
    )
    # Quantify charted-vs-plain at export time so the README sentence about
    # the gap can never go stale.
    charted = charted_vs_plain_stats(theme_rows)
    contents["README.md"] = README_TEMPLATE.format(
        version=DATASET_VERSION,
        url=DATASET_URL,
        data_through=data_through,
        theme_rows=f"{len(theme_rows):,}",
        community_rows=f"{len(community_rows):,}",
        n_rows=charted["n_rows"],
        n_over_10pct=charted["n_over_10pct"],
        max_pct=charted["max_pct"],
        max_theme=charted["max_theme"],
        max_month=charted["max_month"],
        precision_paragraph=precision_paragraph(),
    ).encode("utf-8")

    contents["index.html"] = INDEX_TEMPLATE.format(
        version=DATASET_VERSION,
        data_through=data_through,
        theme_rows=f"{len(theme_rows):,}",
        community_rows=f"{len(community_rows):,}",
    ).encode("utf-8")

    if METHODOLOGY_SRC.exists():
        contents["METHODOLOGY.md"] = METHODOLOGY_SRC.read_bytes()
    else:
        print(f"WARNING: {METHODOLOGY_SRC} not found — bundle will lack METHODOLOGY.md",
              file=sys.stderr)

    row_counts = {
        "monthly_theme_counts.csv": len(theme_rows),
        "monthly_theme_counts.json": len(theme_rows),
        "monthly_community_volumes.csv": len(community_rows),
        "monthly_community_volumes.json": len(community_rows),
    }

    files = []
    for name in sorted(contents):
        content = contents[name]
        entry = {
            "name": name,
            "bytes": len(content),
            "sha256": _sha256(content),
        }
        if name in row_counts:
            entry["rows"] = row_counts[name]
        files.append(entry)

    # Carry generated_at forward when nothing changed, so a daily
    # regeneration over identical data produces no git diff at all.
    manifest_path = out_dir / "manifest.json"
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    if manifest_path.exists():
        try:
            prev = _load_json(manifest_path)
            prev_hashes = {f["name"]: f.get("sha256") for f in prev.get("files", [])}
            new_hashes = {f["name"]: f["sha256"] for f in files}
            if prev_hashes == new_hashes and prev.get("data_through") == data_through:
                generated_at = prev.get("generated_at", generated_at)
        except (ValueError, KeyError, TypeError):
            pass

    manifest = {
        "dataset": DATASET_NAME,
        "version": DATASET_VERSION,
        "generated_at": generated_at,
        "data_through": data_through,
        "license": "CC BY 4.0",
        "license_url": "https://creativecommons.org/licenses/by/4.0/",
        "source": DATASET_URL,
        "repository": "https://github.com/hopeshub/myfriendisai",
        "contains_raw_reddit_content": False,
        "files": files,
    }
    contents["manifest.json"] = (
        json.dumps(manifest, indent=2) + "\n"
    ).encode("utf-8")

    changed = []
    for name in sorted(contents):
        if _write_if_changed(out_dir / name, contents[name]):
            changed.append(name)

    print(f"Public dataset {DATASET_VERSION} -> {out_dir}")
    print(f"  monthly_theme_counts:      {len(theme_rows):,} rows "
          f"({len(THEMES)} themes)")
    print(f"  monthly_community_volumes: {len(community_rows):,} rows "
          f"({len(set(r['subreddit'] for r in community_rows))} communities)")
    print(f"  data through:              {data_through}")
    print(f"  files rewritten:           {', '.join(changed) if changed else 'none (no change)'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
