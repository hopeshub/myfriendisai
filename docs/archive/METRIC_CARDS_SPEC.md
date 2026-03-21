# myfriendisai — Metric Cards Spec

**Created:** March 15, 2026  
**Purpose:** Add a row of metric cards above the main trends chart. Each card shows a theme's current prevalence, a sparkline, and acts as the theme toggle (replacing the existing toggle row).  
**Prerequisite docs:** `docs/FRONTEND_DESIGN_SPEC.md`, `docs/MOBILE_SPEC.md`

---

## What This Replaces

Remove the existing horizontal theme toggle row (the pill-shaped buttons with emoji + label). The metric cards take over that job — clicking a card highlights that theme in the chart below. The toggle interaction logic stays the same, just the UI element changes.

---

## Layout

Six cards in a single horizontal row above the main chart, between the time range selector and the chart area.

Page structure top to bottom:

1. Header (site name + nav)
2. Headline + dynamic summary
3. Time range selector (6M / 1Y / ALL)
4. **Metric cards row (NEW — this spec)**
5. Main trends chart
6. Footer

---

## Card Design

Each card contains, top to bottom:

1. **Theme label** — 11px, `color: var(--secondary-text)` (muted gray), regular weight
2. **Value** — 20px, `font-weight: 500`, theme color, tabular figures. This is the average hits per 1,000 posts for the currently selected time range.
3. **Unit label** — 10px, muted gray, reads "hits / 1k posts"
4. **Sparkline** — 24px tall, showing the trend over the selected time range. Line color = theme color. No axes, no labels, no points — just the line.

**Card container styling:**
- Background: `#1A1D27` (same as chart area surface from FRONTEND_DESIGN_SPEC)
- Border-radius: 8px
- Padding: 12px 10px
- Left border accent: 3px solid [theme color]
- No other borders

**Card dimensions:**
- All six cards equal width, filling the container
- Gap between cards: 8px
- Cards should use CSS grid: `grid-template-columns: repeat(6, 1fr)`

---

## Card Order

Cards are sorted by value, descending (largest theme first, smallest last). Recalculate sort order when the time range changes — a theme that's biggest in ALL might not be biggest in 6M.

---

## Interactive Behavior

### Click/Tap to Toggle
- Clicking a card highlights that theme in the main chart below (same behavior as the old toggle pills)
- Multiple themes can be active simultaneously
- Active card: full opacity, theme color on the value text
- Inactive card: reduced opacity (0.5) on the entire card
- Default state (page load): all cards at full opacity, all themes faint in the chart (matching existing default behavior from FRONTEND_DESIGN_SPEC)

### Hover (Desktop Only)
- On hover: subtle background lightening — `#1F2233` or similar (+1 stop lighter)
- Cursor: pointer
- No hover effect on mobile/tablet (touch devices)

### Value Updates
- When the user switches time range (6M / 1Y / ALL), each card's value recalculates to show the average hits/1k for that period
- The sparkline also updates to show only the selected time range
- Card sort order recalculates (re-sort by new values)

---

## Computing the Value

For each theme, for the selected time range:

```
value = average of all daily count_7d_avg values in the time range
```

Round to nearest integer. Use `count_7d_avg` (the 7-day rolling average), not raw `count` — this matches what the main chart displays and avoids noisy daily spikes.

If a theme merges multiple JSON categories (check FRONTEND_DESIGN_SPEC for the merge table), sum the `count_7d_avg` values for the merged categories before averaging.

---

## Sparkline Implementation

Each sparkline is a tiny line chart rendered in a `<canvas>` element inside the card.

**Specs:**
- Height: 24px
- Width: fills card width (minus card padding)
- Line color: theme color
- Line width: 1.2px
- Tension: 0.4 (smooth curve)
- No fill / no area — just the line
- No points, no axes, no grid, no labels, no tooltip
- Data: the daily `count_7d_avg` values for the selected time range, downsampled if needed

**Downsampling:** If the time range has more than 60 data points (e.g., ALL with 3+ years of daily data), downsample to ~60 points by averaging every N consecutive days. This keeps the sparkline performant and visually clean — you don't need daily resolution at 24px tall.

**Chart library:** Use whatever charting library the main chart uses (likely Recharts or Chart.js). If using Recharts, a `<LineChart>` with all axes/grid/tooltip disabled. If using Chart.js, a minimal line chart with `display: false` on both scales.

---

## Responsive Behavior

### Mobile (< 640px)
- Switch from 6-column grid to **2-column grid, 3 rows**: `grid-template-columns: repeat(2, 1fr)`
- Card order: still sorted by value descending, flows left-to-right then top-to-bottom
- Cards maintain 44px minimum tap target height (they'll naturally exceed this with the content)
- Value font size: 18px (slightly smaller)
- Sparkline height: 20px
- Gap: 6px

### Tablet (640px – 1023px)
- **3-column grid, 2 rows**: `grid-template-columns: repeat(3, 1fr)`
- Otherwise same as desktop styling
- Tap to toggle (no hover)

### Desktop (≥ 1024px)
- **6-column grid, 1 row**: `grid-template-columns: repeat(6, 1fr)`
- Hover effect enabled
- Click to toggle

---

## Accessibility

- Each card should be a `<button>` element (not a `<div>` with an onClick) for keyboard navigation and screen reader support
- `aria-pressed="true/false"` to indicate toggle state
- `aria-label="[Theme name]: [value] hits per 1000 posts"` for screen readers
- Cards should be focusable and toggleable via Enter/Space keys
- Focus ring: use the default browser focus ring or a subtle outline matching the theme color

---

## Data Source

Same JSON file as the main chart: `web/data/keyword_trends.json`

No new data pipeline or export needed. The card values and sparklines are computed client-side from the same data the chart already reads.

---

## What NOT to Build

- Percentage change badges (e.g., "+12% this month") — tempting but adds visual clutter. Save for v2.
- Animated number counting on load — no animations per FRONTEND_DESIGN_SPEC
- Drill-down on card click (e.g., expanding to show keyword breakdown) — v2 feature
- Separate mobile card design — same card, just reflowed in a 2-col grid

---

## CC Prompt

```
Read docs/FRONTEND_DESIGN_SPEC.md, docs/MOBILE_SPEC.md, and docs/METRIC_CARDS_SPEC.md. Add metric cards above the main chart following the METRIC_CARDS_SPEC exactly. Remove the existing theme toggle row — the cards replace it. Each card shows the theme label, average hits/1k value, unit label, and a sparkline. Cards are sorted by value descending and act as theme toggles (click to highlight in the chart). Make them responsive: 6 columns on desktop, 3 on tablet, 2 on mobile. Do not add features from the "What NOT to Build" section.
```
