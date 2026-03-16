# Event Annotation Redesign
#
# The current approach of placing text labels on the chart is broken
# and has failed 6+ attempts to fix. The problem is structural:
# variable-length text on a chart will always overflow, overlap,
# or get cut off when events cluster in time.
#
# This redesign separates MARKERS (on chart) from LABELS (below chart).
# It is durable, handles any number of events, and works at any
# chart width or time range.

## The Design

### On the chart: numbered markers only

At each event date, draw:
- A vertical dotted line (same as current, keep these)
- A small numbered circle at the TOP of the dotted line
  - Circle: 20px diameter, semi-transparent background matching
    the chart surface color, 1px border in white/light gray
  - Number inside: 1, 2, 3, etc. — white text, 11px font
  - Numbers are assigned chronologically (1 = earliest event)

NO TEXT on the chart. No labels, no truncated strings, no rotated
text. Just the dotted line and the numbered circle.

If two events are so close that their circles would overlap (within
30px of each other horizontally), offset one slightly up and the
other slightly down (by 12px each). This only matters for events
in the same month on a monthly chart.

### Below the chart: event legend

Below the chart (between the chart and the page footer), render a
clean horizontal legend row (or rows if needed, wrapping naturally):

```
① Replika ERP removal · ② 4o launches · ③ Sycophancy fix · ④ 4o first sunset · ⑤ 4o sunset announced · ⑥ 4o retired
```

Styling:
- Same font as the rest of the page, 13px, secondary text color
- Each entry: circled number + event name + interpunct separator
- Wrap naturally if the line is too long for the viewport width
- No special layout — just a line of text that wraps like a paragraph

The circled numbers can be unicode (①②③④⑤⑥) or styled spans that
match the on-chart circles visually.

### Hover behavior (optional enhancement)

When the user hovers over a numbered circle on the chart, show a
small tooltip with:
- Event name
- Date (month + year)

Example: "③ Sycophancy fix — Aug 2025"

When the user hovers over an entry in the legend below the chart,
briefly highlight the corresponding dotted line on the chart
(make it brighter or thicker for 300ms). This is a nice-to-have,
not a requirement.

## Event List

Use these short event names. Keep them under 25 characters:

```javascript
const events = [
  { id: 1, date: '2023-02', label: 'Replika ERP removal' },
  { id: 2, date: '2024-05', label: '4o launches' },
  { id: 3, date: '2025-08', label: 'Sycophancy fix' },
  { id: 4, date: '2025-10', label: '4o first sunset' },
  { id: 5, date: '2026-01', label: '4o sunset announced' },
  { id: 6, date: '2026-02', label: '4o permanently retired' },
];
```

Dates should match the monthly x-axis positions. Adjust the exact
months if they're slightly off — check against the actual data.

## Why This Works

1. **No overflow.** Numbers are fixed-width (20px circles). They
   can't overflow the chart edge regardless of where the event is.

2. **No overlap of text.** The only thing on the chart is small
   circles. Even if two events are in adjacent months, the circles
   are small enough to coexist.

3. **Handles any number of events.** Adding a 7th or 8th event
   just means another circle and another legend entry. No layout
   recalculation needed.

4. **Works at any chart width.** Mobile, desktop, resized window —
   the circles stay at their x-position and the legend wraps
   naturally below.

5. **Future-proof.** When Walker adds new events, it's a one-line
   addition to the events array. No label positioning logic to debug.

## Implementation Notes

- Remove ALL existing label rendering code (the rotated text,
  the truncation logic, the staggering logic, the anchor-left
  logic). Delete it entirely. Start fresh with numbered circles.
- The dotted vertical lines stay — just remove the text that was
  attached to them.
- The legend below the chart should be a simple div outside the
  Recharts component, not a Recharts element. This avoids any
  SVG text rendering issues.
- Make sure the circles render ABOVE the chart lines (higher z-index)
  so they're always visible.

## Push and deploy when done.
