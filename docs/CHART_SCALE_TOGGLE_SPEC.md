# Chart Scale Toggle — Absolute vs Relative

**Created:** March 16, 2026  
**Purpose:** Add a toggle to the main chart that lets the user switch between two views of the same data. Fix the coherence gap between the metric cards and the chart.

---

## The Problem

The metric cards show hits per 1,000 posts (absolute rate). The chart shows a Google Trends-style relative index (each theme normalized to its own peak = 100). These are completely different units displayed on the same page with no explanation. A visitor sees "4" on a card and "75" on the chart and has no way to connect them.

---

## The Fix

Add a two-state toggle near the chart that switches between:

### "Absolute" mode (hits per 1k posts)
- Y-axis: shared scale across all themes, unit is "per 1k posts"
- All themes plotted on the same scale — directly comparable
- A theme at 6 is visually 3x taller than a theme at 2
- Y-axis label: "hits per 1,000 posts"
- This matches the unit shown on the metric cards
- Data source: use the existing `hitsPerK` computation (count_7d_avg / total_posts × 1000) per day, then plot the 7-day rolling average

### "Relative" mode (% of peak — what exists now)
- Y-axis: 0–100 scale, each theme independently normalized to its own peak
- Shows the shape of each theme's trajectory relative to itself
- Small themes like Rupture are as visually prominent as large themes like Sex/ERP
- Y-axis label: "% of peak"
- This is the existing chart behavior, unchanged

---

## Toggle UI

A small segmented control (two buttons) placed to the right of the time range selector (6M / 1Y / ALL).

```
[ 6M ] [ 1Y ] [ 2Y ] [ ALL ]          [ Absolute ] [ Relative ]
```

**Styling:**
- Same visual style as the time range buttons — consistent UI language
- Active state: filled/highlighted
- Inactive state: text only, subtle border
- Minimum 44px height on mobile for tap targets

**Default state:** Absolute. This is the honest, comparable view and should be what a new visitor sees first. Users who want to examine individual theme trajectories can switch to Relative.

**Label text:** Use exactly "Absolute" and "Relative" — not "Raw" / "Normalized" or "Actual" / "Indexed." These are the clearest terms for a non-technical audience.

---

## Behavior When Toggling

- The chart transitions between modes without a full re-render — ideally an animated smooth transition of the lines
- The metric cards do NOT change — they always show the absolute rate regardless of chart mode
- The time range selection is preserved when toggling
- The active/highlighted themes are preserved when toggling
- Event annotation lines remain visible in both modes
- Tooltip values update to match the current mode:
  - Absolute: "Romance: 5.3 per 1k" 
  - Relative: "Romance: 73% of peak"

---

## Y-Axis Labels

### Absolute mode
- Show actual values: 0, 2, 4, 6, 8, 10 (or whatever auto-scales to the data range)
- Include the unit on the axis title or the first label: "per 1k posts"
- Use 1 decimal place if values are small (e.g., "2.5")

### Relative mode  
- Show: 0, 25, 50, 75, 100
- Include the unit: "% of peak"
- Add a subtle note below the chart or as a tooltip on the axis label: "Each theme scaled to its own maximum = 100"

---

## Absolute Mode — Data Computation

The existing frontend computes `hitsPerK` for the metric cards. Reuse that same computation for the chart data in absolute mode:

```
For each date, for each theme:
  absolute_value = count_7d_avg / total_posts_that_day × 1000
```

Plot these values directly. Do NOT do monthly aggregation — use daily values with the 7-day rolling average, matching the granularity of the relative mode.

If `total_posts` for a given day is 0 or missing, skip that data point (don't plot 0, which would create false dips).

---

## Relative Mode — Data Computation

This is the existing behavior. No changes needed. Keep the current per-theme normalization logic exactly as-is.

---

## Responsive Behavior

### Mobile (< 640px)
- The toggle sits on its own row between the time range selector and the chart
- Full width, two buttons evenly split: `grid-template-columns: 1fr 1fr`
- 44px height for tap targets

### Tablet (640px – 1023px)
- Toggle sits to the right of the time range selector (same row if space allows, own row if not)

### Desktop (≥ 1024px)
- Toggle sits to the right of the time range selector, same row
- Compact size, doesn't need to be full width

---

## What NOT to Build

- Don't add a third mode (log scale, percentile, etc.) — two modes is enough
- Don't animate the toggle transition if it causes a visible flicker or re-layout — a clean instant swap is fine
- Don't change the metric cards based on the toggle — they always show absolute
- Don't add explanatory tooltips or info icons on v1 — the labels "Absolute" and "Relative" plus the y-axis units are sufficient

---

## Implementation Notes

The key data for absolute mode already exists — `hitsPerK` is computed server-side in `page.tsx`. The frontend just needs to:

1. Pass both the relative (existing) and absolute datasets to the chart component
2. Add state for the current mode
3. Switch which dataset the chart renders based on the mode
4. Update the y-axis config (labels, scale, unit) based on the mode
5. Update tooltip formatting based on the mode

This should NOT require changes to the JSON export pipeline or any backend work. All computation happens client-side from the existing `keyword_trends.json` data.

---

## CC Prompt

```
Read docs/FRONTEND_DESIGN_SPEC.md, docs/MOBILE_SPEC.md, docs/METRIC_CARDS_SPEC.md, and docs/CHART_SCALE_TOGGLE_SPEC.md. Add the absolute/relative chart toggle as described in the CHART_SCALE_TOGGLE_SPEC. Default to absolute mode. Place the toggle to the right of the time range selector. Update y-axis labels and tooltips for each mode. Do not change the metric cards — they always show absolute. Do not add features from the "What NOT to Build" section.
```
