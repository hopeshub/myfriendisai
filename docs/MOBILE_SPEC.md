# myfriendisai — Mobile Responsiveness Spec

**Created:** March 15, 2026  
**Purpose:** Make the myfriendisai trends explorer fully usable on phones and tablets. Single codebase, responsive layout — no separate mobile site.  
**Prerequisite docs:** `docs/FRONTEND_DESIGN_SPEC.md`, `docs/KEYWORD_CATEGORIES_V1.md`

---

## Decision: Responsive, Not Bifurcated

Same codebase, same URL, same deployment. Use CSS breakpoints and layout adjustments to adapt the experience by screen size. Rationale:

- The site is a single page with one chart — the complexity doesn't justify a separate mobile build
- Next.js + Tailwind already support responsive design natively
- Data source is identical across devices (static JSON)
- A bifurcated approach doubles maintenance burden for a solo developer

---

## Breakpoints

Three tiers. Design mobile-first, then scale up.

| Tier | Width | Label | Target devices |
|------|-------|-------|----------------|
| Mobile | < 640px | `sm` | Phones (portrait) |
| Tablet | 640px – 1023px | `md` | Tablets, phones (landscape) |
| Desktop | ≥ 1024px | `lg` | Laptops, desktops |

Use Tailwind's default breakpoint system (`sm:`, `md:`, `lg:`). Do not add custom breakpoints.

---

## Layout Changes by Tier

### Mobile (< 640px)

**Header:**
- Site title "My Friend Is AI" — 20px, left-aligned
- Nav links (About, GitHub) — collapse into a compact row or small icon links below the title. No hamburger menu (only two links, not worth hiding them).

**Headline + Summary:**
- Headline: 22px bold, wrapping to 2 lines is fine
- Dynamic summary: 14px, muted gray, max 2 lines

**Theme Toggles:**
- Switch from horizontal row to a **2×3 grid** (2 columns, 3 rows)
- Each toggle is a pill-shaped button: emoji + label
- Toggle size: minimum 44px tap target height (WCAG touch target guideline)
- Active/selected state: full-opacity theme color background with white text
- Inactive state: transparent background, muted text, subtle border
- Spacing: 8px gap between toggles

**Time Range Selector:**
- Keep as horizontal row (4 buttons: 6M / 1Y / ALL fits easily)
- Minimum 44px height per button
- Full width of container, evenly distributed
- Sits directly above the chart

**Chart Area:**
- Full viewport width (edge to edge, no side padding on the chart itself)
- Fixed height: 280px (enough to show trends without dominating the screen)
- Y-axis labels: move inside the chart area (overlaid, top-left) to save horizontal space
- X-axis labels: show only 4 labels max (e.g., `Jan '24`, `Jul '24`, `Jan '25`, `Jul '25`) to prevent overlap
- Line stroke width: 2px (slightly thicker than desktop for visibility on small screens)

**Event Annotations:**
- Hide rotated text labels entirely on mobile — they overlap and become unreadable
- Replace with: subtle vertical dashed lines only (no text)
- Add a small "ℹ️ Events" toggle button below the chart that expands a simple list view of events with dates when tapped
- Event list format: `Feb 2023 — Replika removes ERP`, one per line, chronological, scrollable if needed

**Touch Interactions:**
- Tap a theme toggle to highlight/unhighlight that theme (same as click on desktop)
- Tap on chart area shows a **tooltip/crosshair** pinned to the nearest data point with date + value
- Swipe left/right on chart to pan (only when zoomed into 6M or 1Y view)
- No hover states — all interactions are tap-based
- Tooltip should appear above the finger position (not behind it)

**Footer:**
- Stack vertically: data source line, methodology link, last updated timestamp
- 12px text, muted gray

---

### Tablet (640px – 1023px)

**Header:** Same as desktop layout — enough room for title + nav in one row.

**Headline + Summary:** Same as desktop — 28px title, 16px summary.

**Theme Toggles:**
- Horizontal row, but allow wrapping to two rows if needed
- Same pill style as mobile but slightly larger
- Minimum 44px tap target height maintained

**Time Range Selector:** Horizontal row, centered, same as desktop.

**Chart Area:**
- Full container width with 16px side padding
- Height: 360px
- Y-axis labels: external (standard position), keep axis line
- X-axis: show 6 labels (every ~6 months)

**Event Annotations:**
- Show vertical dashed lines WITH text labels
- Labels rotated 45° (not 90° — easier to read on medium screens)
- If two events are within 30 days of each other, stack labels vertically or show only the more significant one
- Keep collision detection: labels must not overlap

**Touch Interactions:**
- Same tap behavior as mobile
- Tooltip on tap, dismiss on tap elsewhere

**Footer:** Single row, same as desktop.

---

### Desktop (≥ 1024px)

This is the current design. No changes to the existing `FRONTEND_DESIGN_SPEC.md` layout except:

- Ensure hover tooltip works cleanly (show date + value on hover)
- Event annotation labels at 90° rotation as currently designed
- Mouse cursor changes to crosshair over chart area

---

## Component-Level Specs

### Theme Toggle Component

The toggle should be a single reusable component that adapts its layout to the screen size.

```
Props:
  - themes: array of { id, label, emoji, color }
  - activeThemes: array of theme IDs currently selected
  - onToggle: callback(themeId)

Mobile layout:  grid grid-cols-2 gap-2
Tablet layout:  flex flex-wrap gap-3
Desktop layout: flex flex-row gap-4
```

**Visual states:**
- Inactive: `bg-transparent border border-[theme-color]/30 text-[muted]`
- Active: `bg-[theme-color]/20 border border-[theme-color] text-[theme-color]`
- Each toggle always shows the emoji regardless of state

**Sizing:**
- Mobile: `h-11 text-sm px-3` (44px height for touch targets)
- Tablet: `h-11 text-sm px-4`
- Desktop: `h-9 text-sm px-4` (hover states, smaller targets OK)

---

### Event Annotations Component

Must handle three display modes:

| Mode | When | Behavior |
|------|------|----------|
| Hidden labels | Mobile (< 640px) | Dashed lines only, expandable list below chart |
| Compact labels | Tablet (640–1023px) | Lines + 45° labels, collision-detected |
| Full labels | Desktop (≥ 1024px) | Lines + 90° labels, full text |

The event list (mobile fallback) is a separate component:

```
<EventList>
  - Collapsed by default (just a small "View events" link)
  - Expands to show: date + event name, one per row
  - Scrollable if more than 5 events
  - Styled as a subtle card below the chart
  - Close button to collapse
</EventList>
```

---

### Chart Component

The chart library (Recharts or whatever is currently in use) needs these responsive configurations:

**Margins:**
- Mobile: `{ top: 10, right: 8, bottom: 30, left: 8 }`
- Tablet: `{ top: 10, right: 20, bottom: 30, left: 40 }`
- Desktop: `{ top: 10, right: 30, bottom: 30, left: 50 }`

**Tick counts:**
- X-axis mobile: 4 ticks
- X-axis tablet: 6 ticks
- X-axis desktop: 7–8 ticks (current behavior)

**Stroke widths:**
- Mobile: 2.5px active, 1.5px inactive
- Desktop: 2px active, 1px inactive

**Tooltip behavior:**
- Mobile/tablet: show on tap, dismiss on tap-away or second tap
- Desktop: show on hover, follow cursor

Use a `useBreakpoint()` hook (or Tailwind's responsive utilities) to pass the right config to the chart. Do NOT render three separate charts — render one chart component that accepts responsive props.

---

## Viewport & Meta Tags

Ensure the HTML head includes:

```html
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=5" />
```

Do NOT set `user-scalable=no` — people with low vision need to pinch-zoom. Do NOT set `maximum-scale=1` for the same reason.

---

## Performance Considerations

Mobile devices are slower and on worse networks. Handle this:

1. **JSON data size:** `keyword_trends.json` is the main payload. If it's over 500KB, consider splitting by time range (load "1Y" data first, lazy-load "ALL" only when that tab is selected). If it's under 500KB, don't bother — ship it all at once.

2. **Chart rendering:** Recharts is already lightweight. No additional optimization needed unless the chart has > 5,000 data points visible at once, in which case downsample to every-other-day for mobile.

3. **Font loading:** Use `font-display: swap` to prevent invisible text during load. Consider using system fonts on mobile to eliminate the font download entirely (this is a pragmatic trade, not a design compromise — the chart is the star, not the typography).

4. **No lazy loading needed:** It's a single-page site with one chart. Everything is above the fold.

---

## Testing Checklist

Before shipping, test on these (use Chrome DevTools device emulation at minimum, real devices if possible):

- [ ] iPhone SE (375px) — smallest common phone
- [ ] iPhone 14/15 (390px) — most common iPhone
- [ ] iPhone 14 Pro Max (430px) — largest common phone
- [ ] iPad (768px portrait, 1024px landscape)
- [ ] Android mid-range (360px) — Samsung Galaxy A series
- [ ] Landscape phone (667px × 375px) — verify chart doesn't break

For each device, verify:
- [ ] All 6 theme toggles visible and tappable without scrolling
- [ ] Chart renders fully without horizontal scroll
- [ ] X-axis labels don't overlap
- [ ] Tapping a data point shows tooltip above finger
- [ ] Event annotation lines are visible
- [ ] Event list expands/collapses on mobile
- [ ] Time range buttons are all reachable with one thumb
- [ ] Text is readable without pinch-zooming
- [ ] No horizontal overflow on any element (check for accidental scroll)

---

## What NOT to Build

Stay disciplined. These are tempting but out of scope:

- Pull-to-refresh (static data, no real-time updates)
- App-like navigation or bottom tab bar
- PWA / "Add to Home Screen" prompt
- Landscape-specific layout (let it reflow naturally)
- Gesture controls beyond tap and basic scroll
- Separate mobile-optimized data endpoint
- Native app wrapper (Capacitor, React Native, etc.)
- Offline support / service worker caching

---

## Implementation Order

Do this in sequence:

1. **Add the viewport meta tag** if not already present (5 min)
2. **Make theme toggles responsive** — implement the 2×3 grid for mobile (30 min)
3. **Make the chart responsive** — responsive margins, tick counts, stroke widths, height (1 hr)
4. **Build mobile tooltip** — tap-to-show instead of hover (45 min)
5. **Build event annotation modes** — hide labels on mobile, add expandable event list (1 hr)
6. **Responsive header/headline/footer** — straightforward Tailwind responsive utilities (30 min)
7. **Test across breakpoints** — use the checklist above (30 min)
8. **Fix edge cases** — whatever broke during testing (variable)

**Total estimate:** 4–5 hours of CC time, maybe across 2 sessions.

---

## CC Prompt

```
Read docs/FRONTEND_DESIGN_SPEC.md and docs/MOBILE_SPEC.md. Make the site fully responsive for mobile devices. Follow the MOBILE_SPEC exactly — it defines three breakpoints (mobile < 640px, tablet 640-1023px, desktop ≥ 1024px) with specific layout changes for each. Start with the theme toggles and chart component. Do not add any features from the "What NOT to Build" section.
```
