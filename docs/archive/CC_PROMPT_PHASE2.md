# Phase 2: Layout Reorder + Mobile Polish

## Context

Read `docs/MOBILE_RESPONSIVE_SPEC.md` for the full project spec. Phase 1 (horizontal card strip) should already be implemented. This prompt covers Phase 2.

## Task

A set of small layout and polish changes scoped to the `max-width: 768px` breakpoint. **Desktop layout must not change at all.**

## Requirements

### 1. Move methodology note below the chart

The text that reads "Each theme tracks validated keywords. Mention rates reflect how distinctive each theme's vocabulary is, not necessarily how prevalent the topic is overall." currently sits between the card strip and the chart. On mobile, it's a speed bump between the selector and the visualization.

- On mobile (≤768px), this text should appear **below** the chart instead of above it
- Use CSS `order` on a flex container or CSS Grid reordering — avoid duplicating the DOM element
- If the layout isn't already using flex/grid in a way that supports `order`, refactor the parent container to enable it (mobile only)

### 2. Tighten heading font sizes

- The main heading ("How are people talking about AI companionship?") should be ~1.5rem on mobile (it's currently rendering quite large — probably 2rem+)
- The callout line ("Consciousness is up 68%...") can stay as-is or reduce slightly
- Don't change desktop font sizes

### 3. Audit touch targets

- All tappable elements must be at least 44px in height on mobile. Check:
  - Time range buttons (6M, 1Y, 2Y, ALL)
  - Absolute/Relative toggle
  - Theme cards (these are probably fine after Phase 1)
  - Any links in the nav
- If any are under 44px, increase padding to meet the minimum

### 4. Audit spacing and padding

- Consistent 16px left/right padding on all content sections
- No element should touch the screen edges
- Check that nothing causes unwanted horizontal scrolling on the page body (the card strip scrolls horizontally — the page itself should not)
  - A quick test: add `overflow-x: hidden` on the body/html at mobile widths if not already present, but first check if anything is actually overflowing

### 5. Font size floor

- No text on the page should be smaller than 14px on mobile
- Check axis labels, methodology note, card labels, footer text if any

## How to verify

1. Desktop should be identical to before
2. On mobile: chart should appear directly after the card strip, with the methodology note below the chart
3. All buttons/tappable areas should feel comfortable to tap (no tiny targets)
4. No horizontal page scroll — only the card strip scrolls horizontally
5. Text is readable everywhere — nothing tiny
