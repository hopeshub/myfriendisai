# Corpus / denominator diagnostics — keyword spot-check (2026-05-15)

Layer 4 of the spot-check audit. The chart shows keyword hits **per 1k posts**.
That ratio is only comparable across the timeline if the measurement instrument
— the corpus itself — is constant. It is not. This file records where it varies.

All queries run against `data/tracker.db`, eligible subs = the 21 T1–T3
keyword communities (`load_keyword_communities()`).

---

## 1. Data source — the corpus is ~99% archive backfill

| Source | Posts | Share |
|---|---:|---:|
| `arctic_shift` (backfill archive) | 3,994,182 | 98.8% |
| `json_endpoint` (live daily collection) | 46,506 | 1.2% |

Live collection is almost entirely 2026 (23,173 of 46,506 json_endpoint posts).
2017–2025 is essentially 100% Arctic Shift.

**Read:** one dominant, uniform source is *good* for comparability — there is no
patchwork of collection methods across years. The one seam to be aware of is
within 2026, where live collection (23.2k) and backfill (58.6k) overlap; minor
duplicate/boundary effects are possible there but not in earlier years.

## 2. Body availability rises sharply over time — the main artifact

Keyword matching runs on **title + body**. A post whose body is `[removed]`,
`[deleted]`, or empty can only be caught by a title-matching keyword. Body
availability is not constant — older posts have had years longer to be
moderated or user-deleted before Arctic Shift archived them.

Self-posts (text posts) with a real, readable body, eligible subs:

| Year | Self-posts | % with usable body |
|---|---:|---:|
| 2023 | 95,520 | 55.9% |
| 2024 | 126,135 | 59.2% |
| 2025 | 103,489 | 70.7% |
| 2026 | 39,288 | 77.7% |

A 2023 self-post is **~22 points less likely** to have a body than a 2026 one.

Confirmed downstream in the tagged posts themselves — share of theme-tagged
posts where the body was gone at match time:

| Year | Tagged posts | Tagged on title only (body-less) |
|---|---:|---:|
| 2023 | 6,258 | 26.0% |
| 2024 | 3,145 | 20.3% |
| 2025 | 4,753 | 11.1% |
| 2026 | 3,094 | 7.0% |

**Implication for the trend.** Keyword *recall* is structurally lower in older
years purely because there is less text to match. The per-1k denominator (all
posts) is unaffected by body loss, but the numerator (keyword hits) is depressed
for older years. Net effect: **the chart understates older-year theme prevalence
and therefore overstates the rise.** The shape "rose from nearly nothing" is
partly an instrument artifact, not only a real-world change. This needs an
explicit caveat anywhere the audit or site narrates the slope.

This effect is *uniform across themes* (it is a property of the corpus, not of
any keyword), so it distorts magnitude/slope but not the *relative* ordering of
themes or the *timing* of within-theme spikes.

## 3. Monthly post volume — continuous, no collection blackouts

Eligible-sub monthly post counts from 2022-10 to 2026-05 range 10k–43k with no
zero or near-zero month. Mild dips (2024-02 ≈11.1k, 2024-05 ≈10.6k, 2025-12
≈12.9k); 2026-05 is partial (month in progress, ~10.4k through the 15th). No
month is missing. The per-1k **denominator is continuous and trustworthy** — the
artifact in §2 is on the numerator side only.

## 4. Comments exist only from March 2026 — hard step in the default series

Comment collection began 2026-03-18 (targets posts 5–6 days old). Comment volume
by month: 2026-03 ≈138.8k, 2026-04 ≈213.5k, 2026-05 ≈82.2k; everything before
2026-03 is trace (a few hundred stray comments total).

The published chart's default series is **post+comment**. Comment-sourced tags
can therefore only ever exist for posts from ~March 2026 onward. Every theme
line has a structural discontinuity at March 2026: a step up that is a
data-coverage change, not a discourse change. CLAUDE.md §2.3 documents this; the
audit must not read the March-2026 step as a real-world event, and any
cross-March-2026 comparison should use the **post-only** control series.

---

## Summary — what is and isn't comparable across the timeline

| Property | Comparable over time? |
|---|---|
| Collection source | ✅ ~uniform (Arctic Shift), minor 2026 live/backfill seam |
| Monthly post volume (per-1k denominator) | ✅ continuous, no gaps |
| Body availability (drives keyword recall) | ❌ rises ~22 pts 2023→2026 — **inflates the rise** |
| Comment-sourced tags | ❌ exist only from 2026-03 — **step in post+comment series** |

Two of four properties are not constant. Neither breaks the audit's precision
findings (precision is judged per surviving tag), but both bear directly on
**Layer 3 (temporal comparability)** and feed the report's verdict on whether
the trend *shape* is honest.
