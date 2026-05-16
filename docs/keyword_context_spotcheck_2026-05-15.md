# Keyword context spot-check audit — 2026-05-15

A from-scratch audit of the project's core measurement assumption: **that the
production keyword set accurately tracks its six themes** — i.e. that when a
keyword fires, the post is really about that theme, in an AI-companion context.

This is a six-layer audit (precision, recall, temporal comparability, corpus
denominator, keyword fragility, conclusion loop). It re-classifies a large
production sample with independent CC agents under two rubrics and compares the
verdicts to the live `post_keyword_tags` table.

Reproducible artifacts: `analysis/keyword_pipeline/spotcheck_v2_build.py`,
`spotcheck_v2_score.py`, and everything under
`analysis/keyword_pipeline/spotcheck_2026-05-15/` (manifest, 64 agent batches,
64 result files, `scored_stats.json`, `corpus_diagnostics.md`).

---

## Bottom line

**The instrument is directionally sound but noisier than the project has been
treating it — and the noise is uneven by theme and not constant over time.**

Three findings, in order of importance:

1. **The referent is reliable; the theme is not.** When a keyword fires, the
   post is almost always genuinely about AI companionship (only ~2–3% are
   wrong-referent / non-AI / bot-card noise). The leakage is *within* the
   companion space: ~1 in 5 tagged posts is about AI companionship but a
   *different theme* than the keyword assigned it (`theme-mismatch` is the
   single largest failure mode, 434 of ~2,170 coded items). So "is this about
   AI companions?" → yes. "Is it about *this* theme?" → often enough, no.

2. **Precision is uneven and several high-volume keywords are weak.** Theme
   precision (volume-weighted, topical reading) ranges from **93% (sexual_erp)
   down to ~55–64% (therapy)**. Therapy's two highest-volume keywords
   (`emotional support`, `therapeutic`) sit near 55% even on a confirmatory
   n=100 read. A confirmatory read also *cleared* the highest-volume rupture
   keyword (`goodbye`, 1,754 tags): its n=20 screen of 55% was an unlucky draw
   — at n=100 it is 81%. (See "Confirmatory n=100 read" below — and treat every
   single-keyword n=20 number in this report as a screen with real error.)

3. **The instrument is not constant over time.** Per-theme precision swings
   20–30 points across years, and body-availability (which drives keyword
   recall) rises ~22 points from 2023→2026. The trend *shape* — "rose from
   nearly nothing" — is partly real and partly an artifact of the measuring
   instrument changing under the data.

None of this means the chart is broken. It means the public framing should be:
**these lines are stable indicators of theme-related language, not precise
estimates of theme prevalence** — and the recommended response is disclosure
and monitoring, not churning the keyword set (see Recommendations).

---

## What was done

| | |
|---|---|
| Items classified | 2,330 — 1,821 per-keyword precision posts (every one of the 92 keywords covered), 349 comment-tag items, 160 era-stratified untagged posts, 8 event-spike clusters |
| Method | 64 independent CC agents, each reading title+body fresh — **blind to the keyword and to the existing tag** |
| Rubrics | every item dual-coded: **topical** (the project's locked "when in doubt YES" standard) and **strict** (adversarial "when in doubt NO") |
| Coverage | precision 1,820/1,821 · comments 349/349 · negative-space 160/160 |

### Honest limitations of this audit

- **No human ground truth.** The planned 72-post human gold anchor was dropped
  at the reviewer's request. The audit is therefore LLM-graded. The dual-rubric
  **band is the safeguard** — the truth sits inside the topical–strict range,
  not at a point. Absolute numbers should be read as a range, never a figure.
- **Per-keyword n≈20** — a *screen*, not a verdict. Individual keyword numbers
  have wide confidence intervals (Wilson LBs are in `scored_stats.json`). Theme
  aggregates (n=159–427) and the cross-cutting patterns are the robust part;
  treat a single keyword's number as "investigate", not "proven".
- It re-uses the same theme definitions the chart uses; it does not re-litigate
  whether the six themes are the right carving.

---

## Layer 1–2 — precision, by theme

Volume-weighted by each keyword's production tag count, so this reflects what
the *chart* actually shows, not an unweighted keyword average.

| Theme | Topical | Strict | Band | Pooled n | Read |
|---|--:|--:|---|--:|---|
| sexual_erp | 92.8% | 74.3% | **74–93%** | 298 | Strongest. `erp`/`smut`/`sex with` land cleanly. |
| addiction | 90.4% | 78.0% | **78–90%** | 334 | Strong. Recovery-sub vocabulary is precise. |
| romance | 75.4% | 53.3% | **53–75%** | 411 | Moderate. Direct relationship terms good; `husbando`, `in a relationship with`, `ai lover` leak. |
| rupture | 70.2% | 58.4% | **58–70%** | 427 | Moderate. Event language solid; some grief words leak. |
| consciousness | 68.0% | 48.7% | **49–68%** | 191 | Weak. Polysemous terms; `personhood` itself only ~68%. |
| therapy | 55.1% | 40.1% | **40–55%** | 159 | Weakest. Its two biggest keywords (`emotional support`, `therapeutic`) are weak. |

**Correction after the confirmatory n=100 read (see below):** the table above is
built on the n=20 per-keyword screen. The n=100 read revised `goodbye` from 55%
to **81%**, which lifts **rupture's volume-weighted topical precision to ~78%**;
and put `emotional support`/`therapeutic` at ~55%, which lifts **therapy to
~64%**. Both themes are in better shape than the screened table shows — the
n=20 per-keyword screen carries error of ±10–25 points on an individual keyword.
Theme bands, corrected: rupture **~58–78%**, therapy **~55–64%**.

Overall: of ~2,170 coded post+comment items, **~62% pass both rubrics, ~17%
pass topical only (the band), ~21% fail both (clear false positives).**

### Keyword tiers (92 keywords, n≥8)

- **41 clean** (topical ≥85%) — the validated core works.
- **27 monitor** (70–84%) — defensible but soft-edged.
- **24 weak** (<70%) — listed below.

**Weakest keywords on the n=20 screen, with production volume** (topical %):
`not just an ai` 24% · `husbando` 35% · `emotional support` 40% (vol 571) ·
`more than code` 45% · `tulpa` 45% · `in a relationship with` 45% (vol 238) ·
`therapeutic` 45% (vol 328) · `soulbonder` 50% · `memory reset` 55% ·
`I was hooked` 55% · `goodbye` 55% (vol 1,754) · `lobotomies` 55% ·
`romantic relationship with` 60% · `devastated` 60% (vol 419) ·
`grieving` 60% (vol 423) · `sapience` 64% · `ai lover` 65% · `dating my` 65% ·
`we broke up` 65% · `farewell` 65% · `personality changed` 65% ·
`ai therapy` 65% · `lemoine` 68% · `personhood` 68%.

**These are n=20 screen values — a screen, not a verdict.** The confirmatory
n=100 read (below) revised all three keywords it re-checked *upward* — `goodbye`
55→81%, `emotional support` 40→56%, `therapeutic` 45→55%. So this list reliably
*flags candidates for closer reading*, but an individual number can be off by
10–25 points; do not cut a keyword on its screen value alone.

The pattern that does hold: weak keywords are disproportionately *generic
emotional/grief vocabulary* (`emotional support`, `therapeutic`, `grieving`,
`devastated`, `in a relationship with`), while *specific* vocabulary (`erp`,
`lobotomized`, `my ai boyfriend`, `relapsed`) is clean.

### The dominant failure mode: theme-mismatch

Failure reason codes across all non-YES verdicts:

| Reason | Count | What it means |
|---|--:|---|
| theme-mismatch | 434 | About AI companionship, but a *different* theme |
| thin-removed | 156 | `[removed]`/empty body; theme only inferable from title |
| third-party | 81 | Journalism / research solicitation / observer, no personal stake |
| rp-internal | 49 | Keyword only inside in-character roleplay narration |
| ambiguous | 43 | Genuinely undecidable |
| bot-card | 25 | Keyword is a character-card trait tag |
| ironic-rejection | 20 | Author explicitly denies the frame |
| wrong-referent | 17 | Keyword about a human, no AI |
| non-ai-literal | 9 | Literal non-AI use |

`wrong-referent` + `non-ai-literal` + `bot-card` = 51 items (~2%). **The
community filter works** — keywords are not catching non-AI discourse. The
problem is theme assignment inside the companion space.

### Confirmatory n=100 read

The n=20 per-keyword screen flagged `goodbye`, `emotional support`, and
`therapeutic` as the worst high-volume keywords. Because n=20 has wide
confidence intervals, all three were re-read at n=100 (300 fresh posts, same
blind dual-rubric protocol; `spotcheck_confirm_build.py`):

| Keyword | n=20 screen | n=100 topical | n=100 strict | topical 95% CI |
|---|--:|--:|--:|---|
| `goodbye` (rupture) | 55% | **81%** | 65% | 72–87% |
| `emotional support` (therapy) | 40% | **56%** | 37% | 46–65% |
| `therapeutic` (therapy) | 45% | **55%** | 37% | 45–64% |

Two lessons:

1. **`goodbye` is not weak.** At n=100 it is 81% topical — monitor-grade, not a
   problem keyword. The n=20 screen mis-drew by 26 points. Because `goodbye`
   carries 1,754 production tags, correcting it lifts rupture's volume-weighted
   topical precision from 70% to **~78%**.
2. **Therapy's two big keywords are genuinely weak** — both ~55% confirmed at
   n=100. Correcting them lifts therapy from 55% to **~64%**, but ~55% on its
   two highest-volume keywords still makes therapy the noisiest theme.

All three confirmations moved *upward* from the screen. Treat every n=20
per-keyword number in this report as a flag for investigation, not a verdict;
the theme-level aggregates (pooled n=159–427) are the trustworthy layer.

---

## Layer 3 — temporal comparability (the trend-shape question)

The chart's value is the *trend*. For the slope to be honest, the instrument
must measure the same thing in 2023 as in 2026. It does not.

### Precision drifts by year

Topical precision, per theme per year (n in parentheses):

| Theme | 2023 | 2024 | 2025 | 2026 |
|---|--:|--:|--:|--:|
| therapy | 74% (38) | 80% (40) | 67% (51) | 59% (22) |
| consciousness | 67% (15) | 67% (9) | 59% (94) | 61% (51) |
| addiction | 77% (30) | 75% (59) | 89% (153) | 94% (86) |
| romance | 75% (106) | 72% (64) | 78% (164) | 74% (31) |
| sexual_erp | 93% (152) | 89% (44) | 75% (64) | 63% (16) |
| rupture | 88% (105) | 69% (77) | 67% (94) | 82% (128) |

Romance is roughly flat (good). The others swing 15–30 points. `addiction`
precision *rises* over time; `sexual_erp` and `therapy` *fall*; `rupture` is
non-monotonic. Edge-year cells (e.g. sexual_erp 2026 n=16) are small — read
direction, not the decimal — but the headline holds: **a theme line is not a
constant-precision instrument, so part of its year-over-year movement is the
instrument changing, not discourse changing.**

### The corpus itself changed (from `corpus_diagnostics.md`)

- **Body availability rises ~22 points 2023→2026** (55.9% → 77.7% of self-posts
  have a readable body; older posts were `[removed]`/`[deleted]` before
  archival). Keywords match title+body, so older years have structurally less
  text to match → **older-year theme prevalence is undercounted → the rise is
  overstated.** This is uniform across themes, so it distorts slope/magnitude
  but not the relative ordering of themes or the timing of spikes.
- **Comment-sourced tags exist only from March 2026.** The default post+comment
  series has a hard step there that is a data-coverage change, not a discourse
  change. Cross-March-2026 comparisons should use the post-only control.
- Post volume (the per-1k denominator) is continuous with no collection gaps —
  the denominator is trustworthy; the artifact is entirely numerator-side.

**Verdict on Layer 3:** the trend *shape* is approximately honest in direction
and in the timing of events, but the magnitude of the rise is inflated by two
compounding instrument artifacts. "Rose from nearly nothing" overstates how low
the early baseline truly was.

---

## Layer 4–5 — fragility, comments, recall, spikes

### Single-keyword fragility

Posts caught by exactly one keyword of a theme are consistently 6–16 points
less precise than posts caught by multiple — confirming the weak signal leaks
in through single-keyword posts.

| Theme | single-keyword topical | multi-keyword topical |
|---|--:|--:|
| therapy | 70.5% (n149) | 80.0% (n10) |
| consciousness | 58.8% (n160) | 71.0% (n31) |
| addiction | 81.2% (n229) | 97.1% (n105) |
| romance | 74.6% (n343) | 89.7% (n68) |
| sexual_erp | 84.9% (n212) | 87.5% (n40) |
| rupture | 76.1% (n326) | 77.6% (n85) |

### Comment-sourced tags

| Theme | Topical | Strict |
|---|--:|--:|
| sexual_erp | 95% | 83% |
| addiction | 85% | 67% |
| rupture | 85% | 62% |
| therapy | 77% | 65% |
| consciousness | 76% | 53% |
| romance | 68% | 48% |

Comment precision tracks post precision — no separate comment-specific
collapse, but romance and consciousness comments are weak (matching the
adversarial audit's earlier read).

### Recall / negative space

160 untagged posts from companion subs, era-stratified. Of these, themes that
keyword matching *missed*: **rupture 37, romance 9, consciousness 3,
sexual_erp 3, addiction 1, therapy 1.** Rupture is by far the most
under-captured — it is frequently expressed in plain language ("site is down",
"what happened to my bot") that no keyword catches. This re-confirms the
documented precision-first / recall-floor trade-off; the chart is a floor.

### Event-spike integrity

Every sampled event spike is coherent: rupture 2024-09-24 (CharacterAI old-site
loss) 100%, rupture 2026-02-13 (4o retirement) 100%, the sexual_erp Feb-2023
cluster (Replika ERP removal) 87.5–100%. **The dramatic spikes are real events,
not keyword accidents** — the most reassuring single result in the audit.

---

## Reconciliation with prior audits

This audit's *topical* numbers track the 2026-05-13 robustness audit's manual
read (rupture ~70% both; sexual_erp ~92% both; consciousness/romance within
sampling noise). They sit far below the 2026-05-15 lenient-LLM audit's 93–97%
— which that audit itself flagged as inflated by a rubber-stamping prompt. The
*strict* column is the adversarial floor, consistent with the adversarial
audit's 51–72% comment range. So: nothing here contradicts the project's own
prior work — it quantifies, at much larger scale and stratified by year, the
gap the project already suspected. The per-keyword shocks vs the admission-time
validation docs (`husbando` 95%→35%, `emotional support` 100%→40%) are real:
admission samples were small, drawn at a point in time, and the volume-weighted
view exposes that a theme's biggest keywords are often its weakest. (A manual
read of 20 `husbando` posts during this audit confirmed it: on r/CharacterAI it
is mostly fandom vocabulary — "best husbando?", "favorite waifu/husbando" — not
the author's own AI romance.) An independent parallel review (Codex,
2026-05-16) reached the same directional conclusions: sexual_erp cleanest,
consciousness weakest, therapy soft, `goodbye`/`honeymoon`/`hours a day`
flagged — convergence from a separate method.

---

## Conclusion loop — which on-site claims survive

| Claim on the site | Survives? |
|---|---|
| These are genuine AI-companion communities; the project tracks real AI-companionship discourse | **Yes.** The referent axis is clean (~2–3% non-AI noise). |
| Event annotations (Replika ERP removal, CharacterAI shutdown, 4o retirement) | **Yes.** Spike posts are coherent; spikes are real events. |
| Per-theme trend *lines* as indicators of theme-related language | **Yes, with disclosure.** sexual_erp, addiction, and (corrected) rupture ~78% are solid; romance ~75% is moderate; **therapy ~64% and consciousness ~68% are the weak pair — present them as rough indicators, not measurements.** |
| Absolute theme *prevalence* / "X% of posts are about Y" | **No.** ~20–45% of a theme's tags are off-theme depending on theme; the chart is a noisy floor, not a prevalence estimate. |
| The trend *shape* / "rose from nearly nothing" | **Partially.** Direction and event timing are honest; the steepness of the rise is inflated by body-availability drift and precision drift. |
| Year-over-year headline numbers as precise change | **No.** Precision drifts 15–30 pts across years; YoY partly measures the instrument, not discourse. Keep the existing base-rate framing; do not sharpen it. |

---

## Recommendations

The right response to an uneven instrument in a fast-moving language
environment is **disclosure and monitoring, not reactive keyword churn** —
constant edits would destroy the longitudinal comparability that is the
project's main asset. Concretely:

1. **Do not cut keywords on this audit alone.** n≈20 per keyword is a screen.
   The n=100 confirmatory read is done for the top three flagged: `goodbye`
   cleared (81% — keep), `emotional support` and `therapeutic` confirmed weak
   (~55%). Still un-confirmed at n=100: `grieving`, `devastated`,
   `in a relationship with`, `husbando` — run those before any cut/guard.
2. **Add a "monitored keywords" list** (internal, separate from
   `keywords_v8.yaml`) for the 24 sub-70% keywords, so weak terms are tracked
   without forcing chart changes. Fold the worst into the monthly drift check.
3. **Disclose on the About page**: per-theme precision *bands* (not point
   numbers), the therapy/consciousness weakness, and the body-availability
   caveat on the early trend. The site already flags therapy as noisy — extend
   that honesty to consciousness and to the rise's steepness.
4. **Treat any keyword change as a versioned v9 methodology update** — historical
   re-tag, changelog entry, and (if a line visibly moves) an event-style
   methodology marker. Change the instrument only when a keyword is clearly
   failing *and* visibly distorting a published line.
5. **Re-run this audit** (`spotcheck_v2_build.py` → fleet → `spotcheck_v2_score.py`)
   on a fixed cadence — it is now reproducible — and ideally with the 72-post
   human gold anchor coded once, to pin the topical–strict band to a true point.
