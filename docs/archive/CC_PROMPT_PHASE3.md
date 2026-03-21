# Phase 3: Chart Mobile Optimization

## Context

Read `docs/MOBILE_RESPONSIVE_SPEC.md` for the full project spec. Phases 1–2 should already be implemented. This prompt covers Phase 3.

The time-series chart is now above the fold on mobile (thanks to Phase 1), which means it actually needs to look good at that width. This phase is about making sure it does.

## Task

Optimize the time-series chart rendering for mobile viewports (≤768px). **Desktop chart must not change at all.**

## Requirements

### 1. Chart dimensions

- Chart should be full-width with 8px horizontal padding on each side (so it doesn't bleed to screen edges but still gets maximum width)
- Minimum height of 250px — do not let it squish below this. The chart is the main content; it deserves vertical space.
- If the chart currently has a fixed pixel height, make sure it doesn't shrink too small on mobile. If it uses a responsive aspect ratio, verify 250px minimum is respected.

### 2. Event annotation labels

This is the trickiest part. The chart has vertical dashed lines with rotated text labels for events like "Sycophancy update", "4o 1st sunset", "4o retired". At mobile widths these labels likely overlap or get cut off.

**Investigate which of these approaches works best with the current chart library:**

- **Option A (preferred):** Abbreviate the labels on mobile. Use shorter strings: "Syco. update" → "Syco.", "4o 1st sunset" → "4o sunset", "4o retired" → "4o ret." — or whatever fits. The goal is shorter text that doesn't overlap.
- **Option B:** Reduce the font size of annotation labels to ~10px on mobile.
- **Option C:** If the chart library supports it, replace visible labels with small marker dots/icons on the timeline, and show the full label on tap/touch via a tooltip.

Try Option A first. If the chart library makes it hard to conditionally change label text based on viewport, fall back to B, then C. Document which approach you used and why.

### 3. Axis labels

- **Y-axis:** Keep visible but reduce font size if needed. Make sure the numbers don't overlap the chart area.
- **X-axis (months):** At ~350px chart width, monthly labels (Apr 2025, Jun 2025, Aug 2025...) will likely overlap. Check if the chart library auto-thins them. If not, configure it to show every other month or every quarter on mobile. The chart library may have an `autoSkip` or `maxTicksLimit` option — use it.

### 4. Touch interaction

- If the chart has hover tooltips on desktop, verify they work on tap/touch on mobile
- If they don't, check the chart library's touch/mobile configuration options and enable them
- The tooltip should show the data point values for the tapped position

### 5. Line thickness

- At mobile widths, the chart lines might look too thin or too thick relative to desktop. Eyeball it — if the lines look spindly at mobile size, bump them up by 0.5-1px. If they look chunky, thin them. This is a judgment call.

## How to verify

1. Desktop chart is identical to before
2. On mobile: chart is full-width, at least 250px tall, doesn't look squished
3. Event annotations are readable and don't overlap each other
4. X-axis month labels don't overlap
5. Tapping on the chart shows a tooltip with data values
6. Lines are visually legible at mobile size
