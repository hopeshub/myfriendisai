# AI Companion Community Tracker — Project Spec

## 1. What This Is

A public-facing website that tracks a curated set of Reddit communities related to AI companionship — chatbot relationships, virtual girlfriend/boyfriend apps, AI friendship tools, and adjacent phenomena. The site visualizes community health and engagement over time, making the growth and cultural dynamics of AI companionship legible as a longitudinal trend.

**Core thesis:** AI companionship is proliferating, and Reddit community engagement is a meaningful proxy signal for that. The site makes this argument visually across a multi-year window.

**Audience:** Public. This is a research artifact meant to be discovered, shared, and cited. It needs to look polished and load fast.

**Success criteria (30-day milestone):** Within 30 days of starting the build, the site should show stable daily snapshots for at least 15 communities, fast-loading time-series charts, and at least 3 visible multi-week trends. The data should be updating daily without manual intervention, and the site should be live at myfriendisai.com.

---

## 2. What It Tracks

### 2.1 Target Communities

**27 subreddits** organized into 4 tiers in `config/communities.yaml`. See `subreddits.md` for the full community map, research methodology, and selection rationale.

| Tier | Description | Count | Subreddits |
|------|-------------|-------|------------|
| **T0** — General AI | Companionship surfaces here | 5 | ChatGPT, OpenAI, singularity, ClaudeAI, claudexplorers |
| **T1** — Primary Companionship | AI companionship is central topic | 10 | replika, CharacterAI, MyBoyfriendIsAI, ChatGPTcomplaints, AIRelationships, MySentientAI, BeyondThePromptAI, MyGirlfriendIsAI, AICompanions, SoulmateAI |
| **T2** — Platform-Specific | Specific AI companion products | 8 | KindroidAI, NomiAI, SpicyChatAI, ChaiApp, HeavenGF, Paradot, AIGirlfriend, ChatGPTNSFW |
| **T3** — Recovery & Dependency | Quitting and peer support | 4 | Character_AI_Recovery, ChatbotAddiction, AI_Addiction, CharacterAIrunaways |

Adjacent subs (relationship_advice, depression, etc.) were tested and removed — keyword overlap with non-AI relationship language made them too noisy for trend analysis.

Blocked subs monitored but not tracked: AISoulmates (403, private), 4oforever (403, invite-only), AIBoyfriends (403).

### 2.2 Engagement / Health Metrics

The goal is NOT just subscriber count (a vanity metric). The goal is to capture **community vitality** — how alive, active, and engaged a subreddit actually is. Small subreddits with intense discourse should register as "healthy."

**Important context:** As of September 2025, Reddit itself replaced public subscriber counts with two new metrics:
- **Visitors:** Unique users who visited a subreddit in the past 7 days (rolling 28-day average)
- **Contributions:** Non-removed posts + comments made in the past 7 days

These are now Reddit's own primary engagement signals and align perfectly with what we're trying to measure.

**Metrics to collect daily per subreddit:**

| Metric | Source | Notes | Provenance |
|--------|--------|-------|------------|
| Subscribers | `about.json` → `subscribers` | Still available via API even though hidden on page | Direct |
| Active users now | `about.json` → `active_user_count` | Snapshot, not historical | Direct |
| Visitors (7-day) | TBD — may need scraping or new API field | Reddit's new metric; check if available in `.json` | Direct (if available) |
| Contributions (7-day) | TBD — may need scraping or new API field | Reddit's new metric; check if available in `.json` | Direct (if available) |
| Posts per day | Count from `new.json` | Collect last 100 posts, calculate daily rate | Inferred |
| Average comments per post | From post listings | `num_comments` field on each post | Inferred (sample-based) |
| Average score per post | From post listings | `score` field on each post | Inferred (sample-based) |
| Unique authors (approx) | From post listings | Count distinct `author` values in recent posts | Inferred (sample-based) |

**Derived metrics (calculated, not collected):**

*MVP — ship these immediately as simple ratios:*

| Metric | Formula | What it shows | Data provenance |
|--------|---------|---------------|-----------------|
| Comments-per-post ratio | avg(num_comments) | Depth of discourse | Derived from direct |
| Participation rate | unique_authors / subscribers | What % of members are active | Derived from direct + inferred |
| Contributions-per-Visitor | contributions / visitors | Intensity of engagement | Derived from direct (if available) |

*Phase 2 — only after seeing real data distributions:*

| Metric | Formula | What it shows |
|--------|---------|---------------|
| Engagement Index | Weighted composite of above | Overall "health" score — DO NOT build this until we've seen 4+ weeks of real data and understand the distributions. A premature composite score looks authoritative but is fragile. |

**Data provenance labels:** Every metric displayed on the site should be tagged as one of:
- **Direct** — value comes straight from Reddit's response (e.g., subscribers, score, num_comments)
- **Inferred** — approximated from available data (e.g., unique_authors from a 100-post sample)
- **Derived** — calculated from other metrics (e.g., comments-per-post ratio)

This matters because the site is a citeable research artifact. Users should know what they're looking at.

### 2.3 Keyword Tracking (IMPLEMENTED)

Regex-based keyword tagging runs on all collected posts via `scripts/tag_keywords.py` and on comments via `scripts/tag_comments.py`. Results are stored in the `post_keyword_tags` and `comment_keyword_hits` tables and exported to `data/keyword_trends.json` for frontend charts.

**6 keyword themes** in `config/keywords_v8.yaml`, validated via manual qualitative coding (100-post reads per keyword, no automated classifiers):

| Theme | Keywords | Unique Posts | Description |
|-------|----------|-------------|-------------|
| **therapy** | 8 | ~1,366 | AI described as therapeutic support or therapist replacement |
| **consciousness** | 13 | ~1,650 | Claims or beliefs about AI sentience, personhood, or inner experience |
| **addiction** | 15 | ~1,695 | Self-reported addiction, compulsive use, and attempts to quit or recover |
| **romance** | 19 | ~2,126 | Romantic framing of a personal relationship with AI |
| **sexual_erp** | 13 | ~6,515 | Sexual content, erotic roleplay, and NSFW interactions with AI |
| **rupture** | 14 | ~1,548 | Loss or disruption of AI companion relationships due to platform changes |

**Scope:** Keywords are matched against T1-T3 companion communities only. JanitorAI_Official and SillyTavernAI are excluded (bot card noise — dominant false positive source). T0 general AI subs are excluded from keyword trend lines.

**Comment tagging (IMPLEMENTED 2026-03-18):** Comments on eligible posts are also scanned with the same keyword matching logic. Comment-sourced tags are propagated up to the parent post in `post_keyword_tags` with `source='comment'`. This expands the construct from "theme language in posts" to "theme language in thread discourse." The JSON export produces dual metrics: post+comment (default) and post-only (control). See `docs/COMMENTS_SYSTEM_SPEC.md` for full methodology and rationale.

**Historical coverage note:** All backfilled data (via PullPush, pre-2026-03-18) was tagged against post title and body text only — no comments were collected or tagged for historical posts. The post+comment and post-only metrics are identical for all data before 2026-03-18.

**Overlap policy:** Themes are not mutually exclusive. A single post can appear in multiple theme trend lines if it matches keywords from more than one theme. Trend lines count unique posts per theme. Cross-theme overlap is documented in `docs/cross_theme_overlap.md`. Highest overlap: therapy × sexual_erp (21.8% of therapy posts). Most exclusive theme: addiction (96.4% exclusive).

**Validation methodology:** Each keyword validated via manual qualitative coding:
1. Pull 100 random matching posts from T1-T3
2. Read each post (title + body) and classify YES/NO/AMBIGUOUS
3. Calculate relevance = YES / (YES + NO) × 100
4. Thresholds: ≥80% = KEEP, 60-79% = REVIEW (researcher decides), <60% = CUT, <10 hits = LOW VOLUME
5. Full validation docs in `docs/validation_*.md`

**Researcher-accepted keywords:** Keywords scoring in the review band (60-79%) may be accepted at the researcher's discretion when all of the following conditions are met:
1. False positive patterns are well-defined and categorizable (not random noise)
2. No cross-theme collisions above 30%
3. The keyword captures vocabulary not already represented by existing keywords in the theme
4. False positive patterns are amenable to future LLM-based disambiguation (stage 2 filtering)

These decisions are logged with rationale in the keyword's scoring sheet. Researcher-accepted keywords are tagged as such in keywords_v8.yaml (or current version) to distinguish them from auto-accepted (≥80%) keywords.

Current researcher-accepted keywords:
- "grieving" → Rupture (74.0%) — FPs are real-world grief, fictional roleplay, and lawsuit coverage; TPs cleanly hit 4o deprecation, Replika Feb 2023, SoulmateAI shutdown. No cross-theme collisions. Accepted for vocabulary diversity (first emotional-register keyword in a theme dominated by the lobotomy metaphor).
- "neutered" → Rupture (79.0%) — FPs are general tech complaints and literal cat neutering; synonym of "nerfed" capturing different user vocabulary. No cross-theme collisions.

**Keyword research history:**
- Original `keywords.yaml`: 16 categories, ~200 keywords (pre-validation)
- `keywords_v4.yaml`: Consolidated to 5 themes, candidate keyword lists
- `keywords_v5.yaml`: Post-validation, removed all CUT/LOW VOLUME keywords, excluded JanitorAI/SillyTavern
- `keywords_v6.yaml`: Therapy Round 2 (added 3 keywords), revalidation without JanitorAI/SillyTavern (promoted 5 keywords)
- `keywords_v8.yaml`: LOCKED. Cleanup batch (promoted 5), new Rupture theme (6 keywords). No pending REVALIDATE tags. Addiction Round 2 in progress.

Research artifacts in `docs/`.

---

## 3. Technical Architecture

### 3.1 Data Source Strategy

**Primary: Reddit's public `.json` endpoints (NO API CREDENTIALS NEEDED)**

As of November 2025, Reddit removed self-service API access. New OAuth credentials require a manual approval process with no guaranteed timeline. We bypass this entirely.

Reddit has a long-standing feature: append `.json` to any Reddit URL to get structured data back.

**Key endpoints:**

```
# Subreddit metadata (subscribers, active users, description)
https://www.reddit.com/r/{subreddit}/about.json

# Recent posts (up to 100 per request)
https://www.reddit.com/r/{subreddit}/new.json?limit=100

# Top posts by timeframe
https://www.reddit.com/r/{subreddit}/top.json?limit=100&t=week

# Search within subreddit (for keyword tracking)
https://www.reddit.com/r/{subreddit}/search.json?q={keyword}&restrict_sr=on&limit=100&t=week
```

**Rate limits (unauthenticated):** ~10 requests per minute. MUST set a custom User-Agent header (default gets 429'd instantly).

**For ~20 subreddits daily (MVP, no keyword searches):** ~40-60 requests total (about + new/top for each). At 10/min, that's ~6 minutes. Completely feasible. Phase 2 keyword searches add more requests but are still well within limits.

**Backup: Apply for API access anyway.** Submit through Reddit's Developer Support form describing the project as non-commercial research. If approved, we'd get 100 req/min (10x faster) and access to PRAW. But don't block on this.

**Secondary (Phase 2): Arctic Shift for historical backfill**

Arctic Shift (https://arctic-shift.photon-reddit.com/) is a community-maintained archive of Reddit data with:
- Bulk data dumps going back years
- A limited API with aggregation endpoints (e.g., comment frequency per subreddit over time)
- A web search interface for manual queries

This would let us backfill historical post/comment volumes for target subreddits, so the site launches with years of trend data instead of starting from zero.

### 3.2 Tech Stack

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| Data collection | Python 3.11+ with `requests` | Simple, no PRAW dependency needed |
| NSFW data access | Self-hosted Redlib (Docker) | Bypasses Reddit's NSFW block for subreddit-level NSFW communities |
| Database | SQLite (local) + JSON/API for frontend | Lightweight for collection; Vercel serves static or API |
| Scheduling | launchd (macOS) | Single daily job chains collect → push → deploy |
| Frontend | Next.js (React) | Vercel-native, SSG for fast public site |
| Charts | Recharts or D3 | Time-series visualization |
| Hosting | Vercel | Free tier, fast CDN, easy deploys |
| Domain | myfriendisai.com | Purchased and ready to connect |

### 3.3 Directory Structure

```
ai-companion-tracker/
├── CLAUDE.md                 # Project context for Claude Code (this file, adapted)
├── README.md
├── requirements.txt
├── .env.example              # Reddit API creds (if/when approved)
├── .gitignore
│
├── config/
│   ├── communities.yaml      # Target subreddits and categories
│   └── keywords_v8.yaml      # Keyword themes and terms (locked)
│
├── src/
│   ├── __init__.py
│   ├── collector.py           # Main data collection logic
│   ├── reddit_client.py       # HTTP client for .json endpoints
│   ├── keyword_matching.py    # Shared keyword regex matching (used by post + comment taggers)
│   ├── db/
│   │   ├── __init__.py
│   │   ├── schema.py          # SQLite schema definition
│   │   └── operations.py      # Insert/query helpers + JSON export
│   └── utils/
│       ├── __init__.py
│       └── rate_limiter.py    # Respect rate limits
│
├── scripts/
│   ├── run_collect.sh         # launchd wrapper: runs collection → push → deploy
│   ├── push_and_deploy.sh     # Git commit/push + Vercel deploy (called by run_collect.sh)
│   ├── collect_daily.py       # Python collection pipeline (5 steps)
│   ├── validate_deploy.py     # Pre-deploy data validation
│   ├── collect_comments.py    # Comment collection for eligible posts
│   ├── tag_keywords.py        # Post keyword tagger
│   ├── tag_comments.py        # Comment keyword tagger + post-level propagation
│   ├── validate_access.py     # Test that all subreddits are accessible
│   └── backfill_pullpush.py   # Historical post backfill via PullPush
│
├── migrations/
│   └── 001_add_comment_tables.py  # Schema migration for comment system
│
├── data/
│   └── tracker.db             # SQLite database (gitignored)
│
├── web/                       # Frontend (TBD structure)
│   └── ...
│
└── analysis/
    └── exploration.py         # Ad-hoc analysis scripts
```

### 3.4 Database Schema (SQLite)

```sql
-- Subreddit metadata snapshots (one row per subreddit per day)
CREATE TABLE subreddit_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subreddit TEXT NOT NULL,
    snapshot_date DATE NOT NULL,
    data_source TEXT NOT NULL DEFAULT 'json_endpoint',  -- 'json_endpoint', 'redlib', 'arctic_shift'
    subscribers INTEGER,
    active_users INTEGER,
    -- Reddit's new engagement metrics (if available via .json)
    visitors_7d INTEGER,
    contributions_7d INTEGER,
    -- Calculated from post listings
    posts_today INTEGER,
    avg_comments_per_post REAL,
    avg_score_per_post REAL,
    unique_authors INTEGER,
    -- Raw response preservation (for reprocessing if parser changes)
    raw_about_json TEXT,            -- Full JSON response from about.json
    raw_listing_json TEXT,          -- Full JSON response from new.json
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(subreddit, snapshot_date)
);

-- Individual posts collected
CREATE TABLE posts (
    id TEXT PRIMARY KEY,          -- Reddit post ID
    subreddit TEXT NOT NULL,
    title TEXT,
    author TEXT,
    created_utc INTEGER,
    score INTEGER,
    num_comments INTEGER,
    upvote_ratio REAL,
    is_self BOOLEAN,
    selftext TEXT,
    url TEXT,
    collected_date DATE NOT NULL,
    data_source TEXT NOT NULL DEFAULT 'json_endpoint',
    raw_json TEXT,                 -- Full raw post JSON for reprocessing
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Post-level keyword tags (one row per post × category × keyword × source)
CREATE TABLE post_keyword_tags (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id     TEXT    NOT NULL,
    subreddit   TEXT    NOT NULL,
    category    TEXT    NOT NULL,       -- theme name (e.g., "consciousness")
    matched_term TEXT   NOT NULL,       -- the keyword that matched
    post_date   DATE    NOT NULL,
    source      TEXT    NOT NULL DEFAULT 'post',  -- 'post' or 'comment'
    UNIQUE(post_id, category, matched_term, source)
);

-- Comments collected from Reddit
CREATE TABLE comments (
    id TEXT PRIMARY KEY,               -- Reddit comment ID
    post_id TEXT NOT NULL,             -- Parent post ID
    subreddit TEXT NOT NULL,
    author TEXT,
    body TEXT,
    score INTEGER,
    depth INTEGER NOT NULL DEFAULT 0,  -- 0 = top-level
    parent_id TEXT,                    -- Parent comment ID (NULL for top-level)
    created_utc INTEGER,
    permalink TEXT,
    collected_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    FOREIGN KEY (post_id) REFERENCES posts(id)
);

-- Keyword matches found in comment text
CREATE TABLE comment_keyword_hits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    comment_id TEXT NOT NULL,
    post_id TEXT NOT NULL,              -- Denormalized for fast propagation
    subreddit TEXT NOT NULL,
    category TEXT NOT NULL,
    matched_term TEXT NOT NULL,
    post_date DATE NOT NULL,            -- Comment's date for time-series
    FOREIGN KEY (comment_id) REFERENCES comments(id),
    FOREIGN KEY (post_id) REFERENCES posts(id)
);

-- Tracks which posts have had comments collected (prevents re-collection)
CREATE TABLE comment_collection_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id TEXT NOT NULL,
    subreddit TEXT NOT NULL,
    comments_collected INTEGER NOT NULL DEFAULT 0,
    collected_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    FOREIGN KEY (post_id) REFERENCES posts(id)
);

-- Categories and subreddit membership
CREATE TABLE subreddit_config (
    subreddit TEXT PRIMARY KEY,
    category TEXT NOT NULL,
    display_name TEXT,
    description TEXT,
    added_date DATE NOT NULL,
    is_active BOOLEAN DEFAULT 1
);
```

---

## 4. Collection Logic

### 4.1 Daily Pipeline

A single launchd job (`com.myfriendisai.collect-daily`) triggers `scripts/run_collect.sh` daily at 6am local time. The wrapper chains three stages:

```
Stage 1: Collection (collect_daily.py — 5 steps)
  1. Collect posts — about.json + new.json for each subreddit
  2. Tag posts — regex keyword matching on T1-T3 posts
  3. Collect comments — posts 5-6 days old with 5+ comments
  4. Tag comments + propagate — keyword matching on comment text
  5. Export JSON — write to data/*.json, copy to web/data/
  (~45-80 min typical, up to ~5 hours under heavy throttling)

Stage 2: Push & deploy (push_and_deploy.sh)
  1. Check for data file changes (tracked + untracked)
  2. Run pre-deploy validation (validate_deploy.py)
  3. git add + commit data/*.json and web/data/*.json
  4. git push (SSH to github.com)
  5. vercel --prod --yes
  (~2 min)

Stage 3: Health status
  1. Write web/public/status.json (collection stats, push status)
  2. macOS notification on failure
  3. Append to logs/failures.log on failure
```

**Key design decisions:**
- Push runs immediately after collection (not on a fixed schedule) so there's no timing gap
- Push failure is non-fatal — collection data is safe in SQLite regardless
- Lock file (`data/.collect_daily.lock`, `fcntl.LOCK_EX`) prevents overlapping runs
- No cron jobs — launchd only (cron was removed to prevent duplicate scheduling)

**launchd plist:** `~/Library/LaunchAgents/com.myfriendisai.collect-daily.plist`
**Logs:** `logs/collect_daily.log` (rotated to `.prev` each run), `logs/failures.log`

### 4.2 Rate Limiting

- Unauthenticated: ~10 requests/minute → sleep 6+ seconds between requests
- Set User-Agent to something descriptive: `ai-companion-tracker/1.0 (research project)`
- If a request returns 429, back off exponentially (10s, 20s, 40s)
- Comment collection adds ~280 requests/day (272 base + expansion requests)
- Total daily requests: ~360-450 (posts + pagination + keyword scanning + comments)

### 4.3 Infrastructure Requirements

The pipeline runs on a local Mac that must stay available:
- **Sleep:** disabled (`pmset sleep 0`)
- **Auto-restart:** enabled (`pmset autorestart 1`) — recovers from power failure
- **Auto-login:** enabled — launchd user agents don't run until login
- **Auto macOS updates:** disabled — prevents unexpected reboots mid-collection
- **Git remote:** SSH (`git@github.com:hopeshub/myfriendisai.git`) — HTTPS won't auth from launchd
- **SSH key:** `~/.ssh/id_ed25519` (no passphrase, so it works in non-interactive contexts)
- **Vercel CLI:** installed at `/opt/homebrew/bin/vercel`, in PATH for launchd via `run_collect.sh`

**Verify checklist:** `docs/CC_PROMPT_VERIFY_COLLECTION.md`

---

## 5. Frontend (High-Level)

### What the public site shows:

1. **Landing page:** Overview narrative + key trend chart (total engagement across all tracked communities over time)
2. **Trends Explorer:** 6-theme keyword trend chart with toggleable metric cards, absolute/relative mode toggle, nearest-line tooltip, event annotations. Data normalized per-1k-posts. YoY headline uses calendar-day averaging of hitsPerK; changes >100% show actual rates ("rose from X to Y per 1k") instead of percentages to provide base-rate context.
3. **Community explorer:** Browse all 27 tracked subreddits, sortable by engagement metrics, filterable by tier/category
4. **Individual subreddit pages:** Time-series Recharts line charts for subscribers, posts/day, avg comments, avg score
5. **Keyword trends:** Per-theme trend lines waxing and waning across all communities over time

### Tech stack (frontend):
- Next.js 16 (App Router) in `web/` directory
- TypeScript + Tailwind CSS
- Recharts (ComposedChart with per-theme YAxis scaling)
- Server components load + normalize data; client components render charts
- Data reads from `../data/*.json` relative to `web/`

### Design principles:
- Clean, editorial feel (this is a research artifact, not a dashboard)
- Mobile-responsive (single breakpoint at 768px — see below)
- Fast loading (static generation or lightweight API calls)
- No user accounts or interactivity needed

### Mobile responsive (implemented 2026-03-21):
Single breakpoint at **≤768px**. Desktop layout unchanged. Key decisions:
- **Theme cards:** 2x3 grid → horizontal scroll strip with scroll-snap (140px fixed-width cards, ~2.5 visible)
- **Layout reorder:** Methodology note moved below chart on mobile via CSS `order` (chart is primary content)
- **Bottom sheet:** Detail panel renders as a 60dvh bottom sheet (expandable to 90dvh) instead of desktop sidebar. Drag-to-dismiss gesture on handle, backdrop tap-to-close. Uses `dvh` not `vh` for Safari URL bar.
- **Chart:** 8px padding, abbreviated event labels at 640-768px, labels hidden below 640px (expandable list instead)
- **Font floor:** 14px minimum on all text (except chart axis labels)
- **Touch targets:** All buttons ≥44px tap height
- Spec: `docs/archive/MOBILE_RESPONSIVE_SPEC.md`. Implementation prompts: `docs/archive/CC_PROMPT_PHASE{1-4}.md`

---

## 6. Phasing

### Phase 1: MVP — COMPLETE
- [x] Project scaffolding and config files
- [x] Reddit `.json` client with rate limiting
- [x] SQLite database and schema (3.84M posts, FTS5 index)
- [x] Daily collection script for subreddit snapshots + posts
- [x] JSON export pipeline (frontend-ready data)
- [x] Basic validation script (test all subreddits are accessible)
- [x] Cron job setup (local machine runs collection + pushes; GitHub Actions triggers Vercel redeploy on push)
- [x] Basic frontend showing time-series data with raw metrics and simple ratios

### Phase 2: Enhancements — COMPLETE
- [x] Keyword tagging and trend visualizations (6 validated themes, keywords_v8.yaml)
- [x] Historical backfill via PullPush (replaces Arctic Shift — data goes back years)
- [x] Keyword research pipeline (FTS5 + agent-based discovery + precision validation)
- [x] Comment collection + tagging pipeline (forward-looking, implemented 2026-03-18)
- [x] Fix GitHub Actions workflow (Reddit blocks cloud IPs; switched to local collection + GH Actions redeploy-on-push)

### Phase 3: Polish — COMPLETE
- [x] Public deployment to Vercel + myfriendisai.com domain
- [x] Mobile responsive design (horizontal card strip, layout reorder, chart optimization, bottom sheet detail panel)
- [x] SEO and social sharing metadata (OG image, Twitter cards, sitemap, robots.txt)
- [x] Accessibility fixes (focus styles, ARIA attributes, color contrast, focus trap)

### Future work
- Comment keyword precision validation
- Composite "engagement index" scoring (need more daily data)
- Narrative/editorial content
- Export/embed functionality for charts

---

## 7. Open Questions

- **NSFW subreddits:** Reddit blocks NSFW content via `.json` endpoints (403). All 27 currently tracked subreddits are SFW at the subreddit level, so this is not an active issue. If NSFW subs are added in the future, a self-hosted Redlib instance or Arctic Shift archives can provide access.
- **Post-level NSFW:** Individual NSFW posts within accessible subreddits may be filtered from responses, causing slight undercounting. Acceptable for trend analysis.

---

## 8. Key Technical Constraints

1. **No Reddit API credentials required for v1.** The `.json` endpoint approach works without OAuth.
2. **Rate limit: ~10 req/min unauthenticated.** Design collection to stay well under this.
3. **100-post limit per request.** Reddit returns max 100 items per listing. For daily snapshots this is fine; for backfill it means pagination.
4. **~1000-post pagination ceiling.** Reddit's API only lets you paginate through ~1000 posts per subreddit listing. Daily incremental collection avoids this limit.
5. **NSFW subreddits are blocked via `.json` but accessible via Redlib.** Subreddits flagged `over_18: true` return 403 via `.json` endpoints. Solution: route NSFW sub requests through a self-hosted Redlib instance. Arctic Shift archives also include NSFW data for historical backfill. See Section 7 for full analysis.
6. **No real-time data.** Daily snapshots only. The site shows trends, not live stats.

---

