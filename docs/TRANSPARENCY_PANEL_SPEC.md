# Keyword Transparency Panel Spec

**Created:** March 16, 2026
**Purpose:** When a user clicks a theme card, show the actual keywords being tracked, which subreddits they're hitting in, and real post examples. This lets visitors verify the data is real without reading the methodology page.
**Prerequisite docs:** `docs/FRONTEND_DESIGN_SPEC.md`, `docs/MOBILE_SPEC.md`, `docs/METRIC_CARDS_SPEC.md`

---

## Overview

Click a theme card → a detail panel appears showing:
1. The keywords tracked for that theme (with hit counts)
2. Which subreddits generate the matches (with counts)
3. Real sample post titles for each keyword

No live database queries. Everything is pre-computed during the JSON export step and shipped as static data.

---

## Part 1: New JSON Data Export

### New file: `web/data/keyword_details.json`

The export script needs to generate a new JSON file with this structure:

```json
{
  "addiction": {
    "keywords": [
      {
        "term": "chatbot addiction",
        "hits": 74,
        "precision": 100.0,
        "sample_posts": [
          {
            "title": "Quit and deleted my entire account one month ago",
            "subreddit": "ChatbotAddiction",
            "date": "2025-11-14"
          },
          {
            "title": "I finally deleted C.AI I was addicted",
            "subreddit": "Character_AI_Recovery",
            "date": "2025-09-22"
          },
          {
            "title": "My c.ai addiction is ruining my grades",
            "subreddit": "CharacterAI",
            "date": "2025-12-03"
          }
        ]
      },
      {
        "term": "relapse",
        "hits": 312,
        "precision": 88.0,
        "sample_posts": [...]
      }
    ],
    "subreddits": [
      { "name": "Character_AI_Recovery", "hits": 420, "pct": 34.2 },
      { "name": "ChatbotAddiction", "hits": 285, "pct": 23.2 },
      { "name": "CharacterAI", "hits": 198, "pct": 16.1 },
      { "name": "AI_Addiction", "hits": 95, "pct": 7.7 }
    ],
    "total_hits": 1565,
    "unique_posts": 1348
  },
  "romance": { ... },
  "consciousness": { ... },
  "therapy": { ... },
  "sexual_erp": { ... },
  "rupture": { ... }
}
```

### Export script requirements

Add a new function to the export script (or create `scripts/export_keyword_details.py`) that:

1. For each category in keywords.yaml:
   - List all keywords with their total hit count from keyword_hits
   - Include the precision score from the keyword's inline comment in keywords.yaml (parse the `# XX.X%` comment pattern)
   - For each keyword, pull 3 random sample posts: title, subreddit, date. Pick posts with non-empty, non-deleted titles (filter out "[deleted]" and "[removed]"). Prefer posts from the most recent 12 months so examples feel current.

2. For each category, compute subreddit distribution:
   - Count hits per subreddit
   - Calculate percentage of total category hits
   - Sort descending by hit count
   - Include all subreddits with at least 1% of the category's hits

3. Include total_hits and unique_posts (distinct post_id count) per category

4. Write to `web/data/keyword_details.json`

5. Add this export to the daily collection pipeline so it stays current

### Privacy note

Only include post TITLES, not body text. Titles are public and visible on Reddit without clicking into a post. Do not include author usernames, post IDs, or direct links to Reddit posts. This avoids any perception of surveillance or doxxing.

---

## Part 2: Frontend — Panel Design

### Interaction

**Opening:** Click any theme card → panel slides open below the cards and above the chart. The card gets a visual "selected" state (brighter border, slight elevation or glow). Only one panel open at a time — clicking a different card switches to that theme's panel. Clicking the same card again closes the panel.

**Closing:** Click the active card again, or click a small × button in the panel's top-right corner.

**Animation:** Panel slides down from 0 height with a quick ease-out transition (200ms). Content fades in slightly delayed (100ms after slide begins). No jarring layout shift — the chart should smoothly push down to make room.

### Panel Layout

The panel is a full-width container (same width as the chart area) with the theme's color as a subtle left border accent (matching the card's left border style).

Three columns inside:

```
┌─────────────────────┬──────────────────────┬─────────────────────────┐
│   TRACKED KEYWORDS  │  TOP COMMUNITIES     │  SAMPLE POSTS           │
│                     │                      │                         │
│   chatbot addiction │  Character_AI_       │  "Quit and deleted my   │
│   ████████░░  74    │  Recovery  34.2%     │   entire account..."    │
│                     │  ████████████░░░     │   r/ChatbotAddiction    │
│   relapse           │                      │   Nov 2025              │
│   ██████████░ 312   │  ChatbotAddiction    │                         │
│                     │  23.2%               │  "I finally deleted     │
│   cold turkey       │  ██████████░░░░░     │   C.AI I was addicted"  │
│   ██░░░░░░░░  18    │                      │   r/Character_AI_       │
│                     │  CharacterAI         │   Recovery · Sep 2025   │
│   ...               │  16.1%               │                         │
│                     │  ████████░░░░░░░     │  ...                    │
└─────────────────────┴──────────────────────┴─────────────────────────┘
```

#### Column 1: Tracked keywords

- Header: "Tracked keywords" in 12px uppercase muted text
- List of all keywords for this theme, sorted by hit count descending
- Each keyword shows:
  - The term in 14px, theme color
  - A horizontal bar showing relative volume (longest bar = highest hit count keyword, others proportional)
  - Hit count as a number at the end of the bar, in muted text
- Bar color: theme color at 30% opacity
- Bar background: #1E293B (dark surface)
- If more than 8 keywords, show first 8 with a "Show all N keywords" toggle

#### Column 2: Top communities

- Header: "Top communities" in 12px uppercase muted text
- List of subreddits sorted by hit count descending
- Each entry shows:
  - Subreddit name (format: "r/SubredditName") in 13px
  - Percentage of this theme's hits from that sub
  - A subtle horizontal bar showing the percentage
- Show top 6 subreddits. If more, show "and N more communities" in muted text
- Bar color: theme color at 20% opacity

#### Column 3: Sample posts

- Header: "Example posts" in 12px uppercase muted text
- Show 3 sample post titles, rotating through a different keyword each time if possible
- Each sample shows:
  - Post title in 13px, slightly brighter text (#CBD5E1), truncated to 80 chars with ellipsis if longer
  - Subreddit + date in 11px muted text below: "r/ChatbotAddiction · Nov 2025"
- Posts are separated by a subtle horizontal divider (0.5px #1E293B)
- No links to Reddit — just the title as text

#### Panel footer

A single line at the bottom of the panel in 11px muted text:
```
Showing N keywords across M communities · N,NNN total posts matched · All keywords validated at ≥80% precision
```

---

## Part 3: Responsive Behavior

### Desktop (≥ 1024px)
- Three-column layout as described above
- Panel max-height: 320px (scrollable if content overflows, but it shouldn't with the "show more" truncation)

### Tablet (640px – 1023px)
- Two-column layout: keywords + communities in left column (stacked vertically), sample posts in right column
- Panel max-height: 400px

### Mobile (< 640px)
- Full-width overlay/drawer that slides up from the bottom
- Single column: keywords first, then communities, then sample posts, stacked vertically
- Scrollable within the drawer
- Fixed header with theme name + close button at top of drawer
- Drawer height: 70vh (leaves the top of the main page visible so the user knows where they are)
- Background behind drawer: dimmed (rgba(0,0,0,0.4) overlay)
- Close by tapping × button, swiping down, or tapping the dimmed overlay

---

## Part 4: Visual Details

### Panel background
- Same as chart surface: #1A1D27
- Border: 0.5px solid #2A2D3A
- Border-radius: 8px
- Left border accent: 3px solid [theme color] (matching card style)

### Text colors
- Headers: #64748B (muted slate, 12px uppercase)
- Keyword terms: theme color, 14px
- Hit counts: #94A3B8, 13px
- Subreddit names: #CBD5E1, 13px
- Post titles: #CBD5E1, 13px
- Dates/metadata: #64748B, 11px
- Footer: #64748B, 11px

### Bars
- Keyword bars: theme color at 30% opacity, height 6px, border-radius 3px
- Community bars: theme color at 20% opacity, height 4px, border-radius 2px
- Bar track (background): #0F1117

### Transitions
- Panel open: height transition 200ms ease-out
- Panel close: height transition 150ms ease-in
- Content fade: opacity 0→1 over 150ms, delayed 50ms after panel begins opening

---

## Part 5: Export Pipeline Integration

The keyword details export should run as part of the same daily pipeline that generates keyword_trends.json. Add it to:
- The export script that runs after daily collection
- The manual export command (for when you re-tag and re-export after keyword changes)

Estimated JSON file size: ~50-100KB (small — it's just keyword lists, counts, and short post titles).

---

## What NOT to Build

- Direct links to Reddit posts (privacy concern, also URLs would bloat the JSON)
- Full post body text (titles only)
- Author usernames
- Per-keyword trend lines (save for v3)
- Filtering or search within the panel
- Keyword precision scores in the UI (they're in the JSON for future use, but showing "88% precision" to a general visitor creates more questions than it answers)
- Per-subreddit breakdowns when clicking a community name (v3 feature)

---

## Implementation Order

1. **Build the export script** — generate keyword_details.json from tracker.db (backend, Python)
2. **Add the JSON to the web build** — include keyword_details.json alongside keyword_trends.json
3. **Build the panel component** — desktop three-column layout first
4. **Wire up card click** — toggle panel open/close on card click
5. **Add responsive layouts** — tablet two-column, mobile drawer
6. **Polish** — transitions, hover states, truncation, "show more" toggles
7. **Integrate into daily pipeline** — ensure export runs automatically

---

## CC Prompt (Part 1 — Export)

```
Read docs/TRANSPARENCY_PANEL_SPEC.md. Start with Part 1 only: build the export script that generates web/data/keyword_details.json. For each category in keywords.yaml, pull all keywords with hit counts from keyword_hits, compute subreddit distribution, and sample 3 recent post titles per keyword (exclude deleted/removed posts, prefer last 12 months). Parse precision scores from keywords.yaml comments where available. Write the output to web/data/keyword_details.json. Do not build any frontend yet.
```

## CC Prompt (Part 2 — Frontend)

```
Read docs/TRANSPARENCY_PANEL_SPEC.md. Build the transparency panel frontend (Parts 2-4). Load data from web/data/keyword_details.json. When a theme card is clicked, slide open the detail panel below the cards showing three columns: tracked keywords with hit bars, top communities with percentage bars, and sample post titles. Only one panel open at a time. Make it responsive: three columns on desktop, two on tablet, bottom drawer on mobile. Follow the visual specs exactly. Do not add features from the "What NOT to Build" section.
```
