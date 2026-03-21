# myfriendisai — Phase 3 Frontend Design Spec

**Updated:** March 11, 2026  
**Purpose:** Complete design specification for the v1 frontend rebuild. CC should read this before starting Phase 4. Every decision here is final — do not improvise or add features not described in this document.

---

## Page Structure

One page. One job. A keyword trends explorer for AI companionship discourse on Reddit.

**Top to bottom layout:**

1. **Header:** Site name ("My Friend Is AI") + nav links (About, GitHub)
2. **Headline + dynamic summary:** Title + one-sentence summary that updates based on selected theme
3. **Theme toggles:** Eight theme selectors in a horizontal row
4. **Time range selector:** 30D / 90D / 1Y / ALL
5. **Main chart:** Area/line chart with event annotations
6. **Footer:** Data source note, methodology link, last updated timestamp

---

## Color Palette

**Background and surfaces:**
- Page background: `#0F1117` (near-black)
- Chart area / card surface: `#1A1D27`
- Borders: `#2A2D3A`
- Primary text: `#F8FAFC` (off-white)
- Secondary text / labels / axes: `#94A3B8` (muted gray)

**Theme colors:**
- Intimacy: `#F97316` (orange)
- Attachment: `#3B82F6` (blue)
- Dependency: `#EF4444` (red)
- Consciousness: `#A855F7` (purple)
- Substitution: `#22C55E` (green)
- Therapy: `#EC4899` (pink)
- Memory: `#F59E0B` (amber)
- Realism: `#06B6D4` (cyan)

**Faint/unselected state:** All theme colors at 20% opacity when not highlighted

**Event annotation lines:** `#6B7280` (gray) dotted vertical lines — distinct from amber since Memory now uses amber

---

## The Eight Themes

Each toggle corresponds to keyword categories in `web/data/keyword_trends.json`.

| Toggle Label | JSON categories to merge | Color |
|---|---|---|
| Intimacy | `romantic_language` + `sexual_erotic_language` | `#F97316` |
| Attachment | `attachment_language` | `#3B82F6` |
| Dependency | `dependency_language` + `withdrawal_recovery_language` | `#EF4444` |
| Consciousness | `sentience_consciousness_language` | `#A855F7` |
| Substitution | `substitution_language` | `#22C55E` |
| Therapy | `therapy_language` | `#EC4899` |
| Memory | `memory_continuity_language` | `#F59E0B` |
| Realism | `anthropomorphism_realism_language` | `#06B6D4` |

**Merging:** For themes that combine two JSON categories, sum the daily `count_7d_avg` values for both categories for each date.

---

## Default State (on page load)

- Time range: ALL
- All eight theme lines visible as faint lines (20% opacity of their color)
- No theme highlighted — y-axis shows no scale labels
- Dynamic summary shows: "Tracking how people talk about AI companions across Reddit — from 2023 to today."
- User clicks any theme toggle to highlight it

---

## Interaction Behavior

### Theme Toggles
- Displayed as a horizontal row of pill buttons, each showing the theme name and a small color dot
- **Unselected state:** Gray text, faint color dot, line on chart is 20% opacity
- **Selected/highlighted state:** Theme color background or border, white text, line on chart is full opacity with area fill underneath
- Clicking a faint theme highlights it (full opacity, y-axis updates, dynamic summary updates)
- Clicking an already-highlighted theme dims it back to faint
- Multiple themes can be highlighted simultaneously
- Each highlighted theme shows on its own y-axis scale — shapes are comparable but raw numbers reflect each theme's actual counts

### Y-Axis Behavior
- When no theme is highlighted: no y-axis labels (just faint shapes)
- When one theme is highlighted: y-axis shows that theme's count scale
- When multiple themes are highlighted: show the most recently selected theme's scale. All highlighted lines display at full opacity on independent scales.

### Time Range Selector
- Four options: 30D, 90D, 1Y, ALL
- Styled as small pill buttons, selected = white text on dark surface, unselected = gray text
- Default: ALL

### Chart Line Style
- Use 7-day rolling average (`count_7d_avg` from the JSON), NOT raw daily counts
- Line weight: 2px for highlighted themes, 1px for faint themes
- Highlighted themes get a subtle area fill (theme color at 10% opacity) below the line
- Smooth interpolation

---

## Event Annotations

Vertical dotted lines at key dates with small labels above the chart area.

**Labels must NOT overlap.** If multiple events are close together, stagger vertically or collapse into a grouped marker with hover expansion.

**Events to include:**

| Date | Label |
|---|---|
| 2023-02-01 | Replika removes ERP |
| 2024-05-13 | GPT-4o launches |
| 2025-04-01 | GPT-4o sycophancy update |
| 2025-08-07 | GPT-4o first retirement |
| 2026-01-29 | 4o retirement announced |
| 2026-02-13 | GPT-4o permanently retired |

**Style:** Dotted vertical line in `#6B7280`, 1px, with small label text in `#94A3B8` above the chart.

---

## Dynamic Summary

A single sentence below the headline that updates based on highlighted theme.

**When no theme is highlighted:**
> "Tracking how people talk about AI companions across Reddit — from 2023 to today."

**When a theme is highlighted:**
> "[Theme name] language has [increased/decreased] [X]% since [start of data range]."

Calculate percentage change by comparing 7-day average from first 30 days to most recent 30 days. Use the theme's color for the theme name text.

---

## X-Axis Labels

**Must include years.** Format: `Jan '23`, `Jul '23`, `Jan '24`, `Jul '24`, `Jan '25`, `Jul '25`, `Jan '26`

---

## Typography

- Site title: Inter (or system font), 28px, bold, white
- Dynamic summary: 16px, regular, muted gray
- Theme toggle labels: 14px, semibold
- Chart axis labels: 12px, regular, muted gray (tabular figures)
- Event annotation labels: 11px, regular, muted gray

---

## Responsive Behavior

Desktop-primary.

- ≥1024px: Full layout as described
- 768–1023px: Theme toggles wrap to two rows, chart full width
- <768px: Toggles stack vertically, chart scrolls horizontally. Functional but not optimized.

---

## What NOT to Build

- Community drill-down pages
- Subreddit-level filtering
- Data export (PNG/CSV)
- About/methodology page content (just link to placeholder)
- Search or post browsing
- Tier-based filtering
- Animation on page load
- Dark/light mode toggle (dark only)

---

## Data Source

- Chart data: `web/data/keyword_trends.json`
- Event annotations: hardcoded in frontend for v1
- Format: `{"category_name": [{"date": "YYYY-MM-DD", "count": N, "count_7d_avg": N}, ...]}`

---

## CC Prompt for Phase 4

```
Read docs/REBUILD_PLAN.md, docs/KEYWORD_CATEGORIES_V1.md, and docs/FRONTEND_DESIGN_SPEC.md. Start Phase 4: rebuild the homepage. Follow the frontend design spec exactly. Do not add features listed in "What NOT to Build."
```
