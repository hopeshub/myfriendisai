# Trend Atlas — comprehensive fix plan (2026-05-15)

Synthesizes a three-agent review (a hard critique of the live chart, a
precedent sweep, and a ranked options analysis) into one actionable plan.

**The verdict:** the small-multiples structure is correct — keep it. Every
problem is *execution*: the layout never gives an overview, the honesty cues
are too faint, the charts are under-powered, and there are real bugs. This is a
tuning-and-polish pass on a correct structure — **not a redesign.**

Builds on `docs/chart_redesign_plan_2026-05-15.md` and
`docs/data_presentation_proposals_2026-05-15.md`.

---

## 1. Diagnosis

- **No overview.** ~300px of chrome (headline + 3-line subtitle + contract
  paragraph + event legend) sits before the grid; panels are 248px tall with
  36px gaps. Result: on a normal laptop **zero complete charts are visible
  above the fold**, and the page runs ~2400px. Small multiples exist to be
  swept in one glance — this layout reads them sequentially, like paragraphs.
- **The honesty is opt-in.** All six panels are the same physical size, so the
  forbidden comparison — "which line is taller in its box" — is still the easy
  default glance. The detector label (`narrow/moderate/broad`), the single most
  important "don't compare heights" signal, is the *faintest* text on each
  panel. Visual weight is inversely proportional to epistemic importance.
- **Charts are under-powered.** 3-tick y-axes, no unit on the axis, gridlines
  near-invisible, `monotone` smoothing that invents between-month curve, and a
  y-domain that may not start at zero (truncated axes exaggerate).
- **Real bugs.** Tablet renders 1 column (wastes half the width). Event-marker
  numbers re-index per time range — ① means "Replika ERP" on ALL but
  "Sycophancy" on 1Y.
- **Precedent check (reassuring):** scrolling a 6-panel grid is *normal*
  professional practice (Pew ships 8-panel grids). The failure mode is not
  scrolling — it is scrolling with no orientation and no overview. Fix the
  overview; do not abandon the grid.

---

## 2. The plan

### A. Layout — make the grid fit ~one viewport
- **A1.** Compress the chrome: headline + a **single-line** measurement
  contract. Move the full explanation and the event legend into a collapsed
  `<details>` disclosure ("About this chart / events").
- **A2.** Genuine **3×2 grid**: panel height 248 → ~190px; row gap 36 → ~20px.
- **A3.** Restore **tablet 2-column** (`cols = bp === "mobile" ? 1 : 2`).
- **A4.** Rewrite each theme's `blurb` to **one line** (~10–14 words) — keeps
  the editorial voice, reclaims the vertical space it currently spends.
- **Target:** all six panels visible within ~1–1.15 viewport on a standard
  laptop. That is the "overview" the owner asked for.

### B. Honesty execution — make incomparability visually loud
- **B1.** Promote the **detector label** to a real, visible element (size and
  contrast) — not a faint tag with its meaning hidden in a tooltip.
- **B2.** Force every y-axis to **start at 0** (no truncated/exaggerated
  baselines); show the unit ("per 1k posts") clearly; 4–5 ticks, not 3.
- **B3.** Keep the one-line contract **co-present with the chart**, so it does
  not scroll out of view while the reader is on panels 3–6.
- *(Considered and rejected: varying panel heights to signal scale differences
  — too fragile. B1 + B2 carry it instead.)*

### C. Chart quality
- **C1.** `type="monotone"` → `type="linear"` — stop inventing between-month
  shape; more honest for monthly data.
- **C2.** Gridlines slightly more visible; axis tick text legible.
- **C3.** Make the y-domain policy explicit and identical across all six panels.

### D. Bugs & correctness
- **D1.** Tablet 1-column (covered by A3).
- **D2.** Number events by **fixed chronological order across the full set**,
  stable regardless of the selected time range — ① is always Replika ERP.
- **D3.** Mobile: detector label and "measurable from" caption to **≥14px**
  (the project's own mobile font floor).
- **D4.** Ensure event ticks/numbers are not cramped at the smaller panel size.

### E. Information architecture
- **E1.** Add a **visible "open detail" affordance** on each panel (a small
  chevron or "Details →"), discoverable on touch, not just a hover tint.
- **E2.** Consolidate the methodology text — it currently says the same caveat
  ~3× (subtitle, detector labels, footer). One concise contract + the detector
  labels + a short footer.
- **E3.** Keep a **deliberate, fixed panel order** and do **not** sort panels
  by value — sorting by value would itself imply the cross-theme ranking the
  whole design exists to prevent.

### Deferred (considered, not now)
- **Sparkline overview strip** — six mini-lines in one row as an at-a-glance
  index, click to expand a focused detail chart. The strongest "everything at
  once" option, but a real information-architecture change (detail becomes
  one-theme-at-a-time) and more to build. Revisit only if Section A does not
  deliver the overview feel.

---

## 3. How it's built

- One focused pass. Edits confined to `web/app/TrendAtlas.tsx`,
  `web/app/TrendsExplorer.tsx`, and `web/app/themes.ts` (one-line blurbs). No
  data-layer change, no new components.
- Build, then **screenshot-verify at desktop / tablet / mobile** before
  deploying — no blind deploys.
- Then commit + deploy as one change.

## 4. Acceptance criteria

- All six panels visible within ~one viewport on a standard laptop.
- The detector label is a clearly visible element, not the faintest thing on
  the panel.
- Every y-axis starts at 0; units shown.
- Tablet renders 2 columns; event numbers stable across time ranges.
- `npm run build` green; the page reads as an editorial atlas, not a
  scroll of paragraphs.

## 5. What this is NOT

Not a teardown. The honest independent-axis model, the editorial per-theme
readings, the amber event layer, and the post-only data series all stay. The
structure was the right call; this pass makes the execution match it.
