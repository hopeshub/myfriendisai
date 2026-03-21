# myfriendisai — v1 Rebuild Plan

**Created:** March 11, 2026  
**Goal:** A single-page keyword trends explorer — like Google Trends for AI companionship on Reddit.  
**Core experience:** Someone lands on the site, sees keyword topic categories, clicks one, and immediately sees how that topic has grown or changed across tracked communities from 2023 to present.

---

## Current State (what exists and works)

- ✅ Backfill pipeline: ~27/31 subreddits backfilled via PullPush (2023–2026)
- ✅ Database: tracker.db with posts table (~9.5 GB, hundreds of thousands of posts)
- ✅ Daily snapshot aggregation: export_json.py computes daily post/comment counts from posts table
- ✅ Keyword categories: defined in config/keywords.yaml (consciousness, grief, dependency, romance, etc.)
- ✅ Event annotations: defined in database events table (Replika ERP removal, GPT-4o launch/retirement, etc.)
- ✅ Frontend shell: Next.js site deployed on Vercel at myfriendisai.com
- ✅ Domain + GitHub + Vercel pipeline: push to main → auto-deploy
- ❌ Keyword tagging: posts have NOT been scanned against keyword lists
- ❌ Keyword frequency data: no daily keyword counts exist yet
- ❌ Frontend: chart/toggles/filters are broken or non-functional
- ❌ X-axis labels: no year indicators, timeline is unreadable

---

## Rebuild Phases

Work through these IN ORDER. Do not skip ahead. Each phase has a clear deliverable and a "done" condition.

### Phase 1: Keyword Tagging Pipeline
**Type:** Backend (Python, in CC)  
**Depends on:** Backfill data in tracker.db, keywords.yaml  

**What to build:**
- A script (`scripts/tag_keywords.py`) that scans every post in tracker.db against the keyword categories in keywords.yaml
- For each post, check the title + body text for matches against each category's keyword list
- Store results in a new `keyword_hits` table: post_id, subreddit, category, matched_term, post_date
- A post can match multiple categories (e.g., a post mentioning "addicted" and "sentient" hits both dependency and consciousness)
- Script should be idempotent — running it again doesn't create duplicate hits
- Script should log progress (it's scanning hundreds of thousands of posts, will take a while)

**Done when:** You can run `SELECT category, COUNT(*) FROM keyword_hits GROUP BY category` and see real numbers for each category.

**CC prompt:**
```
Read config/keywords.yaml for the keyword categories and terms. Build scripts/tag_keywords.py that scans every post in tracker.db (title + selftext fields) for matches against each keyword category. Store matches in a new keyword_hits table with columns: id, post_id, subreddit, category, matched_term, post_date. Make it idempotent (skip posts already tagged). Log progress every 1000 posts.
```

---

### Phase 2: Keyword Frequency Export
**Type:** Backend (Python, in CC)  
**Depends on:** Phase 1 complete  

**What to build:**
- Add keyword aggregation to `scripts/export_json.py`
- For each keyword category, for each day, count the number of matching posts
- Export as `web/data/keyword_trends.json` — format: `{ "consciousness": [{"date": "2023-01-15", "count": 12}, ...], "grief": [...], ... }`
- Also export a version with 7-day rolling averages for smoother chart display
- Optionally: also break down by subreddit (for future drill-down feature)

**Done when:** `web/data/keyword_trends.json` exists, is populated, and you can open it and see daily counts per category spanning 2023–2026.

**CC prompt:**
```
Add keyword trend aggregation to scripts/export_json.py. Query the keyword_hits table to produce daily counts per keyword category. Export to web/data/keyword_trends.json. Also compute 7-day rolling averages. Format: { "category_name": [{"date": "YYYY-MM-DD", "count": N, "count_7d_avg": N}, ...] }. Push the updated JSON to GitHub.
```

---

### Phase 3: Design Spec for Frontend
**Type:** Planning (you + me, NOT in CC yet)  
**Depends on:** Phase 2 complete (need real data to design against)  

**What to decide:**
- Sketch the page layout (on paper or in notes): where does the chart go, where do keyword toggles go, where do event labels go
- Finalize color palette: dark gray/black background, orange primary accent, gray secondary, white text
- Decide: one keyword at a time, or multiple overlaid? (Recommendation: one at a time for v1, cleaner)
- Decide: what's the default state when someone first loads the page? Which keyword, which time range?
- Decide: how do event annotations display without overlapping? (The current pileup on the right side of the chart)
- Write a CC brief that captures ALL of these decisions so CC isn't guessing

**Done when:** You have a written brief (even just bullet points) that describes exactly what the page looks like and how it behaves. No ambiguity for CC.

---

### Phase 4: Frontend Rebuild
**Type:** Frontend (Next.js/React, in CC)  
**Depends on:** Phase 3 complete  

**What to build:**
- Tear down the existing broken chart/toggles
- Build a single-page trends explorer with:
  - Keyword category selector (top of page): row of toggles, one active at a time, selected = orange, unselected = gray
  - Main chart: area or line chart showing keyword frequency over time, using 7-day rolling average
  - Time range selector: 30D / 90D / 1Y / ALL — actually functional
  - X-axis with YEAR labels (Jan '23, Jul '23, Jan '24, etc.)
  - Event annotation markers: vertical dotted lines at key dates, with labels that DON'T overlap
  - Tooltip on hover showing: date, count, active keyword category
- Color palette: #0F1117 background, #1A1D27 card surface, #F97316 (orange) accent, #94A3B8 (gray) secondary, #F8FAFC (white) text
- Responsive but desktop-primary (don't over-optimize for mobile in v1)

**Done when:** You land on myfriendisai.com, see a clean chart, can toggle between keyword categories and see different trend shapes, can change time ranges, and event markers are readable.

**CC prompt (draft — refine after Phase 3):**
```
Rebuild the homepage of the myfriendisai site. Read REBUILD_PLAN.md for full context. The page is a single keyword trends explorer. [Include all Phase 3 decisions here]. Read the data from web/data/keyword_trends.json. Use the 7-day rolling average values for the chart line. Keep the existing nav links and footer. Replace everything else.
```

---

### Phase 5: Polish & Ship
**Type:** Frontend + content (in CC)  
**Depends on:** Phase 4 complete  

**What to do:**
- Add an "About" page explaining what this project is, how data is collected, methodology, limitations
- Fix the nav links (Communities page can be a placeholder or removed for v1)
- Add a brief explainer under the chart: what the keyword categories mean
- Test all time ranges, all keyword toggles, and event annotations
- Hard refresh on mobile to make sure it's not broken (doesn't need to be great, just not broken)
- Final push + verify on myfriendisai.com

**Done when:** You're comfortable sharing the link publicly.

---

## Future (v2 — NOT part of this rebuild)

These are real features but they come later. Don't let them creep into v1.

- Community drill-down pages (click a subreddit, see its individual trends)
- Multi-keyword overlay (see two categories on the same chart)
- Keyword breakdown by subreddit (where is "consciousness" talk happening most?)
- Community comparison tool
- Data export (PNG charts, CSV data)
- Daily automated collection (collect_daily.py on cron)
- Sentiment analysis layer
- Search/filter for individual posts

---

## How to Use This Document

1. Put this file in your project root: `~/Projects/myfriendisai/REBUILD_PLAN.md`
2. When starting a CC session, tell it: "Read REBUILD_PLAN.md for project context"
3. Work through phases in order — check the "Done when" before moving on
4. When you come back to me for guidance, tell me which phase you're on
5. Update the checkboxes (change ❌ to ✅) as you complete phases
