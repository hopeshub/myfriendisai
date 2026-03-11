# myfriendisai.com — UI/UX Spec
## Frontend Design & Visualization Framework
*Draft v1.0 · March 2026*

---

## 1. Core Design Philosophy

This is a **data visualization showcase**, not a research tool. The experience should feel like Google Trends meets a cultural observatory. Someone lands, sees something moving, clicks a lens, feels like they discovered something, shares it.

**The guiding principle:** The homepage IS the product. No explainer page, no onboarding, no "what is this site" wall of text. Just the data, immediately, with enough context to make it legible.

**Aesthetic target:** Clean, dark, data-forward. Think Bloomberg Terminal meets Are.na. Not a academic paper, not a startup dashboard. Minimal chrome, maximum signal.

---

## 2. Homepage — The Hero Chart

The entire homepage is built around one primary visualization.

### 2.1 The Main Chart

A time-series line chart showing community engagement over time. Default view on load:

- **X axis:** Time (default: last 90 days, expandable to all-time)
- **Y axis:** Normalized engagement (not raw subscribers — activity composite)
- **Lines:** One line per community tier, aggregated
  - Companionship communities (highlighted, primary color)
  - Recovery communities (accent color)
  - Control subs (muted, for comparison)
- **Event markers:** Vertical lines with labels at key moments (see Section 4)

The key visual story on load: **companionship communities growing faster than control subs.** This should be immediately legible without reading anything.

### 2.2 Time Range Selector

Simple toggle across the top of the chart:

```
[ 30D ]  [ 90D ]  [ 6M ]  [ 1Y ]  [ ALL ]
```

Clicking updates the chart instantly. Default: 90D.

### 2.3 The Lens Selector

Six clickable lenses below or beside the chart. Clicking a lens recolors/refilters the chart to show that keyword dimension instead of raw engagement.

```
📈 Growth    💕 Romance    🔁 Addiction    🤖 Consciousness    💔 Grief    🔞 ERP
```

Each lens maps to keyword categories:

| Lens | Keyword Categories |
|---|---|
| 📈 Growth | Raw subscriber/activity data (default) |
| 💕 Romance | relationship_language + attachment_language |
| 🔁 Addiction | dependency_language + withdrawal_relapse_language |
| 🤖 Consciousness | sentience_consciousness_language |
| 💔 Grief | grief_rupture_language |
| 🔞 ERP | sexual_roleplay_language |

When a lens is active, the chart shows **keyword density over time** (hits per 100 posts) rather than raw engagement. The event markers stay visible on all lenses.

### 2.4 The "vs. Control" Toggle

A subtle toggle that overlays the control sub trend line for comparison:

```
[ Show vs. control subs ]
```

Default: off. When on, adds a muted line showing the same metric in r/ChatGPT and r/singularity. The visual gap between companionship and control is the "aha moment."

---

## 3. Community Cards (Below the Hero Chart)

Below the main chart, a row of community cards — one per tracked subreddit. Small, scannable, not the main event.

Each card shows:
- Subreddit name + tier badge
- Subscriber count
- 7-day sparkline (tiny trend line)
- Top keyword category firing this week (e.g. "💕 Romance ↑")
- Access status badge for restricted/inaccessible subs

Clicking a card opens a **community detail view** (see Section 5).

---

## 4. Event Markers

Vertical lines on the chart at key moments. These are the screenshot moments — when someone sees a spike and there's a label, that's what gets shared.

**Pre-seeded events:**

| Date | Label | Notes |
|---|---|---|
| Feb 2023 | 💔 Replika removes ERP | Defining grief event. Suicide resources pinned. |
| May 2024 | ✨ GPT-4o launches | Enhanced warmth/voice. Largest companionship attachment spike. |
| Aug 2025 | 📢 First 4o retirement attempt | OpenAI backed down under pressure. |
| Oct 2025 | 📊 MIT loneliness study published | Found heavy ChatGPT users lonelier, older users most dependent. |
| Jan 29, 2026 | 🚨 #Keep4o movement begins | 19K+ petition signatures. Physical protests at OpenAI HQ. |
| Feb 13, 2026 | 💔 GPT-4o retired | Day before Valentine's Day. "Emotional lobotomy" framing dominant. |

**Future events:** Walker adds these manually via a simple admin mechanism (a yaml file or direct database entry). No CMS needed.

---

## 5. Community Detail View

Clicking any community card opens a detail page at `/communities/[subreddit-name]`.

Shows:
- Full time-series chart for that community
- All 6 lens options available
- Subscriber growth over time
- Top posts from the last 7 days (titles only, linked to Reddit)
- Keyword breakdown: which categories are firing and how often
- Access status and any collection notes

---

## 6. Navigation

Minimal. Three items max:

```
myfriendisai.com          Communities    About    [GitHub ↗]
```

- **Communities** — scrolls to the community cards section or opens a full list view
- **About** — single page explaining the project, methodology, data sources, and limitations
- **GitHub** — links to the public repo (transparency signal for researchers)

---

## 7. About Page

Short. Three sections:

1. **What this is** — 2-3 sentences. "A public tracker monitoring Reddit communities where people form emotional attachments to AI. Updated daily."
2. **How it works** — Brief methodology: what's collected, how keywords are tracked, what the tiers mean, data limitations (sample size, English-language bias, etc.)
3. **Who made it** — Walker's framing as a qualitative researcher. Link to Twitter/X @hopes_revenge. Contact.

---

## 8. Visual Design Notes

- **Color palette:** Dark background (#0a0a0a or similar). Primary accent: a cool blue or teal for companionship lines. Warm amber/orange for recovery. Muted grey for controls.
- **Typography:** Clean sans-serif. Inter or similar. Data should feel crisp, not cozy.
- **Chart library:** Recharts (already in the stack). Use smooth curves not jagged lines.
- **Mobile:** The hero chart should be fully functional on mobile. Lens selector becomes a horizontal scroll. Community cards stack vertically.
- **Loading states:** Show skeleton loaders, not spinners. Data should feel like it's populating, not loading.

---

## 9. Implementation Priority

Build in this order:

1. **Hero chart with Growth lens** (raw engagement over time) — this is the MVP
2. **Time range selector** — 30D/90D/1Y/ALL
3. **Event markers** — pre-seed the 6 events above
4. **Lens selector** — wire up keyword data to chart (requires keyword data to accumulate first — build the UI now, populate with real data in 2-4 weeks)
5. **vs. Control toggle**
6. **Community cards with sparklines**
7. **Community detail pages**
8. **About page**

---

## 10. What We're NOT Building (yet)

- User accounts or saved views
- Data export / download
- Email alerts
- Comments or community features
- Any backend CMS for event markers (yaml file is fine)
- Individual post drill-down (post titles only, linked out to Reddit)

---

*Draft v1.0 · March 2026 · Save to docs/ui_spec.md in project root*
