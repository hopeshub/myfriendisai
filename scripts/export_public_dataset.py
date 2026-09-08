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
from datetime import date, datetime, timezone
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
    on every chart is a complete month.
    """
    return date.today().strftime("%Y-%m")


def _round(x, places=4):
    return round(x + 0.0, places)


# ── monthly theme counts ─────────────────────────────────────────────────

def build_theme_rows(trends):
    """Monthly per-theme counts, aggregated exactly as themeData.ts does.

    For each theme the walk runs over the CORPUS calendar (the dates present
    in ``_total_posts``) from that theme's ``_coverage_start`` up to the last
    complete month. Walking the corpus calendar rather than the theme's
    hit-days matters: the trends export omits zero-hit days, so a hit-day walk
    would leave those days' posts out of the denominator.

    Both columns are now the same pooled monthly rate. Until 2026-09-08 the
    site charted a mean of daily smoothed rates, and ``rate_per_1k_charted``
    reproduced that estimator; it ran 2-8% above the pooled rate by an amount
    that drifted by era, its numerator and denominator smoothing windows
    covered different spans of time, and it turned a gap in collection into a
    spike. The chart now plots the pooled rate, so the two columns coincide.
    The column is kept so the dataset schema does not break for anyone who
    already reads it.
    """
    total_entries = sorted(trends.get("_total_posts", []), key=lambda e: e["date"])
    totals = {e["date"]: e["count"] for e in total_entries}

    coverage_start = trends.get("_coverage_start", {}) or {}
    current_month = _current_month()

    rows = []
    for theme in THEMES:
        series = trends.get(theme) or []
        # count_post_only is the PUBLISHED series. The combined post+comment
        # `count` carries a step artifact at 2026-03-18 (when comment tagging
        # began) and is not longitudinally comparable. Fall back to `count`
        # for older export vintages that predate the post-only split.
        by_date = {e["date"]: e.get("count_post_only", e["count"]) for e in series}

        cs = coverage_start.get(theme)
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
            m = d[:7]
            bucket = monthly.setdefault(m, {"count": 0, "eligible": 0, "days": 0})
            bucket["count"] += by_date.get(d, 0)
            bucket["eligible"] += totals.get(d, 0)
            bucket["days"] += 1

        for m in sorted(monthly):
            b = monthly[m]
            pooled = (b["count"] / b["eligible"] * 1000) if b["eligible"] else 0.0
            rows.append({
                "theme": theme,
                "month": m,
                "post_only_count": b["count"],
                "eligible_posts": b["eligible"],
                "rate_per_1k": _round(pooled),
                # Identical to rate_per_1k since 2026-09-08 — see the docstring.
                "rate_per_1k_charted": _round(pooled),
                "days_observed": b["days"],
                "coverage_start": cs or "",
            })
    return rows


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
                # Real boolean: the JSON export carries it as true/false, and
                # _csv_bytes lowercases it for the CSV form.
                "in_theme_measurement": in_measurement,
            })
    return rows


# ── writers ──────────────────────────────────────────────────────────────

def _csv_bytes(rows, columns):
    buf = io.StringIO(newline="")
    writer = csv.DictWriter(buf, fieldnames=columns, lineterminator="\n")
    writer.writeheader()
    for r in rows:
        # Booleans are real JSON booleans in the .json form; in CSV they render
        # as lowercase "true"/"false" rather than Python's "True"/"False".
        writer.writerow({
            k: ("true" if v is True else "false" if v is False else v)
            for k, v in r.items()
        })
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
- **Generated at:** see `manifest.json`
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

**About `manifest.json`.** Its `generated_at` is when these numbers were first
produced, not when the bundle was last rebuilt. The pipeline regenerates the
bundle daily and carries the previous timestamp forward whenever every file
hash matches, so a day on which nothing moved leaves no diff at all. Read it as
"these numbers date from", not "last checked".

**What is not here.** The site also publishes an *Excluding r/CharacterAI*
version of every theme line — r/CharacterAI is 60–90% of all post volume, so
that second view shows the rest of the corpus on its own. It is not part of v1;
this bundle carries the full-scope series only.

---

## `monthly_theme_counts`

One row per theme per month. Themes are not mutually exclusive — a post can
be counted under several themes — so the theme rows do not sum to anything
meaningful.

| Column | Provenance | Meaning |
|---|---|---|
| `theme` | Direct | One of `romance`, `sexual_erp`, `consciousness`, `therapy`, `addiction`, `rupture`. |
| `month` | Direct | Calendar month, `YYYY-MM`. |
| `post_only_count` | Derived | Distinct posts in that month whose **own title or body** matched at least one validated keyword for the theme. This is the published series. Keyword hits found only in a post's *comments* are deliberately excluded — comment tagging began 2026-03-18, so including them puts a step artifact in the series at that date. Counted over the same population as `eligible_posts`: posts whose text survived. |
| `eligible_posts` | Derived | Posts with surviving text that month across the theme-measurement scope (T1–T3, minus the communities excluded from keyword tracking). Posts recorded as removed or deleted are excluded — the archive kept a title and nothing else, so there is no text to match. Image and link posts, which have a title and an empty body, are included. This is the per-1k denominator. |
| `rate_per_1k` | Derived | `post_only_count / eligible_posts * 1000`. The pooled monthly rate, and the number the site's chart plots. |
| `rate_per_1k_charted` | Derived | Identical to `rate_per_1k` since 2026-09-08. Kept so the schema does not break — see below. |
| `days_observed` | Derived | Days in that month present in the corpus calendar. Below ~28 means the collector missed days entirely. It will not catch a month that was collected thinly rather than not at all — for that, compare `eligible_posts` against the neighbouring months. |
| `coverage_start` | Derived | The theme's first reliably-measurable month (see below). Constant per theme; repeated on each row for convenience. |

**The two rate columns now carry the same number.** Until 2026-09-08 the
site's chart plotted a different estimator — a mean, over the month's days, of
a daily rate smoothed with a 7-day trailing window — and `rate_per_1k_charted`
reproduced it. That estimator ran 2–8% above the pooled rate by an amount that
drifted era to era, its numerator and denominator smoothing windows covered
different spans of time, and it turned a gap in collection into a spike. The
chart now plots the pooled rate: one month's count over one month's eligible
posts. The column stays in the schema so existing readers do not break, but
there is no longer a choice to make between the two. **Downloads taken before
2026-09-08 have different values in the two columns**; in those files,
`rate_per_1k` is the one to analyse.

**What counts as a post.** As of 2026-09-08 the published population is posts
whose text survived to capture. A post the archive recorded as `[removed]` or
`[deleted]` kept only its title, so it is out of both the count and the
denominator. Keeping such posts in made every rate depend on how hard a
community moderates and on which collection regime was running — one tracked
community runs 70–85% removed posts, and the live-Reddit window of March–May
2026 contained none at all, because Reddit's own listing omitted them.
Downloads taken before 2026-09-08 used the wider population and sit roughly
12–16% lower in the affected months.

**Coverage gating.** Each theme's rows begin at its `coverage_start` — the
first calendar month where the post-only count is at least 5 and every later
completed month is also at least 5. Before that point a theme's vocabulary is
too sparse in the corpus to chart honestly, so those months are omitted here
exactly as they are omitted from the site. The corpus itself reaches back to
2017; the theme lines do not.

**Small months.** Clearing that gate does not make a month precise: 41% of the
consciousness rows and about a third of the therapy and addiction rows have a
`post_only_count` under 20. `post_only_count` and `eligible_posts` are both on
every row so that you can put an interval on any month rather than take the
rate at face value.

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
| `posts` | Derived | Posts collected from that community with a creation timestamp in that month, counting measurable posts only — the same population as `eligible_posts` above, so a community's volume here is what it contributes to the theme denominator. Posts recorded as removed or deleted are excluded; image and link posts are included. |
| `tier` | Direct | 0–4. See `METHODOLOGY.md` for what each tier is and why it exists. |
| `tier_label` | Direct | Human-readable tier name. |
| `category` | Direct | The community's category label as shown on the site. |
| `in_theme_measurement` | Derived | `true` when the community counts toward `monthly_theme_counts` — i.e. tier 1–3 and not excluded from keyword tracking. T0 general-AI and T4 ambient communities are tracked for context only and are always `false`, as are the three explicitness-scope exclusions. In the JSON this is a real boolean; in the CSV it is the lowercase string `true` or `false`. |

This table covers the communities currently being collected. Two communities
that were tracked and later deactivated — r/HeavenGF (banned by Reddit, ~May
2026) and r/MySentientAI (moribund) — keep their historical posts in the
corpus and in the theme denominator, but do not appear here.

---

## Revision history

| Version | Date | What changed |
|---|---|---|
| v1 | 2026-08-27 | First publication. |
| v1.1 | 2026-09-08 | Population narrowed to **measurable posts**: posts recorded as removed or deleted leave every count and the per-1k denominator. The site's chart switched to the **pooled monthly rate**, so `rate_per_1k_charted` now equals `rate_per_1k`. `in_theme_measurement` is a real boolean in the JSON form. Numbers moved; the schema did not. |

The bundle URL and file names stay `v1` — these are corrections to how the same
quantities are computed, not a new set of quantities. `manifest.json` records
when the current numbers were produced.

---

## Reading these numbers honestly

**The counts are a floor, not a ceiling.** The keyword instrument is
precision-first: it would rather miss a real post than admit a false one. A
hand-coded audit of 400 posts put per-theme recall between 0% and 32% —
consciousness caught none of the eight posts a human classified as on-theme
(a small sample, whose Wilson interval reaches about 32%). Shape and timing are
approximately honest; absolute magnitude is a clear undercount, and the
undercount is uneven across themes.

**Do not compare theme heights.** A theme written in blunt, distinctive
vocabulary (addiction: "relapse", "cold turkey") reads higher than one
written in ordinary language (romance: "I love him") whatever the truth
beneath. Read each theme against itself — direction, timing, spikes.

**Measured per-theme precision** (share of matched posts genuinely about the
theme, census re-measurement 2026-05-16): addiction ~97%, sexual_erp ~96%,
consciousness ~87%, romance ~86%, rupture ~77%, therapy ~66–68%. Earlier
versions of this file put therapy at ~80%; that figure was a projection for a
rebuilt keyword set that has not shipped, and the table now carries the measured
value for the set that is actually counting. `METHODOLOGY.md` §4.4 has the
correction in full, along with the separate drift-check figures and why they
differ.

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
  table {{ border-collapse:collapse; width:100%; margin:0 0 24px; font-size:15px; table-layout:fixed; }}
  td, th {{ overflow-wrap:anywhere; }}
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
  <p>The numbers behind the charts at <a href="/">myfriendisai.com</a>, as plain
  CSV and JSON. Data through <strong>{data_through}</strong>; the in-progress
  calendar month is excluded.</p>
  <p>Derived counts only — no post text, no titles, no usernames, no post IDs.</p>

  <table>
    <thead><tr><th>File</th><th>Rows</th><th>What it is</th></tr></thead>
    <tbody>
      <tr><td><a href="monthly_theme_counts.csv">monthly_theme_counts.csv</a> ·
              <a href="monthly_theme_counts.json">.json</a></td>
          <td class="n">{theme_rows}</td>
          <td>Per theme per month: published keyword count, denominator, rate per 1,000.</td></tr>
      <tr><td><a href="monthly_community_volumes.csv">monthly_community_volumes.csv</a> ·
              <a href="monthly_community_volumes.json">.json</a></td>
          <td class="n">{community_rows}</td>
          <td>Per tracked community per month: post volume, with tier.</td></tr>
      <tr><td><a href="README.md">README.md</a></td><td class="n">—</td>
          <td>Column-by-column schema, provenance, and how to read the numbers.</td></tr>
      <tr><td><a href="METHODOLOGY.md">METHODOLOGY.md</a></td><td class="n">—</td>
          <td>Standalone statement of scope, method, validation, and limits.</td></tr>
      <tr><td><a href="manifest.json">manifest.json</a></td><td class="n">—</td>
          <td>Version, generation timestamp, row counts, SHA-256 hashes.</td></tr>
    </tbody>
  </table>

  <hr>
  <p class="note"><strong>Read these as a floor, not a ceiling.</strong> The
  keyword instrument is precision-first: a hand-coded audit put per-theme recall
  between 0% and 32%. Shape and timing are approximately honest; magnitude
  is an undercount, and it is uneven across themes, so theme heights are not
  comparable to each other. <a href="METHODOLOGY.md">METHODOLOGY.md</a> and the
  site's <a href="/about">About page</a> state the limits in full.</p>
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
    contents["README.md"] = README_TEMPLATE.format(
        version=DATASET_VERSION,
        url=DATASET_URL,
        data_through=data_through,
        theme_rows=f"{len(theme_rows):,}",
        community_rows=f"{len(community_rows):,}",
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
