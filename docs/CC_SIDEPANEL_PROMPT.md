# Task: Refactor Theme Detail Dropdown → Slide-Out Side Panel

## Context
When a user clicks one of the theme cards (Romance, Sex/ERP, Consciousness, Therapy, Addiction, Rupture), the detail view (tracked keywords, top communities, example posts) currently expands as a dropdown panel below the cards. This pushes the time series chart and all content below it down the page, which is bad UX — the chart is the anchor content and should never be displaced.

## Goal
Replace the dropdown with a **right-edge slide-out panel** that overlays the page content. The chart and everything else stays in place.

## Requirements

### Panel behavior
- Panel slides in from the **right edge** of the viewport
- Panel sits **on top of** page content (position fixed/absolute + z-index), does NOT push content left or down
- Semi-transparent backdrop behind the panel (clicking backdrop closes panel)
- Close button (X) in the top-right corner of the panel
- Clicking a **different theme card** while the panel is open should **swap content in place** — no close-then-reopen animation, just replace the data
- Clicking the **same theme card** that's already active should **close** the panel
- Smooth slide-in/slide-out animation (200-300ms, ease-out)

### Panel dimensions & positioning
- Width: **400px** on desktop
- Height: full viewport height (or from below the top nav to the bottom)
- Anchored to the right edge of the viewport

### Active state indicator
- The currently active theme card should get a visible highlight (brighter border, glow, or similar treatment that fits the existing dark theme)
- When panel is closed, no card should appear active

### Content
- The panel contains the **exact same content** currently in the dropdown: tracked keywords (with bar charts), top communities (with percentages), and example posts
- Do NOT change the data layer, data bindings, or component logic for this content — just re-mount it inside the panel instead of the dropdown container
- Panel should have a header showing the active theme name + emoji

### Mobile / responsive
- Below **768px** viewport width, the panel should go **full-width** (essentially a modal overlay)
- On full-width, keep the same close/backdrop behavior

### Cleanup
- Remove the old dropdown expand/collapse logic entirely
- Remove any CSS that handled the dropdown push-down layout

## What NOT to change
- Theme card layout and positioning
- Time series chart
- Data fetching or keyword/community/post data logic
- Any backend code
- The visual design of the keyword bars, community list, or example posts themselves — just move them into the new container
