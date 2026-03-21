# Phase 1: Convert Theme Cards to Horizontal Scroll Strip on Mobile

## Context

Read `docs/MOBILE_RESPONSIVE_SPEC.md` for the full project spec. This prompt covers Phase 1 only.

The site is a single-page dashboard at myfriendisai.com. On desktop, the 6 theme cards display in a horizontal row (or 2x3 grid at narrower desktop widths). On mobile, this grid pushes the main time-series chart far below the fold — the chart is the most important element and most mobile users never see it.

## Task

Add a CSS breakpoint at `max-width: 768px` that converts the theme card grid into a horizontally scrolling strip. **Desktop layout must not change at all.**

## Requirements

### Card container (mobile only, ≤768px):
- Single horizontal row, no wrapping
- `overflow-x: auto` with `-webkit-overflow-scrolling: touch`
- `scroll-snap-type: x mandatory`
- Hide the scrollbar visually (use the `::-webkit-scrollbar { display: none }` and `scrollbar-width: none` pattern)
- Add ~16px horizontal padding on the container so cards don't touch screen edges

### Individual cards (mobile only, ≤768px):
- Fixed width of ~140px (so 2–2.5 cards are visible at once — the partial visibility signals scrollability)
- `scroll-snap-align: start`
- `flex-shrink: 0` so they don't compress
- **Remove** the "mentions / 1k posts" text label to save vertical space — keep the emoji, theme name, rate number, and sparkline
- The selected/active card border state should still work as-is

### What NOT to change:
- Desktop layout (anything above 768px)
- Card component internals (colors, sparklines, click handlers)
- Any other part of the page

## How to verify

1. Open the site at desktop width — should look identical to current
2. Resize to <768px (or use Chrome DevTools mobile emulation) — cards should be in a horizontal scrollable row
3. Swipe/scroll horizontally through all 6 cards — scroll snapping should feel natural
4. The time-series chart should now be visible without scrolling (or with minimal scrolling)
5. Tapping a card should still open the detail panel as before
