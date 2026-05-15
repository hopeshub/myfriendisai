# Pre-launch comprehensive audit — 2026-05-14

Seven parallel specialized review agents read the project as it stood
on the morning of 2026-05-14, then a coordinated triage shipped fixes
across pipeline, content accuracy, mobile UX, and accessibility.

## Agents dispatched

1. **First-visitor experience** — cold reader, 3-min chart + 5-min about page
2. **Mobile experience** — iPhone 13 + 4G UX evaluation
3. **Hostile critic re-review** — same lens as 2026-05-13, on updated state
4. **Methodology + reproducibility reviewer** — could a researcher reproduce this?
5. **Technical / operational review** — pre-launch ops readiness
6. **Accessibility audit** — WCAG 2.1 AA compliance + screen reader experience
7. **Content accuracy review** — fact-check every public numerical claim

## Critical finding (acted on immediately)

**The daily pipeline had been broken for 3 days.** r/HeavenGF was returning
`Subreddit does not exist` (the sub was deleted on Reddit). The
`collect_daily.py` exit logic treated any per-sub error as fatal, which
made `run_collect.sh` skip the push step. Result: the live site has been
serving data from May 11 since May 12. The StaleDataBanner was firing
but no one was noticing because the failure-notification path
(`osascript display notification`) only works when the user is at the
Mac.

**Fixes shipped:**
- `config/communities.yaml`: r/HeavenGF deactivated
- `scripts/collect_daily.py`: per-sub errors now non-fatal unless they
  affect >50% of subs or a step itself fails

Tomorrow's 6am pipeline run will succeed and the banner will clear.

## Convergent findings across reviewers (high priority)

Multiple agents independently flagged these:

1. **Verification examples panel claims a system that "isn't running yet."**
   The chart subtitle and OG description implied LLM verification was live;
   the May 14 changelog said the LLM was over-rejecting and the default
   chart series was still raw keyword counts. Hostile critic and academic
   reviewer both flagged this as bait-and-switch.

   **Fix:** softened README + layout.tsx OG description to "rolling out"
   framing. Chart subtitle already softened earlier in the day.

2. **Numerical contradictions on the same page.**
   - "two-thirds of all sex/ERP-tagged posts" (page.tsx lines 911 and 988):
     actual share is 40% — three different agents flagged this.
   - "10 currently-flagged noisy keywords": the live Theme Health snapshot
     shows 20.
   - Rupture count "1,830 → 5,026": current count is ~4,800.
   - 3.8M vs 3.9M post count: README, layout.tsx, and stats card fallback
     all said 3.8M; site_meta.json reports 3,907,171.
   - Three different "inter-rater agreement" numbers (88%, 93%, 61.5%)
     referring to different sample/surface combinations without disambiguation.

   **Fix:** all of the above corrected on the public-facing pages.

3. **Default chart state looks broken.**
   First-visitor agent: "all six theme lines are dimmed to 20% opacity
   with no theme selected. I see six faint squiggles. A reader might
   bounce thinking the chart is broken."

   **Fix:** default opacity for un-selected state changed from 0.2 → 0.85.
   Selecting a theme still dims others to 0.2 (so the focus interaction
   works), but the default view is now legible.

4. **Color contrast failure.**
   `#64748B` body text on `#1A1D27` card background = 3.6:1 contrast,
   below the WCAG AA 4.5:1 minimum. Used in multiple places on the about page.

   **Fix:** all instances changed to `#94A3B8` (6.7:1).

## Mobile-specific fixes

- **BottomSheet close button**: 32px → 44px (Apple touch-target floor)
- **Theme Health snapshot grid**: 1-col on <640px, 2-col tablet+ (was
  forcing 2-col always, which wrapped "r/ChatGPTcomplaints (61%)" to 3
  lines on iPhone)
- **Verification example card headers**: stack on mobile, row on tablet+
  (was four metadata pieces on one cramped row)

## Accessibility fixes (WCAG 2.1 AA)

- **Skip-to-content link** added to layout (was missing — blocked by 2.4.1)
- **Chart wrapped in `<figure>` with `<figcaption>`** + `role="img"` +
  `aria-labelledby` (was completely silent to screen readers — blocked
  by 1.1.1 Non-text Content)
- **Recharts `outline: none !important`** scoped to `:not(:focus-visible)`
  so keyboard users still get focus indicators (was blocking 2.4.7)
- **Focus restored** to originating theme card after detail panel closes
  (was leaving keyboard users at top of DOM — blocked 2.4.3 Focus Order)

## Findings disclosed but NOT fixed in this audit (require user input or larger redesign)

- **Consciousness comment-level series at 51% precision** is still
  publicly visible. Methodology reviewer recommended suppressing it
  until the LLM gate ships properly. Currently disclosed via Theme
  Health snapshot color-coding (red).
- **Single-model calibration limitation** (Claude classifies, Claude
  audits, Claude calibrates) is disclosed in red text on the about page
  but a human-coded calibration set or cross-model validation would
  meaningfully strengthen the methodology.
- **DOI / Zenodo per-release snapshots** not shipped. Currently the
  citable URL is the live site, which moves daily. Academic reviewer
  flagged this as a citation-readiness gap.
- **r/ChatGPTcomplaints is 60% of three different comment-themes** —
  themes are confounded with subreddit selection. Documented in audits
  but not visually surfaced on the chart itself.
- **No live data backups.** The 24 GB SQLite DB is irreplaceable for
  the historical backfill portion (PullPush is dead). Ops reviewer
  flagged this as a launch risk.
- **Disk at 95% full.** Ops reviewer flagged this — a VACUUM or large
  WAL checkpoint could brick collection.

## What survives unscathed

- Methodology rigor is **unusually high for a non-institutional research
  artifact** (multiple reviewers said this).
- Audit transparency is **a moat** — every reviewer was struck by how
  much the site discloses about its own failures.
- The chart's **shape and timing signal** is honest and defensible.
- The **infrastructure (drift detection, theme health, calibration
  framework, monitor scripts)** is durable and scales to future work.

## Reviewer-reported vulnerability for launch

Hostile critic, paraphrased:
> "Substantially less than the previous review. The project has moved
> from 'misleading by omission' to 'self-flagellating in the footnotes.'
> A motivated hostile reviewer can still produce a takedown, but every
> attack now has a corresponding paragraph on the about page conceding
> the point. The dominant criticism shifts from 'this is misleading' to
> 'if you have to disclose this many caveats, why publish it?' — a
> softer, more philosophical attack."

Academic reviewer:
> "Would I cite this? MAYBE — as supplementary reference, with caveats.
> Not as primary evidence for any quantitative claim. Until it has a
> citable snapshot (DOI), a named author with affiliation, and a
> human-coded calibration layer, it lives in the 'useful pointer, not
> primary evidence' tier."

## Files modified in this audit pass

- `config/communities.yaml`
- `scripts/collect_daily.py`
- `web/app/about/page.tsx`
- `web/app/TrendsExplorer.tsx`
- `web/app/BottomSheet.tsx`
- `web/app/layout.tsx`
- `web/app/globals.css`
- `README.md`
- `CLAUDE.md`

## Commits

- `5695718` — pipeline fix + content/UX/a11y batch
- `e2da3ff` — first-visitor UX (default chart opacity)
- `c966595` — focus restore + CLAUDE.md keyword count
