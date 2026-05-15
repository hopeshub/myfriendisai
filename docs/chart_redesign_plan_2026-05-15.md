# Chart redesign — synthesized plan & build sequence (2026-05-15)

Synthesizes `docs/data_presentation_proposals_2026-05-15.md` (the "Trend Atlas"
proposals) with a three-agent research pass (internal diagnosis of the current
chart, real-world precedent survey, and a technique pressure-test). This is the
actionable plan; the proposals doc remains the fuller design rationale and the
research reports remain the evidence base.

---

## 0. Overriding design principle — visual quality and UX are paramount

The current site's look, feel, and usability are a real asset and must not
regress. This redesign is a *correctness* fix, not a downgrade to a clinical
"methods figure." The small-multiples grid must be executed as a polished,
deliberate editorial piece — keeping the existing dark editorial aesthetic,
theme colors, typography, spacing, smooth interactions, and responsive
behavior (the mobile bottom-sheet, etc.). A concrete mockup is reviewed and
approved by the owner before any production build — that review is the
visual-quality gate. If the grid does not clear the current site's polish
bar, the design iterates until it does.

## 1. The problem (one paragraph)

The current chart draws 6 theme lines on one shared y-axis. Each line's height
is roughly *true rate × that theme's detection rate*, and detection varies ~10×
between themes (rupture ~3%, addiction ~32%). A shared axis is an implicit
claim that heights are comparable — this data cannot support that claim.
Within-theme shape and timing over time are honest; cross-theme heights are not.
The six metric cards (six comparable-looking numbers in identical units) make
the invalid comparison even more directly than the chart does.

## 2. Settled design — every source agrees

- **Replace the overlaid 6-line chart with a small-multiples grid** ("Trend
  Atlas") — one panel per theme, 2×3 on desktop, 1×6 stacked on mobile.
- **Shared x-axis** across panels; **synchronized hover**; **shared event and
  methodology bands** across all panels (so cross-theme *timing* is still
  readable — that comparison IS valid).
- **Default data series: post-only** (`count_post_only`). Removes the
  March-2026 comment-tagging step artifact; comparable back through the 2017
  corpus. Post+comment becomes an optional surface toggle.
- **Remove "% of peak"** — it forces every theme to peak at 100, equating a
  one-day noise spike with a durable rise.
- **Per-panel detector chip** — `narrow detector` / `moderate detector` /
  `broad detector`, derived (coarsely) from the recall audit.
- **Measurement-contract subtitle on the chart itself**, not buried in
  methodology: *"Compare each theme's shape and timing over time — not theme
  heights as prevalence. Keyword sensitivity differs by theme."*
- **Cards become diagnostics, not a leaderboard** — fixed conceptual order (not
  sorted by value), within-theme trend, detector chip, top community; no
  cross-theme absolute number.
- **Reliability profile per theme** (detail drawer): what it catches, what it
  misses, detection coverage, post & comment precision, top communities,
  coverage start, one safe claim, one unsafe claim.
- **Distinguish event types**: product/community events as thin vertical
  markers; methodology changes (keyword expansions, comment-collection start)
  as shaded bands/tags — so an instrument change is never mistaken for a
  social spike.
- **Plain-language uncertainty** — coarse detector chips, not confidence-
  interval bands (bands would imply a recall correction the project does not
  perform). Exact recall figures live in the theme detail and downloads.
- **"Measurement begins" marker** at each theme's `coverage_start`, so
  consciousness starting in 2025 reads as "we could not measure this earlier,"
  not "this did not exist."

## 3. The one resolved disagreement — normalization within panels

The proposals doc recommends **baseline-indexing** (100 = a theme's average over
its first six months) on a shared panel y-axis. The research pressure-test
recommends **independent raw axes, no indexing**.

**Resolution: independent raw per-1k axes are the default. Baseline-index is a
later, optional, clearly-labeled toggle — not v1.**

Reasoning:
- Baseline-indexing requires an analyst-chosen baseline window. That is exactly
  the kind of judgment layer the project deliberately removed elsewhere this
  cycle (keeping raw `count` as the default series; demoting LLM verification).
  Making it the chart default is inconsistent with the project's own
  deterministic, reproducible, no-analyst-judgment philosophy.
- The early corpus is very sparse (single-digit daily counts). A baseline
  computed from sparse months carries large relative error, and indexing
  *divides* by it — freezing a permanent multiplicative error into the whole
  line. It trades a known, stable bias for an unknown, frozen one.
- Consciousness has a near-zero early baseline; indexing it explodes or forces a
  special-case exclusion. Independent raw axes handle every theme uniformly.
- Mismatched axes are the honest signal: the reader sees the panels do not
  share a scale and correctly infers heights are not comparable. An indexed
  shared axis re-invites "compare the index heights," which is itself
  baseline-contaminated.
- Independent raw axes also preserve within-theme absolute magnitude — real
  information — which indexing discards.

Per-panel y-axes must still show a couple of gridline labels (per Datawrapper's
rule for independent-scale small multiples) so each panel's scale is legible.

The "is this theme above/below its own baseline" question still gets served —
via the theme detail and, later, the optional indexed toggle — just not as the
parameter-laden default.

## 4. Deferred decision — the overlay / co-movement view

The proposals doc keeps the overlaid chart as an "Explore" mode. Recommendation:
**do not build it for v1.** The small-multiples grid with a shared x-axis and
shared event bands already lets a reader see co-movement (scan a date column
across panels). A separate overlay reintroduces the shared-axis comparability
problem and adds a surface to maintain. Add it later only if co-movement proves
to need its own view. (Owner may override.)

---

## 5. Build sequence

### Phase 0 — Make the current code honest (prerequisite; fixes real bugs)

The exporter and test suite are still entangled with the abandoned LLM path.
**6 tests currently fail** (`OperationalError` at `src/db/operations.py:484` —
`export_keyword_trends_json` queries `llm_classifications`, absent on a fresh
schema).

- **0.1** Guard the `llm_classifications` query in `export_keyword_trends_json`
  with a table-existence check (or remove it). Fixes the 6 failing tests.
- **0.2** Remove `count_llm_verified` / `count_llm_verified_7d_avg` from the
  public `keyword_trends.json` export. Update `CLAUDE.md` §2.3, which currently
  says the series stays in the export — change to "removed from the public
  export; LLM verdicts are audit data only."
- **0.3** Remove stale "flip the default to `count_llm_verified`" comments in
  `web/app/page.tsx`.
- **0.4** Reconcile community counts — 26 vs 27 tracked, 21 vs 22 keyword
  communities — across `web/public/status.json`, `subreddits.json`,
  `site_meta.json`, About-page copy, and OpenGraph/meta copy. Single-source.
- **0.5** Verify: `pytest` green, `npm run build` green; re-export
  `keyword_trends.json` so committed data matches the exporter. Commit +
  deploy — safe honesty cleanup, independent of the chart. *(The
  numerator/denominator smoothing mismatch is folded into Phase 1.1, which
  rebuilds the rate computation anyway — fixing it twice would be wasted work.)*

### Phase 1 — Build the Trend Atlas (the headline chart)

- **1.1** Data layer: compute monthly post-only per-1k rates per theme from the
  daily series (numerator + denominator on the same window); apply each theme's
  `_coverage_start`.
- **1.2** `ThemePanel` component — one small-multiple: raw per-1k line on its
  own y-axis (with minimal gridline labels), `coverage_start` "measurement
  begins" marker, event/methodology bands, detector chip in the title.
- **1.3** `TrendAtlas` component — 2×3 grid (1×6 mobile), shared x-axis,
  synchronized hover, shared event bands, the measurement-contract subtitle.
- **1.4** Swap the Atlas in as the landing page's primary chart; retire the
  overlaid `TrendsExplorer` chart and the "% of peak" toggle.
- **1.5** Rebuild the metric cards as per-theme diagnostic cards — fixed order,
  within-theme trend + sparkline, detector chip, top community; no cross-theme
  absolute number.
- **1.6** Style methodology events distinctly from product events.
- **1.7** Verify build; visual check at desktop and the 768px mobile breakpoint.
  Commit + deploy.

### Phase 2 — Reliability profiles

- **2.1** Extend the theme-health export with presentation-ready fields:
  `detector_coverage_label`, `safe_claim`, `unsafe_claim`, `misses_summary`,
  `recall_estimate` + CI, `precision_post`, `precision_comment`,
  `top_communities`, `coverage_start` — generated from audit constants +
  export-derived values, not hand-coded in React.
- **2.2** Theme detail drawer/sheet rendering those fields.
- **2.3** Wire each panel's detector chip to open the detail drawer.
- **2.4** Verify; commit + deploy.

### Phase 3 — Optional follow-ups (not v1)

- Baseline-index toggle, gated on baseline stability (themes whose baseline
  window is too sparse are not offered the toggle).
- Validation checks (proposals doc Proposal 9): assert community counts agree,
  `_coverage_start` present for all themes, no "LLM rolling out" copy, fresh-
  schema export works, stale `web/data` copies flagged.
- Overlay / co-movement view — only if it proves needed.

## 6. Acceptance criteria for the redesign

- No shared y-axis across themes in the default view.
- No cross-theme absolute number presented as comparable.
- A reader landing cold cannot easily make a "theme A > theme B" reading.
- The measurement contract is visible on the chart itself.
- post-only is the default; the March-2026 comment step is gone from the
  default view.
- `pytest` and `npm run build` both green.
- The redesign looks at least as polished as the current site and preserves
  its UX quality — verified against an owner-approved mockup before build.
