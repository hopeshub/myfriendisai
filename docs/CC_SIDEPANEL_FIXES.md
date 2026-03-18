# Task: Side Panel Fixes — Layout, Fit, and Clickable Posts

## Context
The slide-out side panel is working, but has three issues that need fixing.

---

## Fix 1: Side panel should NOT overlay the chart

**Current behavior:** The side panel slides in on top of the main content, covering the right portion of the time series chart.

**Desired behavior:** When the side panel opens, the **main content area should shrink** to make room for the panel. The panel and the chart should sit **side-by-side**, not overlapping. Think of it like a layout shift — the main content column gets narrower (by the panel width) and the panel occupies the freed-up space on the right.

- When the panel is closed, the main content takes the full width as normal.
- When the panel is open, the main content area shrinks (e.g., `calc(100% - 400px)` or use flex/grid) and the panel takes the remaining 400px on the right.
- The chart should **reflow/resize** to fit its new narrower container — not get clipped or hidden.
- Use a smooth transition on the main content width so it doesn't jump.
- The panel should NOT be `position: fixed` or `position: absolute` overlaying content. It should be part of the document flow (or use a layout approach like CSS grid or flex that achieves the same side-by-side result).

---

## Fix 2: Side panel content must fit without scrolling

**Current behavior:** The side panel content (keywords + communities + example posts) extends beyond the viewport and requires scrolling down the page.

**Desired behavior:** Everything in the side panel should be visible without any page-level scrolling. The panel itself can have **internal scroll** (overflow-y: auto) if the content is taller than the viewport, but the page should not scroll.

- The panel should be the full height of the viewport (minus any top nav).
- Use `overflow-y: auto` on the panel's content area so it scrolls internally if needed.
- The panel header (theme name + close button) should stay fixed at the top of the panel — only the content below it scrolls.

---

## Fix 3: Example posts should be clickable links to Reddit

**Current behavior:** Example posts show the post title and subreddit but are not clickable.

**Desired behavior:** Each example post should be a clickable link that opens the actual Reddit post in a new tab.

- The post data should already include a permalink or URL field from the database. Use that to construct the link.
- If the data has a `permalink` field, the full URL is `https://www.reddit.com{permalink}`
- If the data only has a post `id`, the URL pattern is `https://www.reddit.com/comments/{id}`
- Wrap the post title in an `<a>` tag with `target="_blank"` and `rel="noopener noreferrer"`
- Style the link so it looks natural in the dark theme — no bright blue underline. A subtle hover effect (underline on hover, or slight color shift) is enough.

---

## Fix 4: Click outside the panel to close it

**Desired behavior:** Clicking anywhere outside the side panel (on the main content area, the chart, the theme cards, etc.) should close the panel.

- Add a click listener on the main content area (or document level) that closes the panel when the click target is outside the panel.
- Make sure clicking **inside** the panel (scrolling, clicking a link, etc.) does NOT close it.
- Make sure clicking a **different theme card** still swaps the panel content (don't let the outside-click handler interfere with the card click handlers — card clicks should take priority).
- No backdrop/overlay needed — just the click-outside behavior.

---

## What NOT to change
- Theme card design or positioning
- Keyword bars, community list content/data logic
- The time series chart component itself (just let it respond to its container width)
- Any backend or data fetching code
