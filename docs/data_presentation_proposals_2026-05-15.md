# Data presentation proposals - 2026-05-15

## Executive recommendation

Build the public experience around a **Trend Atlas** rather than a single
rank-like comparison chart.

The current data is valuable, but it is not six equally sensitive thermometers.
Each theme is a precision-first detector built from a different keyword set,
with different recall, different community concentration, and different
susceptibility to vocabulary drift. The presentation should make that feel
obvious to a casual visitor without making the project look apologetic or
overcomplicated.

The strongest public claim is:

> MyFriendIsAI tracks how clearly expressed AI-companion themes rise and fall
> over time across Reddit communities.

The weakest and most dangerous public claim is:

> Theme A is more common than Theme B.

The recommended design should therefore optimize for **shape, timing, and
within-theme change**, not cross-theme ranking.

## Measurement contract

Put this contract in the product, not just in methodology docs:

| User question | Answerable? | Presentation treatment |
|---|---:|---|
| Did a theme spike or fade over time? | Yes | Primary chart task |
| When did a theme spike? | Yes | Events and annotations |
| Is a theme above or below its own baseline? | Yes | Indexed view |
| Did two themes move together around an event? | Mostly | Synchronized small multiples |
| Which theme is biggest? | No | Avoid rank-like charts |
| Did Theme A overtake Theme B? | No | Do not encourage crossovers |
| What fraction of all discourse is about the theme? | No, not without recall correction | Label as detected language, not prevalence |
| Did LLM verification make the chart more accurate? | No | LLM remains audit/monitoring only |

Suggested chart subtitle:

> Compare each theme's shape, timing, and change from its own baseline. Do not
> compare theme heights as prevalence; keyword sensitivity differs by theme.

This is the single most important product decision in the project.

## Current project read

### What is strong

- The deterministic keyword pipeline is defensible. It is reproducible,
  auditable, and has a clear precision-first philosophy.
- The recent About-page framing is directionally right: the chart uses keyword
  counts, not AI classification.
- The corpus is substantial: `data/site_meta.json` currently reports 4,040,688
  posts from 2017-01-01 through 2026-05-15.
- The export already contains useful parallel series: `count`,
  `count_post_only`, `count_llm_verified`, and `_coverage_start`.
- The comprehensiveness audit is unusually honest for a public dashboard. It
  gives the project a principled way to explain why magnitude comparisons are
  weak while trend-shape claims remain useful.

### What is fragile

- The interface still invites cross-theme comparison because the main chart is
  an overlaid multi-line chart. Casual users will read line height as "how much
  people talk about this."
- The relative chart mode is currently `% of peak`, which makes every theme
  peak at 100. That creates a false equivalence between a one-off noisy peak
  and a broad durable rise.
- The LLM layer is conceptually scoped down, but code still exports
  `count_llm_verified` and tests fail when the `llm_classifications` table is
  absent. That means the abandoned path is still entangled with the production
  exporter.
- Community counts are inconsistent in public copy and status data. Current
  local artifacts show 26 active `data/subreddits.json` entries while some
  copy/status fields still say 27, and the About page still says 22 primary
  AI-companion subreddits where the config currently loads 21 keyword
  communities.
- The `count` series mixes posts and comments. Comment tagging began later
  than the historical corpus, so post+comment is not the cleanest default for
  long-run trend comparisons.
- The frontend currently smooths the theme numerator but divides by that
  day's unsmoothed total post count. For a polished public metric, numerator
  and denominator should use the same window.

### Test and validation snapshot

Observed on 2026-05-15:

- `.venv/bin/python -m pytest -q`: 26 passed, 6 failed. All failures are in
  `tests/test_export_keyword_trends.py`, caused by
  `src/db/operations.py:export_keyword_trends_json` querying
  `llm_classifications` even when tests create a schema without that table.
- `npm run lint` from `web/`: passed.

This matters for presentation because the public methodology says "no LLM in
the chart," while the exporter and test suite still treat the LLM series as a
production shape.

## External research distilled

The outside guidance points in the same direction:

- [Google Trends FAQ](https://support.google.com/trends/answer/4365533?hl=en-GB)
  is a useful public analogy: normalized trend data can be valuable, but it is
  not absolute volume, and Google explicitly warns that spikes and normalized
  scores should not be read as direct popularity or polling.
- [Dallas Fed DataBasics on indexing](https://www.dallasfed.org/research/basics/indexing)
  explains why indexing series to a common starting point is useful when
  comparing change across series with different magnitudes.
- [CDC COVE small-multiples guidance](https://www.cdc.gov/cove/data-visualization-types/small-multiples.html)
  recommends small multiples for line charts with more than five series to
  reduce cognitive load and make patterns easier to compare.
- [ONS small-multiple chart guidance](https://service-manual.ons.gov.uk/data-visualisation/chart-types/small-multiple-charts)
  says small multiples make individual trends clearer and reduce reliance on
  color; it also recommends indexes or derived variables when magnitudes differ
  substantially.
- [ONS uncertainty guidance](https://service-manual.ons.gov.uk/data-visualisation/guidance/showing-uncertainty-in-charts)
  recommends showing uncertainty when it would change interpretation, using
  plain-language explanations, and avoiding charts where uncertainty makes
  comparisons meaningless.

For this project, that becomes:

1. Use indexed trends for broad comparison.
2. Use small multiples as the primary view.
3. Explain uncertainty and detection coverage in plain language.
4. Keep absolute per-1,000 values available, but not as the first impression.

## Proposal 1: Make "Trend Atlas" the default chart

Replace the current overlaid chart as the first chart experience with a 2x3
small-multiples grid:

- One panel per theme.
- Same x-axis across panels.
- Same y-axis if using an index.
- Baseline line at 100.
- Event bands shared across panels.
- Synchronized hover across panels.
- Each panel title includes a reliability chip: `narrow detector`, `moderate
  detector`, or `broad detector`.

Default metric:

> Post-only baseline index, where 100 is the theme's average detected rate in
> its first six complete months after `coverage_start`.

Why post-only:

- It avoids the March 2026 comment-collection break.
- It is comparable back through the 2017 historical corpus.
- It gives the cleanest longitudinal story.

Why baseline index:

- It preserves within-theme percentage change.
- It reduces the visual temptation to compare raw theme heights.
- It is more honest than `% of peak`, because it does not force every theme to
  have an equally dramatic maximum.

Implementation formula:

```text
daily_rate_7d = 1000 * sum(count_post_only over last 7 days)
                / sum(total_posts over last 7 days)
monthly_rate = 1000 * sum(count_post_only over completed month)
               / sum(total_posts over completed month)
baseline = mean(monthly_rate) over first six complete months after coverage_start
baseline_index = 100 * monthly_rate / baseline
```

If the baseline is too sparse, hold the theme out of indexed display until the
existing `coverage_start` rule passes and a six-month baseline can be formed.
For consciousness, this will likely mean the public line starts later than the
others; that is a feature, not a bug.

## Proposal 2: Turn the current overlaid chart into "Explore"

Keep the overlaid multi-line chart, but make it an advanced view with explicit
mode labels:

- `Trend Atlas` - default, small multiples, baseline index.
- `Overlay` - compare timing and co-movement.
- `Raw rates` - per 1,000 detected posts, with warning copy.

In `Overlay`, use indexed values by default. If raw per-1,000 overlay remains,
show an inline warning:

> Raw line heights are not prevalence rankings. Use this view for timing and
> event inspection only.

Remove `% of peak` as a primary mode. If it survives, rename it to `Peak-normalized`
and place it behind an explanation. It is useful for finding co-movement, but
it is actively bad as a default because it visually equalizes noisy and robust
signals.

## Proposal 3: Add theme reliability profiles

Each theme should have a compact profile available from the panel, side sheet,
or theme detail view.

Recommended fields:

| Field | Purpose |
|---|---|
| What this detector catches | Human-readable scope |
| What it misses | Explains recall without burying the user |
| Detection coverage | Low/medium/high, derived from recall audit |
| Post precision | From validation/audit records where available |
| Comment precision | Separate because comments behave differently |
| Top communities | Helps users interpret concentrated signals |
| Known noisy keywords | Builds trust without overexposing machinery |
| Coverage start | Explains why some lines begin later |
| Safe claim | One sentence users can repeat |
| Unsafe claim | One sentence users should not repeat |

Example for romance:

- Safe claim: "Clearly AI-romance-coded language rose or fell during this
  period."
- Unsafe claim: "Only this share of AI-companion posts are romantic."
- Misses: naturalistic relationship language such as names, pronouns, and
  everyday partner updates.

Example for addiction:

- Safe claim: "Explicit dependency and recovery language increased relative to
  this theme's own baseline."
- Unsafe claim: "Addiction is more prevalent than romance."
- Misses: positive or normalized heavy-use posts that do not use dependency
  vocabulary.

These profiles will do more for reader trust than another global methodology
paragraph.

## Proposal 4: Present current values as diagnostics, not rankings

The current cards should not look like a leaderboard. A row of six numbers
invites "which is highest?" even if the text says not to compare them.

Recommended card structure:

```text
Rupture
3.2x baseline
Latest 90 days vs first stable baseline
Detector: narrow | Recall: low | Top community: CharacterAI
```

Avoid sorting cards by latest raw value. Sort by a fixed conceptual order or by
recent change from baseline, and label the sort explicitly. If a "largest
increase" view is useful, make it a mode, not the default.

Better summary stats:

- `latest_index`: current 30- or 90-day average vs baseline.
- `change_90d`: latest 90 days vs previous 90 days.
- `peak_month`: strongest indexed month, with event context.
- `volatility`: optional, useful for distinguishing one-off spikes from durable
  shifts.

Less useful summary stats:

- Raw latest count across themes.
- Raw rank across themes.
- Percent of all posts without recall correction.

## Proposal 5: Add event and methodology bands

This project is event-driven. The chart should admit that.

Recommended event types:

- Product events: Replika ERP crisis, Character.AI model changes, outages,
  major policy changes.
- Community events: subreddit additions/removals, subreddit outages,
  moderation changes.
- Methodology events: keyword expansions, keyword removals, comment collection
  start, LLM verification experiment retired.

Display rules:

- Show major product/community events as thin vertical markers.
- Show methodology changes as shaded bands or small tags at the top of the
  chart.
- Apply the same markers across all small multiples.
- Keep labels terse; open a detail panel for longer explanation.

This protects the project from a common dashboard failure: users see a spike
and infer a social phenomenon when it may be an instrumentation change.

## Proposal 6: Separate measurement data from audit data

The LLM integration should be made physically harder to mistake for production
measurement.

Recommended data boundary:

- `keyword_trends.json`: production public chart data only.
- `theme_health.json`: public reliability metadata, no LLM precision oracle.
- `llm_audit_summary.json` or docs-only reports: verdict counts, drift checks,
  candidate discovery, and calibration history.

Specific code recommendation:

- Remove `count_llm_verified` from the public chart export, or make it opt-in
  behind an `include_experimental=True` parameter used only by audit scripts.
- If keeping it, guard the query with a schema check so tests and fresh DBs do
  not require `llm_classifications`.
- Remove stale comments in `web/app/page.tsx` that describe flipping the chart
  default to `count_llm_verified`.
- Rename any user-facing LLM language from "verification" to "audit" or
  "monitoring" unless the output actually changes a published number.

The mental model should be:

> Keywords measure. LLMs inspect the measuring instrument.

## Proposal 7: Use plain-language uncertainty, not statistical theater

Do not put confidence intervals on every chart line. The recall audit has wide
intervals, but the public chart is not a direct prevalence estimate. Full bands
would imply a level of statistical correction the project is not actually
performing.

Instead:

- Use coarse detector labels: `low coverage`, `moderate coverage`, `higher
  coverage`.
- Show exact recall audit values in the methodology/details view.
- Put one sentence near the chart explaining that the lines are floors, not
  prevalence estimates.
- In downloads, include the recall estimates and Wilson intervals for
  researchers.

This follows the spirit of the ONS uncertainty guidance: expose uncertainty
when it changes interpretation, but do not make the chart harder to read than
the data can support.

## Proposal 8: Add a first-viewport narrative that is honest and compelling

The first viewport should not feel like a methodology apology. It should feel
like a good research instrument.

Suggested layout:

```text
Header:
MyFriendIsAI
Detected AI-companion themes across Reddit, indexed to each theme's own baseline.

Status strip:
4.0M posts | 26 tracked communities | updated May 15, 2026 | keyword-based

Primary surface:
Trend Atlas, six small multiples, baseline = 100

Controls:
Time range | Surface: Posts / Posts + comments | View: Atlas / Overlay / Raw rates

Below chart:
Three event callouts from the selected period
```

The phrase "indexed to each theme's own baseline" does a lot of work. It tells
users that the chart is comparative, but not a raw prevalence rank.

## Proposal 9: Tighten deployment and freshness trust

Data presentation includes operational presentation. If a user sees stale or
inconsistent counts, the methodology will feel fragile.

Recommended validation additions:

- Assert that community counts in `status.json`, `subreddits.json`,
  `site_meta.json`, About copy, Communities metadata, and OpenGraph copy agree
  or are generated from the same source.
- Assert that `keyword_trends.json` has `_coverage_start` for all public themes.
- Assert that no public copy says "LLM verification is rolling out" or implies
  LLM-classified counts are in the chart.
- Assert that `theme_health.json` does not expose `llm_stats.precision`.
- Assert that exported chart data can be generated from a fresh schema without
  optional LLM migrations.
- Add a build check for stale public data copies under `web/data`.

The frontend should also show freshness plainly:

```text
Updated May 15, 2026, 8:53 AM PT
571 posts collected today across 26 communities
```

If a collection or push fails, show a quiet warning, not a dramatic error:

```text
Data is current through May 14. Today's collector is retrying.
```

## Proposal 10: Recommended implementation sequence

### P0 - Make the current story true in code

1. Fix `export_keyword_trends_json` so optional LLM data cannot break tests or
   fresh DB exports.
2. Remove or quarantine `count_llm_verified` from public chart data.
3. Update stale public copy and comments: 26 vs 27 tracked communities, 21 vs
   22 keyword communities, and any "flip to LLM" language.
4. Add validation checks for LLM/chart copy and community-count consistency.
5. Keep the chart default on deterministic keyword counts.

### P1 - Replace the headline chart

1. Compute monthly post-only rates from existing daily series.
2. Compute per-theme baseline windows after `_coverage_start`.
3. Add `baseline_index` client-side first; move to export later if needed.
4. Build the 2x3 Trend Atlas small-multiples component.
5. Replace `% of peak` with `baseline index`.
6. Add synchronized hover and event bands.

### P2 - Add reliability profiles

1. Extend `theme_health.json` with presentation-ready fields:
   `detector_coverage_label`, `safe_claim`, `unsafe_claim`,
   `misses_summary`, `coverage_start`, and `top_communities`.
2. Add a theme detail sheet or drawer.
3. Add a compact reliability chip to each small-multiple panel.

### P3 - Add research depth without changing measurement

1. Build the quarterly recall-gap candidate report from unfiltered posts.
2. Keep LLM output in docs or audit files, not chart JSON.
3. Consider a quarterly qualitative snapshot as editorial context, clearly
   labeled as qualitative and not part of the measurement series.

## Suggested data additions

The existing export can support a first version, but the site will be easier to
reason about if presentation metadata is explicit.

Possible `theme_metadata.json`:

```json
{
  "romance": {
    "label": "Romance",
    "coverage_start": "2023-01-01",
    "baseline_start": "2023-01-01",
    "baseline_end": "2023-06-30",
    "baseline_metric": "post_only_mentions_per_1000_posts",
    "detector_coverage_label": "low coverage",
    "recall_estimate": 0.04,
    "recall_ci": [0.01, 0.11],
    "precision_post": 0.82,
    "precision_comment": 0.72,
    "safe_claim": "Clearly AI-romance-coded language changed relative to its own baseline.",
    "unsafe_claim": "This is the share of AI-companion discourse that is romantic.",
    "misses_summary": "Naturalistic partner language, names, pronouns, and title-only relationship updates."
  }
}
```

This should be generated from a mix of audit constants and export-derived
values, not hand-copied into React.

## Public copy bank

Good wording:

- "Detected theme language"
- "Compared with its own baseline"
- "Clearly expressed posts"
- "Keyword-sensitive slice"
- "Trend shape and timing"
- "Floor, not full prevalence"

Risky wording:

- "Prevalence" unless qualified
- "Share of discourse" unless qualified
- "Most common theme"
- "Bigger than"
- "Overtook"
- "LLM-verified" for published chart values

Recommended explainer:

> The chart tracks clearly detectable language, not total prevalence. Some
> themes, like romance, are often expressed in ordinary relationship language
> that keywords intentionally avoid. Use the chart to compare timing and change
> within a theme, not to rank themes by size.

## The core product stance

This project should not try to hide its measurement limitations. It should make
them part of the product's intelligence.

The compelling outside-user version is not:

> Here are six perfect measurements.

It is:

> Here are six carefully documented detectors watching a strange social
> phenomenon unfold over time. The heights are not prevalence rankings, but the
> spikes, timing, and directional changes are meaningful.

That framing is accurate, memorable, and sturdy enough for public use.
