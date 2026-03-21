# Chart UX Fix Pass (v2)
#
# Major change: switch from raw post counts to Google Trends-style
# relative index. Several visual fixes included. Do all in one pass.

## 1. Switch to indexed values with monthly aggregation

**This is the biggest change.** Replace raw post counts with a
relative index, the same way Google Trends works.

### How to calculate:

For each theme:
1. Aggregate keyword hits into calendar months (not weeks, not days)
2. Find the PEAK month (highest raw count) for that theme
3. Set the peak month = 100
4. Scale all other months relative to that peak

Formula: `index = (month_count / peak_month_count) * 100`

Example: If Rupture's peak month had 65 posts and the current month
has 20 posts, the current index value is (20/65)*100 = 30.8

### Why:
- Thin themes (Rupture at 0.5 posts/day) look credible instead of
  embarrassingly small
- All themes are on the same 0-100 scale, so relative growth is
  comparable across themes
- Monthly smooths out daily/weekly noise while preserving trend shapes
- This is how Google Trends works — there's a reason they do it

### Y-axis:
- Label: "Interest over time" (or just no label — Google Trends
  doesn't label their y-axis)
- Scale: 0 to 100, fixed, same for every theme
- Grid lines at 25, 50, 75, 100

### Tooltip on hover:
Show: "Month, Theme name: [index value]"
Do NOT show the raw post count in the tooltip. The index IS the
metric. If Walker wants to add raw counts later, that's a v2 decision.

### Data pipeline:
You can either:
(a) Compute the index in the export script and add it to the JSON, or
(b) Keep the JSON as raw daily counts and compute the index in the
    frontend by aggregating to months and dividing by max.

Option (b) is more flexible — do that.

## 2. Default state: show ALL themes together

When the page first loads (no theme selected), show ALL 6 theme
lines on the chart simultaneously. Since every theme is now on the
same 0-100 scale, this is visually honest — you can directly compare
relative growth across themes.

Use distinct colors per theme. Make all lines the same weight.
Highlight on hover — when you mouse over a line, it thickens and
shows the tooltip.

## 3. Selected state: highlight one theme

When a user clicks a theme toggle:
- That theme's line becomes bold/prominent
- Other theme lines become faint (20-30% opacity) but STAY VISIBLE
- This is the opposite of the previous instruction (which said to
  hide ghost lines). With indexed data on a shared scale, ghost
  lines ARE honest and useful for comparison.

When clicking the same theme again, deselect it and return to the
default "all visible" state.

## 4. Fix event annotation overflow

Event labels on the right edge are getting cut off. Fix:
- If a label would overflow the right edge of the chart, anchor it
  to the LEFT of the dotted line instead of the right
- Truncate labels to max 30 characters with ellipsis if needed
- Add a tooltip on hover showing the full event name
- If two event labels would overlap vertically, stagger them —
  offset the second one down by ~20px

## 5. Update the subtitle logic

- Default (no theme selected): "Tracking AI companion discourse
  across [N] subreddits, [start month] to [end month]."
- Theme selected with YoY data: "[Theme] is up/down X% vs same
  period last year"
- Theme selected, no YoY: "[Theme] peaked in [peak month/year]"

Do NOT mention raw post counts or "per 1k" in the subtitle.

## 6. Rename "Conscious" to "Consciousness"

The toggle button says "Conscious" — should say "Consciousness."

## 7. Time range selector behavior

With monthly data, the time range options should be:
- **6M** — last 6 months
- **1Y** — last 12 months
- **ALL** — full dataset (Jan 2023 to present)

Remove the 30D and 90D options — they don't make sense with
monthly granularity.

## 8. Push and deploy when done.
