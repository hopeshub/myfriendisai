# Keyword context spot-check plan and initial execution

Date: 2026-05-16

## Bottom line

The keyword method is directionally sound, but the robustness is uneven by
theme. That is not a reason to keep changing the instrument. In a fast-moving
language environment, too much reactive maintenance would make the time series
less trustworthy, not more. The strongest version of this project is a stable,
validated vocabulary basket with documented limits, monitored drift, and rare
versioned methodology changes when the instrument has clearly stopped measuring
what it was built to measure.

This does not mean the chart is broken. The sample below intentionally
oversamples risky terms, so it should not be read as the production precision
rate. It means the public interpretation should be explicit: these lines are
stable indicators of recurring language, not live estimates of total theme
prevalence.

## Stability principle

The project should distinguish three layers:

1. **Production measurement instrument**: the frozen keyword set used for the
   public chart. This should change rarely. Its main virtue is longitudinal
   comparability.
2. **Monitoring layer**: periodic spot-checks, drift checks, negative-space
   samples, and notes about changing language. Monitoring can identify weakness
   without immediately changing the chart.
3. **Versioned instrument changes**: occasional, documented keyword additions,
   cuts, or guarded rules. These should be treated like methodology changes:
   rerun historical tagging, mark the change in the changelog, and avoid
   presenting pre-/post-change movement as pure discourse movement.

The central claim should be: this site tracks a stable, validated vocabulary
basket over time. It is optimized for consistency and interpretability, not
total coverage. When language changes, the project records that limitation
first; it changes the measuring instrument only when the old instrument is
clearly failing.

## What I built

I added a reproducible audit builder:

- `analysis/keyword_pipeline/context_spotcheck_audit.py`

It generates five artifacts from the current production database:

- `analysis/keyword_pipeline/results/context_spotcheck_summary_2026-05-16.md`
- `analysis/keyword_pipeline/results/context_spotcheck_per_keyword_sample_2026-05-16.csv`
- `analysis/keyword_pipeline/results/context_spotcheck_manual_focus_sample_2026-05-16.csv`
- `analysis/keyword_pipeline/results/context_spotcheck_negative_space_sample_2026-05-16.csv`
- `analysis/keyword_pipeline/results/context_spotcheck_event_spike_sample_2026-05-16.csv`

I also coded the risk-focused sample here:

- `analysis/keyword_pipeline/results/context_spotcheck_initial_manual_coding_2026-05-16.csv`

Rerun with:

```bash
python3 analysis/keyword_pipeline/context_spotcheck_audit.py --audit-date 2026-05-16
```

## Audit design

The audit asks two separate questions for each hit:

1. Is the post actually in an AI-companion / AI-companion-use context?
2. Is the matched keyword being used in the intended theme context?

The full check has six layers:

1. **Scope gate**: restrict review to active T1-T3 keyword communities and
   `source='post'`, because that is the public chart series. Exclude known
   platform/dev accounts.
2. **Per-keyword positive sample**: sample every current keyword, not just the
   suspicious ones.
3. **Risk-focused oversample**: oversample high-volume terms, known ambiguous
   terms, concentrated terms, and terms with low relative agreement in the old
   audit verdicts.
4. **Negative-space recall sample**: sample untagged recent posts, stratified
   evenly across active keyword communities, and ask which themes were missed.
5. **Spike integrity sample**: sample the largest dates per theme and verify
   the spike has a coherent event/story rather than a keyword accident.
6. **Decision thresholds**: keep terms at 85%+ clean context agreement. Terms
   at 70-84%, or terms with clear concentration/false-positive clusters, become
   monitored terms. Guard or cut only when a term is persistently below 70%,
   is driving a visible public-chart distortion, and the change is worth a
   versioned methodology update.

## Current production universe

From the 2026-05-16 audit run:

- Active keyword communities: 21
- Current keywords: 92
- Keywords with at least one production post hit: 92
- Sum of per-keyword distinct post hits: 20,622

Theme hit totals in the post-only audit universe:

| Theme | Per-keyword post hits |
|---|---:|
| therapy | 1,426 |
| consciousness | 496 |
| addiction | 3,129 |
| romance | 2,680 |
| sexual_erp | 7,259 |
| rupture | 5,632 |

Scope wrinkle: there are 30 stale tagged posts from inactive `r/HeavenGF` in
the database. The chart/export path filters active keyword communities, but
manual audits should keep using the explicit active-community filter.

## Initial manual coding

I manually coded the 69-item risk-focused sample. Because this sample
deliberately overrepresents ambiguous terms, treat these rates as a problem
finder, not a production estimate.

| Theme | Sample n | Theme YES | Borderline | NO | Read |
|---|---:|---:|---:|---:|---|
| therapy | 9 | 7 | 2 | 0 | Strong, but broad adjectives create soft edges. |
| consciousness | 9 | 3 | 2 | 4 | Weakest first-pass result; several terms are polysemous. |
| addiction | 12 | 9 | 2 | 1 | Mostly strong; `hours a day` has a clear FP mode. |
| romance | 12 | 7 | 3 | 2 | Real AI romance is present, but roleplay/product metaphors leak in. |
| sexual_erp | 12 | 11 | 1 | 0 | Strongest context validity in the sample. |
| rupture | 15 | 10 | 2 | 3 | Event spikes are real; broad grief/farewell language needs guarding. |
| **Total** | **69** | **47** | **12** | **10** | Risk-focused, not representative. |

## Theme findings

### Sex / ERP

This is the cleanest theme in the spot-check. `erp`, `sex with`, and `smut`
are overwhelmingly being used in AI-sexual/ERP contexts. The main caveat is
commercial/platform language such as custom NSFW character building, which is
still about sexual AI content but less personally grounded than the ideal
example.

Stability read: keep as-is. This theme is a good benchmark for what strong
keyword/context alignment looks like.

### Addiction

The addiction terms mostly work. Posts matching `my addiction`, `screen time`,
and `finally deleted` usually describe compulsive use, quitting, withdrawal, or
real-life impairment. The clear weak spot is `hours a day`, which can describe
ordinary work/computer use rather than AI dependency.

Stability read: keep the theme as-is for the current production instrument.
Track `hours a day` as a monitored term. Do not change it unless repeated drift
checks show it is driving visible distortion rather than contributing tolerable
noise.

### Therapy

The sample supports the theme, but with soft edges. `emotional support` is
doing real work. `therapeutic` sometimes means genuine therapeutic use, but it
can also be a casual adjective. `coping mechanism` mostly catches the intended
construct, though one sampled post reversed the direction and described the AI
as having the coping mechanism.

Stability read: keep, but publicly continue to label therapy as noisier than
the other themes. Treat `therapeutic` as a monitored term rather than an
immediate fix target.

### Romance

The direct relationship terms are good: `my ai boyfriend`, `my ai partner`,
`in a relationship with`, and wedding/marriage terms often capture exactly the
phenomenon the site is trying to show. The leakage is also clear:
`honeymoon` can mean product novelty, and `we broke up` can refer to fictional
roleplay rather than an actual user-AI relationship.

Stability read: keep the theme, but do not overclaim absolute volume. Track
`honeymoon` and `we broke up` as monitored terms. A future version could guard
`honeymoon phase` when it clearly means product novelty, but that should be a
versioned instrument change, not a quiet patch.

### Consciousness

This is the most fragile theme. Strong terms like `personhood` can be excellent
when the post is actually about AI rights, memory, and continuity. But
`not just an ai` and `subjective experience` are weak in a keyword-only system:
they can refer to marketing copy, human subjective experience, or comparisons
that do not engage AI consciousness at all.

Stability read: this should be disclosed as the narrowest and most
subculture-sensitive indicator, not treated as a broken line. The follow-up is
not "fix consciousness now"; it is to run a targeted review and decide whether
the current consciousness basket is still a useful stable proxy. If a future
version cuts or guards `not just an ai` / `subjective experience`, rerun
history and mark the change as a methodology update.

### Rupture

The event-level signal is real. The spike samples for the 2024 CharacterAI old
site shutdown and the 2026 4o retirement are coherent. But broad words like
`goodbye`, `grieving`, and `devastated` can catch ordinary farewells, user
departures, ads, pre-existing human grief, or general sadness.

Stability read: keep the theme, and present it as strongest for event spikes.
`goodbye` is the top monitored term: it had two clear false positives in a
3-item risk sample and is also the highest-volume rupture term. A guarded
matcher could improve precision, but it would also change the historical
instrument; make that only as a versioned update if the current term proves to
be distorting the rupture line.

## Spike integrity

The event-spike sample now takes the top two dates per theme, not just the
largest global spikes. Early read:

- `sexual_erp`: February 2023 Replika ERP removal is extremely coherent.
- `rupture`: September 24, 2024 old CharacterAI site loss and February 13,
  2026 4o retirement are coherent.
- `romance`: February 9, 2021 is heavily driven by repeated Replika wedding
  posts; real but concentrated.
- `therapy`: June 10, 2024 appears to mix real therapy/dependency language
  with an outage day. This spike needs closer reading before using it as a
  clean therapy-story example.
- `consciousness`: the top dates appear concentrated in
  `r/BeyondThePromptAI` and `r/ChatGPTcomplaints`; probably valid but highly
  subculture-specific.

## Recall / negative-space plan

The negative-space sample is now evenly stratified: 6 untagged recent posts
from each active keyword community, 120 total. It is ready to code.

This sample should be coded with a permissive question: "Is any of the six
themes clearly present even though no keyword fired?" The goal is not to add
all missed language to the chart. It is to estimate whether the keyword floor
is stable enough over time and which themes are most undercounted.

The first title scan already shows expected missed categories:

- standalone `NSFW` / sexual roleplay language that does not use current ERP
  phrases;
- AI-relationship posts that do not use the explicit romance terms;
- birthday/continuity/memory attachment posts;
- platform-loss posts that use generic outage/end language.

That aligns with the existing recall story: the chart is a high-precision
floor, not a comprehensive prevalence estimate.

## Governance recommendation

Do not continuously edit the production keyword set. Use this governance rule:

1. **Monitor without changing**: run spot-checks and drift checks on a fixed
   cadence. Record findings even when no code or keyword change follows.
2. **Promote to review**: a term becomes a review term if repeated samples show
   coherent false-positive drift, community migration, or a major change in how
   the phrase is used.
3. **Version only when necessary**: change production keywords only if the
   current term is clearly failing, the failure affects chart interpretation,
   and the fix is worth losing perfect continuity with prior exports.
4. **Rerun history**: every production keyword change should rerun historical
   tagging so the chart remains internally comparable under the new instrument.
5. **Mark the instrument change**: add an About/changelog note and, if the line
   visibly moves, an event-style methodology marker.

## Concrete next actions

1. Keep the current production chart stable for now.
2. Code the 276-row per-keyword sample for the top monitored terms:
   `goodbye`, `not just an ai`, `subjective experience`, `hours a day`,
   `honeymoon`, `we broke up`, `therapeutic`, and `emotional support`.
3. Code the 120-row negative-space sample to better estimate what the stable
   instrument misses.
4. Add a small internal "monitored terms" registry, separate from the
   production keyword file, so weak or drifting terms are tracked without
   forcing immediate chart changes.
5. Revisit production keyword changes only as a future v9-style methodology
   update, with historical rerun and public changelog.
