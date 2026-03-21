# Mobile Responsive Spec — myfriendisai.com

## Problem Statement

The dashboard is designed for desktop and currently has two critical UX problems on mobile:

1. **Chart buried below the fold.** The 2x3 theme card grid consumes ~50% of the mobile viewport, pushing the main time-series chart — the primary visualization — far below the fold. Most mobile users will never scroll to it.
2. **Detail panel takes over the screen.** On desktop, the theme detail panel (keywords, communities, example posts) opens as a right sidebar alongside the chart. On mobile, it fills the entire viewport with no visible connection to the chart it's describing.

## Approach

Single codebase, responsive CSS. One breakpoint at **768px** (standard tablet/phone threshold). No separate mobile site. Desktop layout is unchanged — all changes are scoped to `@media (max-width: 768px)`.

## Current Desktop Layout (Reference — Do Not Change)

```
┌─────────────────────────────────────────────────────┬──────────────┐
│ My Friend Is AI                     About  GitHub ↗ │              │
│                                                     │              │
│ How are people talking about AI companionship?      │  [Theme      │
│ Consciousness is up 68% vs same period last year.   │   Detail     │
│                                                     │   Panel]     │
│ 6M  [1Y]  2Y  ALL            [Absolute]  Relative  │              │
│                                                     │  Keywords    │
│ ┌────────┬────────┬────────┬────────┬────┬────────┐ │  Communities │
│ │Romance │Sex/ERP │Consc.  │Therapy │Add.│Rupture │ │  Example     │
│ │ 4.8    │ 5.2    │ 4.8    │ 6.0    │8.5 │ 7.4    │ │  Posts       │
│ └────────┴────────┴────────┴────────┴────┴────────┘ │              │
│                                                     │              │
│ ┌─────────────────────────────────────────────────┐ │              │
│ │                                                 │ │              │
│ │              TIME SERIES CHART                  │ │              │
│ │                                                 │ │              │
│ └─────────────────────────────────────────────────┘ │              │
└─────────────────────────────────────────────────────┴──────────────┘
```

## Target Mobile Layout

```
┌─────────────────────────────┐
│ My Friend Is AI   About  GH │
│                              │
│ How are people talking       │
│ about AI companionship?      │
│ Consciousness is up 68%...   │
│                              │
│ 6M [1Y] 2Y ALL              │
│         [Absolute] Relative  │
│                              │
│ ◄ [Rom] [Sex] [Con] [The] ► │  ← horizontal scroll strip
│                              │
│ ┌──────────────────────────┐ │
│ │                          │ │
│ │    TIME SERIES CHART     │ │  ← now visible without scrolling
│ │                          │ │
│ └──────────────────────────┘ │
│                              │
│ methodology note text        │
│                              │
│ ┌──────────────────────────┐ │
│ │ ── drag handle ──        │ │  ← bottom sheet (on theme tap)
│ │ 🧠 Consciousness         │ │
│ │ Keywords, Communities,   │ │
│ │ Example Posts             │ │
│ └──────────────────────────┘ │
└──────────────────────────────┘
```

---

## Component Specs

### 1. Header / Nav

**Current (desktop):** "My Friend Is AI" left, "About" and "GitHub ↗" right.

**Mobile change:** Reduce font size slightly. Keep same layout — it already works. GitHub link can abbreviate to just the icon if space is tight, but probably fine as-is.

**Effort:** Minimal — likely needs no changes at all.

### 2. Headline + Callout

**Current:** Large heading + colored callout ("Consciousness is up 68%...").

**Mobile change:** Reduce heading font size (maybe ~1.5rem instead of ~2.5rem). Callout text stays. This section already works okay on mobile based on the screenshot.

**Effort:** Minimal — one or two font-size overrides.

### 3. Time Range & Mode Toggles

**Current:** "6M 1Y 2Y ALL" left-aligned, "Absolute / Relative" right-aligned, same row.

**Mobile change:** Stack them if they don't fit on one line, or keep on one line with reduced padding. Looking at the mobile screenshot, they currently render fine as two rows. That's acceptable. Could be tightened to one row if we reduce padding.

**Effort:** Minimal.

### 4. Theme Cards → Horizontal Scroll Strip

**This is the highest-impact change.**

**Current (desktop):** 6 cards in a single horizontal row (or wrapping 2x3 on narrower desktop). Each card shows: emoji + theme name, rate number, "mentions / 1k posts" label, sparkline.

**Mobile change:** Single horizontal scrolling row. Cards become compact but keep all four elements (emoji, name, rate, sparkline). The sparkline is useful at this level — it lets users see trend shape before tapping.

**Behavior:**
- `overflow-x: auto` with `-webkit-overflow-scrolling: touch`
- `scroll-snap-type: x mandatory` with `scroll-snap-align: start` on each card
- Cards have a fixed width (~140px) so 2–2.5 are visible at once, signaling scrollability
- No scrollbar visible (hide with CSS)
- Active/selected card gets the highlighted border (same as current desktop selection state)
- Tapping a card still opens the detail panel (now a bottom sheet, see below)
- Drop the "mentions / 1k posts" label on mobile to save vertical space — the rate number and sparkline are enough. The label is established by context.

**Visual spec:**
```
┌─────────────────────────────────────┐
│  ┌─────────┐ ┌─────────┐ ┌────     │
│  │💕Romance│ │🔞Sex/ERP│ │🧠Co     │  ← partially visible = scroll hint
│  │  4.8    │ │  5.2    │ │  4.     │
│  │ ∿∿∿∿∿∿ │ │ ∿∿∿∿∿∿ │ │ ∿∿     │
│  └─────────┘ └─────────┘ └────     │
└─────────────────────────────────────┘
```

**Effort:** Medium. Requires restructuring the card container CSS and possibly some JS for scroll-snap behavior. The card component itself stays the same — just restyled.

### 5. Methodology Note

**Current:** Centered text below cards: "Each theme tracks validated keywords..."

**Mobile change:** Move this below the chart instead of between cards and chart. On mobile, it's a speed bump between the card selector and the visualization. On desktop, it's fine where it is because the chart is immediately below it.

**Effort:** Low — conditionally reorder in the DOM or use CSS `order` property.

### 6. Time Series Chart

**Current:** Full-width chart with event annotations (vertical dashed lines with rotated labels like "Sycophancy update", "4o 1st sunset", "4o retired").

**Mobile changes:**
- Chart should be full-width with maybe 8px horizontal padding
- Chart height: at least 250px (don't let it get squished — this is the main content)
- **Event annotations:** Rotate labels to be more compact, or abbreviate them. At mobile widths, the rotated text labels may overlap. Consider shortening to abbreviated labels ("Syco. update", "4o sunset", "4o ret.") or reducing font size. If the chart library supports tooltip-on-tap for annotations, that's the ideal solution — show a dot on the timeline, tap for label.
- Y-axis labels: keep but reduce font size
- X-axis labels: the chart library probably handles this, but verify that month labels don't overlap at ~350px chart width. May need to show fewer labels (every other month).
- Touch interaction: make sure any hover tooltips work on tap

**Effort:** Medium. Depends on what chart library is in use. Annotation handling is the trickiest part.

### 7. Theme Detail Panel → Bottom Sheet

**This is the most complex change but critical for UX.**

**Current (desktop):** Right sidebar, ~300px wide, scrollable, shows: theme header (emoji + name + description), tracked keywords with counts and bar charts, top communities with percentages, example posts with links.

**Mobile change:** Bottom sheet that slides up from the bottom of the viewport.

**Bottom sheet behavior:**
- **Closed state:** Not visible (no persistent tab — it only appears when a theme card is tapped)
- **Open state (default):** Slides up to cover ~60% of viewport height. Chart remains partially visible above. A small drag handle bar at the top signals draggability.
- **Expanded state:** User can drag up to ~90% of viewport. Scrollable content within.
- **Dismiss:** Drag down past a threshold, or tap the X button, or tap the visible chart area above the sheet.
- **Backdrop:** Semi-transparent dark overlay on the area above the sheet (optional — helps focus attention but might feel heavy. Start without it and add if needed.)

**Content inside the sheet:** Same as current panel content, just full-width instead of sidebar-width. The keyword bars and community bars will actually look better with more horizontal space.

**Implementation approach:**
- CSS `transform: translateY()` for the slide animation
- Touch event handlers for drag-to-dismiss / drag-to-expand
- `position: fixed; bottom: 0; left: 0; right: 0;` 
- `border-radius: 16px 16px 0 0` for the rounded top corners
- Internal content scrolls with `overflow-y: auto` when sheet is at max height
- Consider using a lightweight library if building the gesture handling from scratch is too complex — but it's doable in vanilla JS with touchstart/touchmove/touchend

**Visual spec:**
```
┌──────────────────────────────┐
│                              │  ← chart still partially visible
│    ┌────────────────────┐    │
│    │                    │    │
├────┤  ── drag handle ── ├────┤  ← rounded top corners
│    │                    │    │
│ 🧠 Consciousness              │
│ Language of sentience...       │
│                                │
│ TRACKED KEYWORDS               │
│ sentient          ████████ 1048│
│ self-aware        ███      320 │
│ ...                            │
│                                │
│ TOP COMMUNITIES                │
│ r/CharacterAI     ████   37.2% │
│ ...                            │
│                                │
│ EXAMPLE POSTS                  │
│ "I Gotta Say..."               │
│ r/CharacterAI · Mar 2026       │
└────────────────────────────────┘
```

**Effort:** High. This is the biggest piece of work. Probably 1–2 sessions with CC.

### 8. General Mobile Polish

These are small things that add up:

- **Touch targets:** Make sure all tappable elements (cards, toggle buttons, time range selectors) are at least 44px tall — Apple's minimum recommendation.
- **Font sizes:** Audit all text to make sure nothing is smaller than 14px on mobile.
- **Horizontal padding:** Consistent 16px padding on left/right edges throughout.
- **No horizontal scroll on the page itself:** Only the card strip should scroll horizontally. Make sure nothing else causes an unwanted horizontal scrollbar.

**Effort:** Low — cleanup pass after the main changes.

---

## Implementation Phases

### Phase 1: Horizontal Card Strip (DO FIRST)
**Why first:** Biggest impact for least effort. Gets the chart above the fold immediately.
- Convert 2x3 card grid to horizontal scroll row at ≤768px
- Add scroll-snap behavior
- Drop "mentions / 1k posts" label on mobile
- Ensure selected card state works

### Phase 2: Layout Reorder
- Move methodology note below the chart on mobile (CSS `order` or conditional render)
- Tighten heading font sizes
- Audit padding and touch targets

### Phase 3: Chart Mobile Optimization
- Verify chart renders well at mobile widths
- Handle annotation label overlap (abbreviate or convert to tap-to-reveal)
- Confirm touch tooltips work
- Ensure axis labels don't overlap

### Phase 4: Bottom Sheet Detail Panel
**Why last:** Most complex, and the current full-screen behavior is functional (just not ideal). The other phases improve the core experience; this polishes the exploration flow.
- Build bottom sheet component with slide-up animation
- Implement drag-to-dismiss gesture handling
- Wire up to theme card tap events (replacing current full-screen panel on mobile)
- Test scroll behavior inside sheet
- Add dismiss on backdrop tap / X button

---

## Breakpoint Summary

| Breakpoint | Layout |
|---|---|
| > 768px | Current desktop layout, no changes |
| ≤ 768px | Horizontal card strip, chart promoted, bottom sheet detail panel |

Only one breakpoint needed. We're not trying to handle tablets as a separate case — 768px cleanly separates "phone" from "everything else," and the desktop layout works fine on tablets.

## Technical Notes

- All changes are CSS-only except: bottom sheet gesture handling (JS), and possibly chart annotation abbreviation (depends on chart library API).
- No new dependencies should be needed. Bottom sheet can be built with vanilla JS + CSS transitions.
- Test on iPhone Safari and Chrome Android at minimum. Safari has quirks with `position: fixed` and `100vh` (the URL bar issue) — use `100dvh` instead of `100vh` for the bottom sheet height calculations.
- The `scroll-snap` CSS is well-supported now but test that it feels right — sometimes the deceleration curve feels off on different browsers.
