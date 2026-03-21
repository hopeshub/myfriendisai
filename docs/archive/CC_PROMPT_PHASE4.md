# Phase 4: Bottom Sheet Detail Panel

## Context

Read `docs/MOBILE_RESPONSIVE_SPEC.md` for the full project spec. Phases 1–3 should already be implemented. This prompt covers Phase 4 — the most complex change.

Currently, tapping a theme card on mobile opens the detail panel (keywords, communities, example posts) as a full-screen overlay that completely hides the chart. The goal is to replace this with a bottom sheet that slides up from the bottom, keeping the chart partially visible above.

## Task

On mobile (≤768px), replace the current full-screen detail panel with a bottom sheet component. **Desktop sidebar behavior must not change at all.**

## Bottom Sheet Behavior

### States

1. **Closed:** Not visible. No persistent tab or handle — the sheet only appears when a theme card is tapped.

2. **Open (default):** Sheet slides up from the bottom to cover ~60% of viewport height. The chart and top of the page remain visible above. A small drag handle bar at the top of the sheet signals that it can be dragged.

3. **Expanded:** User drags the sheet upward. It can expand to ~90% of viewport height. Content inside the sheet becomes scrollable.

### Opening
- Triggered by tapping a theme card
- Animate in with a CSS transition: `transform: translateY(0)` from `transform: translateY(100%)`, duration ~300ms, ease-out curve
- If a different theme card is tapped while the sheet is already open, update the sheet content in place (don't close and reopen)

### Closing (any of these should work)
- Drag the sheet downward past a threshold (~30% of sheet height)
- Tap the X button in the sheet header
- Tap the dimmed area above the sheet (the backdrop)

### Backdrop
- When the sheet is open, add a semi-transparent dark overlay (`rgba(0,0,0,0.4)`) over the area above the sheet
- Tapping the backdrop closes the sheet
- The backdrop should also animate in/out with the sheet

## Drag Gesture Implementation

Use touch events (touchstart, touchmove, touchend) on the drag handle area:

```
touchstart → record starting Y position
touchmove  → calculate delta, apply transform: translateY(delta) in real-time
               (only allow downward drag when at default height,
                or upward drag to expand)
touchend   → if dragged down > 30% of sheet height → close (animate out)
             if dragged up > threshold → expand to 90%
             otherwise → snap back to default 60% position
```

- During drag, disable the sheet's internal scroll to prevent scroll/drag conflicts
- Only the drag handle area (top ~40px of the sheet) should initiate a drag gesture
- Content below the handle scrolls normally with `overflow-y: auto`

## Sheet Layout

```
┌────────────────────────────────────┐
│          ── handle bar ──          │  ← 40px tall, centered 32x4px rounded bar
│                                  ✕ │  ← X button, top-right
│  🧠 Consciousness                  │  ← emoji + theme name
│  Language of sentience...          │  ← description
│  ──────────────────────────────    │  ← divider
│                                    │
│  TRACKED KEYWORDS                  │  ← same content as current panel
│  sentient          ████████  1,048 │
│  self-aware        ███       320   │
│  personhood        ██        106   │
│  ...                               │
│                                    │
│  TOP COMMUNITIES                   │
│  r/CharacterAI     ████     37.2%  │
│  ...                               │
│                                    │
│  EXAMPLE POSTS                     │
│  "I Gotta Say, Didn't See..."     │
│  r/CharacterAI · Mar 2026         │
│  ...                               │
└────────────────────────────────────┘
```

## CSS Specs

```css
/* Sheet container */
position: fixed;
bottom: 0;
left: 0;
right: 0;
height: 60dvh;                    /* default open height — use dvh not vh for Safari */
max-height: 90dvh;                /* expanded height */
background: (match current panel background color);
border-radius: 16px 16px 0 0;
transform: translateY(100%);      /* hidden by default */
transition: transform 300ms ease-out, height 200ms ease-out;
z-index: 1000;
overflow: hidden;                 /* internal content handles its own scroll */

/* When open */
transform: translateY(0);

/* Drag handle */
width: 32px;
height: 4px;
background: rgba(255,255,255,0.3);
border-radius: 2px;
margin: 12px auto;

/* Internal scroll area (everything below the handle) */
overflow-y: auto;
-webkit-overflow-scrolling: touch;
padding: 0 16px 16px;
height: calc(100% - 40px);        /* minus the handle area */

/* Backdrop overlay */
position: fixed;
inset: 0;
background: rgba(0,0,0,0.4);
z-index: 999;
opacity: 0;
transition: opacity 300ms ease-out;
pointer-events: none;

/* Backdrop visible */
opacity: 1;
pointer-events: auto;
```

## Integration with Existing Code

- Find where the current detail panel is rendered and how it's triggered (likely a state variable set on card click)
- On mobile (≤768px): instead of rendering the sidebar/full-screen panel, render the bottom sheet
- On desktop (>768px): keep the existing sidebar behavior exactly as-is
- The simplest approach: detect viewport width in JS and conditionally apply the bottom sheet behavior. Or use CSS to hide the sidebar version and show the sheet version at the mobile breakpoint — but the gesture handling requires JS either way.
- A clean approach: create a new `BottomSheet` wrapper component that receives the same content as the current panel. On mobile, the panel content renders inside the BottomSheet. On desktop, it renders in the sidebar as before.

## Important Edge Cases

- **Safari `100vh` bug:** Use `dvh` units, not `vh`. On Safari mobile, `100vh` includes the area behind the URL bar, causing the sheet to extend off-screen.
- **Scroll vs drag conflict:** When the sheet content is scrolled to the top and the user drags down, it should close the sheet (not just scroll). When scrolled partway down, downward swipes should scroll normally. This is the classic "pull to dismiss" pattern. The simplest way: only allow drag-to-dismiss from the handle area, not from the content area.
- **Keyboard avoidance:** If any future interactive elements are added inside the sheet, the sheet should respect the virtual keyboard. Not a concern right now since the content is read-only, but worth noting.
- **Rapid tapping:** If a user taps cards quickly, don't queue up multiple animations. The sheet should update content immediately if already open.

## How to verify

1. Desktop: sidebar detail panel works identically to before
2. Mobile: tap a theme card → sheet slides up from bottom, covering ~60% of screen
3. Chart is partially visible above the sheet
4. Drag the handle down → sheet dismisses with animation
5. Tap backdrop → sheet dismisses
6. Tap X → sheet dismisses
7. Drag handle up → sheet expands to ~90%
8. Scroll within the sheet content (keywords, communities, posts)
9. Tap a different card while sheet is open → content updates without close/reopen flicker
10. Rotate device / resize → sheet adapts (doesn't break)
