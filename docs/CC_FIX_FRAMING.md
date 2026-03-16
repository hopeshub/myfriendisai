# Fix Cross-Theme Comparison Framing

**Context:** The current dashboard implies that themes with higher hit rates represent bigger or more important phenomena. This is misleading. Hit rates reflect how distinctive and capturable each theme's vocabulary is, not how prevalent the underlying phenomenon is. Addiction language is clinically specific ("relapse," "cold turkey") and validates at near 100% precision. Romance language uses everyday words ("love," "boyfriend") that fail precision thresholds because they're indistinguishable from human relationship talk. Addiction showing 6.7/1k and Romance showing 4.8/1k does NOT mean addiction is more prevalent — it means addiction has a more distinctive vocabulary.

This document covers all changes needed to fix this across the site.

---

## 1. Stop sorting cards by value

**Current behavior:** Metric cards are sorted in descending order by hit rate, creating an implied ranking.

**New behavior:** Cards use a FIXED order that reflects a conceptual taxonomy, not a leaderboard. The order should be:

```
Romance → Sex / ERP → Consciousness → Therapy → Addiction → Rupture
```

This loosely follows a narrative arc: how people engage with AI companions (romance, sex), how they think about what's happening (consciousness), how they use it for wellbeing (therapy), when it becomes problematic (addiction), and when the relationship is disrupted (rupture).

**Do NOT re-sort when the time range changes.** The order is always fixed.

---

## 2. Update the main page subtitle

**Current:**
```
Tracking AI companion discourse across 6 themes, Jan 2023 to Feb 2026.
```

**New:**
```
Tracking how people talk about AI companions across 27 Reddit communities, from January 2023 to present.
```

This shifts emphasis from "6 themes" (which invites comparison between them) to "27 communities" and the temporal scope (which frames the project as longitudinal tracking).

---

## 3. Add a short explainer line below the metric cards

Add a single line of small muted text between the metric cards row and the chart. This provides context for the numbers without being intrusive.

**Text:**
```
Each theme tracks validated keywords — hit rates reflect how distinctive each theme's vocabulary is, not how prevalent the topic is overall. See About for methodology.
```

**Styling:**
- Font size: 12px
- Color: #64748B (muted slate)
- Centered
- Margin: 8px above, 16px below (sits between cards and chart)
- "About" should be a link to /about

---

## 4. Add a section to the About page

Add this as a new section BEFORE "What this captures and what it doesn't" (since it's arguably the most important methodological caveat).

**Section header:** `Why hit rates don't compare across themes`

**Section text:**
```
A theme's hit rate reflects how often people use distinctive, validated language for that topic — not how prevalent the topic is overall.

Some themes have highly specific vocabulary. When someone describes AI addiction, they borrow clinical recovery language: "relapse," "cold turkey," "chatbot addiction." These terms are rare outside that context and validate at near-perfect precision. The keyword net catches most of what's there.

Other themes are expressed through everyday language. When someone is in a romantic relationship with their AI, they say "I love him," "my boyfriend," "we went on a date" — words that are indistinguishable from how people talk about human relationships. These fail precision validation because they can't be reliably attributed to AI companionship. Only highly specific phrases like "our wedding" or "my AI partner" survive, meaning the keyword net captures only a fraction of the actual romance discourse.

The result: addiction may show a higher hit rate than romance, but that reflects vocabulary distinctiveness, not phenomenon size. Each theme's trend line is meaningful over time — a spike or decline in a theme tells you something real about how that conversation is changing. But comparing hit rates between themes does not tell you which topic is "bigger" or more important.
```

---

## 5. Update the card unit label

**Current:** `hits / 1k posts`

**New:** `mentions / 1k posts`

"Mentions" is slightly more intuitive for a general audience than "hits" and avoids the technical/gaming connotation. Apply this change to:
- The metric cards on the main page
- The y-axis label on the chart in absolute mode
- The tooltip in absolute mode
- The About page text (change "how often these validated terms appear per 1,000 posts" to "how often these validated terms are mentioned per 1,000 posts")

---

## 6. Minor: fix date range in subtitle

The subtitle currently says "Jan 2023 to Feb 2026" as a static string. It should say "January 2023 to present" — or better, dynamically compute the latest month from the data. At minimum, change the hardcoded "Feb 2026" to "present" so it doesn't go stale.

---

## Summary of changes

| # | What | Where |
|---|------|-------|
| 1 | Fixed card order (Romance → Sex/ERP → Consciousness → Therapy → Addiction → Rupture) | Main page, TrendsExplorer component |
| 2 | Updated subtitle text | Main page headline area |
| 3 | Added explainer line below cards | Main page, between cards and chart |
| 4 | New methodology section on cross-theme comparison | About page, before "What this captures" |
| 5 | Changed "hits" to "mentions" across all UI | Cards, chart axis, tooltips, About page |
| 6 | Changed date range to "to present" | Main page subtitle |

---

## CC Prompt

```
Read docs/CC_FIX_FRAMING.md and implement all 6 changes. The most important change is #1 — stop sorting cards by value, use the fixed order specified. Do not re-sort on time range change. Apply all changes to both the main page and the About page as described.
```
