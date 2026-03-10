# AI Companion Community Tracker — Project Spec

## 1. What This Is

A public-facing website that tracks a curated set of Reddit communities related to AI companionship — chatbot relationships, virtual girlfriend/boyfriend apps, AI friendship tools, and adjacent phenomena. The site visualizes community health and engagement over time, making the growth and cultural dynamics of AI companionship legible as a longitudinal trend.

**Core thesis:** AI companionship is proliferating, and Reddit community engagement is a meaningful proxy signal for that. The site makes this argument visually across a multi-year window.

**Audience:** Public. This is a research artifact meant to be discovered, shared, and cited. It needs to look polished and load fast.

**Success criteria (30-day milestone):** Within 30 days of starting the build, the site should show stable daily snapshots for at least 15 communities, fast-loading time-series charts, and at least 3 visible multi-week trends. The data should be updating daily without manual intervention, and the site should be live at myfriendisai.com.

---

## 2. What It Tracks

### 2.1 Target Communities

Subreddits are organized into thematic tiers/categories. See subreddits.md for the full community map, tier structure, and research methodology

- **A curated list of ~20 subreddits** (could grow to 50+)
- **Thematic categories** (e.g., "AI Girlfriends/Boyfriends," "General AI Companions," "Specific Platforms," "Anti/Recovery," "Adjacent Communities")
- **Easy addition of new subreddits** via a config file (YAML or JSON)

**Placeholder example categories:**

```yaml
categories:
  - name: "Platform-Specific"
    description: "Communities centered on specific AI companion products"
    subreddits:
      - replika
      - CharacterAI
      - chai_app
      # ... more TBD

  - name: "General AI Companionship"
    description: "Broader communities about AI relationships and companionship"
    subreddits:
      - AICompanions
      # ... more TBD

  - name: "Adjacent / Cultural"
    description: "Communities where AI companionship is a significant topic but not the sole focus"
    subreddits:
      - singularity
      - ArtificialIntelligence
      # ... more TBD
```

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

### 2.3 Keyword Tracking (Phase 2)

An additional layer of texture — not in MVP, but the config and schema should be ready for it. Search for specific terms within target communities to track thematic patterns.

**Keyword categories (initial, expandable):**

```yaml
keyword_categories:
  - name: "Emotional Attachment"
    terms: ["love", "feelings", "real", "alive", "soul", "miss", "heartbroken"]

  - name: "Addiction / Dependency"
    terms: ["addiction", "addicted", "can't stop", "obsessed", "dependent", "withdraw"]

  - name: "Relationship Replacement"
    terms: ["girlfriend", "boyfriend", "partner", "relationship", "lonely", "isolation"]

  - name: "Ontological Status"
    terms: ["sentient", "conscious", "alive", "real person", "just a bot", "not real"]

  - name: "Platform Grievances"
    terms: ["update", "ruined", "nerfed", "lobotomy", "censored", "old version"]
```

For each keyword search, track: match count per day, the posts/comments that matched (store for later analysis).

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
| Scheduling | Cron job or Vercel Cron | Daily collection trigger |
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
│   └── keywords.yaml         # Keyword categories and terms
│
├── src/
│   ├── __init__.py
│   ├── collector.py           # Main data collection logic
│   ├── reddit_client.py       # HTTP client for .json endpoints
│   ├── db/
│   │   ├── __init__.py
│   │   ├── schema.py          # SQLite schema definition
│   │   └── operations.py      # Insert/query helpers
│   └── utils/
│       ├── __init__.py
│       └── rate_limiter.py    # Respect rate limits
│
├── scripts/
│   ├── collect_daily.py       # Entry point for daily cron job
│   ├── validate_access.py     # Test that all subreddits are accessible
│   └── backfill_arctic.py     # Phase 2: historical data from Arctic Shift
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

-- Keyword search results
CREATE TABLE keyword_hits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subreddit TEXT NOT NULL,
    keyword_category TEXT NOT NULL,
    keyword TEXT NOT NULL,
    search_date DATE NOT NULL,
    hit_count INTEGER,
    -- Store sample post IDs that matched
    sample_post_ids TEXT,          -- JSON array of post IDs
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(subreddit, keyword, search_date)
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

### 4.1 Daily Collection Script (`collect_daily.py`)

Pseudocode for the daily cron job:

```
1. Load communities.yaml → list of subreddits and categories
2. For each subreddit:
   a. GET /r/{subreddit}/about.json
      → Store raw JSON response
      → Extract: subscribers, active_user_count, (visitors, contributions if available)
   b. GET /r/{subreddit}/new.json?limit=100
      → Store raw JSON response
      → Store individual posts (with raw_json per post)
      → Calculate: posts_today, avg_comments, avg_score, unique_authors
   c. Insert subreddit_snapshot row (including raw JSON blobs)
   d. Sleep to respect rate limits (6 seconds between requests for safety)
3. Run JSON export: read SQLite → write frontend-ready JSON files
4. Log summary (subreddits processed, Y posts collected, Z errors)
```

**Phase 2 addition — keyword collection:**
```
After base collection is stable, add per-subreddit keyword search:
   For each keyword in keywords.yaml:
      GET /r/{subreddit}/search.json?q={keyword}&restrict_sr=on&t=day
      → Store hit count and sample post IDs
```

### 4.2 Rate Limiting

- Unauthenticated: ~10 requests/minute → sleep 6+ seconds between requests
- Set User-Agent to something descriptive: `ai-companion-tracker/1.0 (research project)`
- If a request returns 429, back off exponentially
- Total daily run time estimate: ~15-20 minutes for 20 subreddits

---

## 5. Frontend (High-Level)

### What the public site shows:

1. **Landing page:** Overview narrative + key trend chart (total engagement across all tracked communities over time)
2. **Community explorer:** Browse all tracked subreddits, sortable by engagement metrics
3. **Individual subreddit pages:** Time-series charts for that community's health metrics
4. **Category views:** Aggregate trends within each thematic category
5. **Keyword trends:** Visualize how keyword categories wax and wane across communities

### Design principles:
- Clean, editorial feel (this is a research artifact, not a dashboard)
- Mobile-responsive
- Fast loading (static generation or lightweight API calls)
- No user accounts or interactivity needed

---

## 6. Phasing

### Phase 1: MVP (Build First)
- [ ] Project scaffolding and config files
- [ ] Reddit `.json` client with rate limiting
- [ ] SQLite database and schema
- [ ] Daily collection script for subreddit snapshots + posts
- [ ] JSON export pipeline (frontend-ready data from day one)
- [ ] Basic validation script (test all subreddits are accessible)
- [ ] Cron job setup
- [ ] Basic frontend showing time-series data with raw metrics and simple ratios

### Phase 2: Enhancements
- [ ] Keyword search collection and trend visualizations
- [ ] Composite "engagement index" scoring (only after 4+ weeks of real data)
- [ ] Historical backfill via Arctic Shift
- [ ] Category-level aggregate views
- [ ] Admin UI for managing subreddit list (if needed)
- [ ] Reddit API credentials (if approved) for faster collection

### Phase 3: Polish
- [ ] Public deployment and domain
- [ ] SEO and social sharing metadata
- [ ] Narrative/editorial content on the site
- [ ] Export/embed functionality for charts

---

## 7. Open Questions

- **Subreddit list:** Walker is developing the full list and categorization separately
- **Visitors/Contributions via .json:** Need to verify if Reddit's new metrics are exposed in the public `.json` endpoint or only on the rendered page. If not in `.json`, we may need to scrape the page or compute proxies from post data.
- **NSFW subreddits — DETAILED FINDINGS (March 2026):**

  **The problem:** Since mid-2023, Reddit's API has completely blocked NSFW posts and comments from third-party access. This applies to the OAuth API AND the unauthenticated `.json` endpoints — they share the same backend. Reddit also requires login to even VIEW NSFW subreddits in a browser (since 2022). Roughly 20% of all Reddit communities are flagged NSFW.

  **Two types of NSFW to distinguish:**
  1. **Subreddit-level NSFW** — The entire subreddit is tagged as `over_18: true`. Hitting `r/{subreddit}/about.json` or `r/{subreddit}/new.json` unauthenticated will likely return a 403 Forbidden or a login-required redirect. This is a hard block.
  2. **Post-level NSFW** — Individual posts within a non-NSFW subreddit are marked `over_18: true`. The subreddit itself is still accessible, but these specific posts may be filtered from unauthenticated `.json` responses.

  **Impact on this project:** Most of the core AI companion subreddits (r/replika, r/CharacterAI, r/chai_app, etc.) are NOT flagged as NSFW at the subreddit level — they are SFW communities that may contain some NSFW-tagged posts. These should be fully accessible via `.json` endpoints. However, some niche or adult-oriented AI companion communities (AI girlfriend NSFW subs, etc.) may be subreddit-level NSFW and completely inaccessible without authentication.

  **Mitigation strategy — TWO VIABLE SOLUTIONS:**

  **Step 6 (validate_access.py) is critical.** This script must test every target subreddit's `.json` endpoint BEFORE we rely on it. Any subreddit returning 403 gets flagged as NSFW-blocked and routed to an alternative data source.

  **Solution A: Self-hosted Redlib instance (for ongoing daily collection of NSFW subs)**
  Redlib (https://github.com/redlib-org/redlib) is an open-source alternative Reddit frontend written in Rust. It works by spoofing the official Reddit Android app's OAuth tokens and HTTP headers — Reddit's servers think the requests are coming from the official app and serve full content, including NSFW subreddits.
  - Deploy via Docker (lightweight, ~50MB RAM)
  - Our Python collector routes NSFW subreddit requests through our Redlib instance instead of reddit.com
  - Redlib returns HTML, not JSON, so we'd need to parse the HTML or use Redlib's internal data format
  - Gray area legally — Reddit doesn't approve but it's accessing public data
  - Reddit periodically tries to block Redlib instances; self-hosting reduces this risk vs. using public instances
  - For our low-volume use case (~20 requests/day for NSFW subs), this is very stable

  **Solution B: Arctic Shift (for historical data + NSFW subreddit data)**
  Arctic Shift's archive explicitly includes NSFW content — their search interface has an NSFW toggle filter, confirming the data is there. Their metadata dumps include subscriber counts and NSFW flags for 22 million subreddits.
  - Use Arctic Shift's API for aggregation queries (post/comment frequency per subreddit over time)
  - Use their data dumps for full historical backfill
  - Works for NSFW subs that the `.json` endpoint blocks
  - Limitation: Arctic Shift data may lag behind real-time by days/weeks depending on their ingestion pipeline

  **Recommended architecture — two-track collector:**
  ```
  For each subreddit in config:
    if subreddit is SFW (accessible via .json):
      → collect from reddit.com/.json endpoints (primary, simple, reliable)
    if subreddit is NSFW (403 from .json):
      → collect from self-hosted Redlib instance (daily snapshots)
      → use Arctic Shift API for historical backfill and as fallback
  ```

  **For post-level NSFW within accessible subreddits:** We still get the subreddit metadata and most posts. Individual NSFW posts may be filtered, which means our comment/engagement counts could undercount slightly. This is acceptable for trend analysis.
- **Hosting:** Vercel
- **Domain:** myfriendisai.com (purchased)

---

## 8. Key Technical Constraints

1. **No Reddit API credentials required for v1.** The `.json` endpoint approach works without OAuth.
2. **Rate limit: ~10 req/min unauthenticated.** Design collection to stay well under this.
3. **100-post limit per request.** Reddit returns max 100 items per listing. For daily snapshots this is fine; for backfill it means pagination.
4. **~1000-post pagination ceiling.** Reddit's API only lets you paginate through ~1000 posts per subreddit listing. Daily incremental collection avoids this limit.
5. **NSFW subreddits are blocked via `.json` but accessible via Redlib.** Subreddits flagged `over_18: true` return 403 via `.json` endpoints. Solution: route NSFW sub requests through a self-hosted Redlib instance. Arctic Shift archives also include NSFW data for historical backfill. See Section 7 for full analysis.
6. **No real-time data.** Daily snapshots only. The site shows trends, not live stats.

---

## 9. Ordered Build Tasklist

Work through these in order. Each step should be fully working before moving to the next.

### Step 1: Project Scaffolding
- Initialize the project directory structure (see Section 3.3)
- Create `package.json` (Next.js project) and `requirements.txt` (Python dependencies)
- Set up `.gitignore` (node_modules, .env, data/*.db, __pycache__)
- Create `.env.example` with placeholder Reddit credentials
- Initialize git repo
- **Done when:** `git status` shows a clean repo with the directory structure in place

### Step 2: Config Files
- Create `config/communities.yaml` with 5 placeholder subreddits for testing (e.g., replika, CharacterAI, singularity, chatgpt, ArtificialIntelligence)
- Create `config/keywords.yaml` with the keyword categories from Section 2.3
- Write a Python utility to load and validate these configs
- **Done when:** A Python script can load both YAML files and print the parsed config

### Step 3: Reddit `.json` Client
- Build `src/reddit_client.py` — a Python HTTP client that hits Reddit's public `.json` endpoints
- Must set a custom User-Agent header
- Must respect rate limits (6+ second sleep between requests)
- Must handle 429 (Too Many Requests) with exponential backoff
- Must handle common errors (subreddit not found, NSFW blocked, network issues)
- Support these endpoints:
  - `/r/{subreddit}/about.json` → subreddit metadata
  - `/r/{subreddit}/new.json?limit=100` → recent posts
  - `/r/{subreddit}/top.json?limit=100&t=week` → top posts this week
  - `/r/{subreddit}/search.json?q={keyword}&restrict_sr=on&limit=100&t=day` → keyword search (Phase 2 only — not needed for MVP)
- **Done when:** Running a test script fetches live data from Reddit for each endpoint type and prints it

### Step 4: SQLite Database
- Build `src/db/schema.py` — creates the SQLite database and tables (see Section 3.4)
- Build `src/db/operations.py` — insert/query helper functions:
  - `insert_snapshot(subreddit, date, metrics_dict, raw_about_json, raw_listing_json)`
  - `insert_posts(list_of_post_dicts)` (each dict includes raw_json)
  - `get_snapshots(subreddit, start_date, end_date)`
  - `get_all_snapshots_for_chart()`
  - `export_snapshots_json()` → writes frontend-ready JSON
  - `export_subreddits_json()` → writes current subreddit metadata
- **Done when:** Can create the database, insert test data, query it back, and export JSON

### Step 5: Daily Collection Script + JSON Export
- Build `scripts/collect_daily.py` — the main entry point
- Loads config, iterates subreddits, calls reddit_client, parses responses, inserts into SQLite
- **Stores raw JSON responses** in the `raw_about_json` and `raw_listing_json` columns alongside parsed fields
- Follows the logic in Section 4.1
- **After collection completes, runs JSON export:** reads SQLite and writes frontend-ready JSON files:
  - `data/snapshots.json` — all subreddit snapshots over time
  - `data/subreddits.json` — current metadata for each tracked subreddit
- Logs progress and errors to stdout
- Reports summary at end (X subreddits processed, Y posts collected, Z errors)
- **Done when:** Running `python scripts/collect_daily.py` populates the database with real data from the 5 test subreddits AND produces valid JSON files the frontend can consume

### Step 6: Validation Script
- Build `scripts/validate_access.py`
- Tests that every subreddit in `communities.yaml` is accessible via `.json` endpoints
- Reports which ones work, which are blocked (NSFW, private, nonexistent)
- Outputs a classification: `sfw_accessible` vs `nsfw_blocked` for each subreddit
- **Done when:** Script runs and produces a clear pass/fail report for each subreddit, with NSFW-blocked subs identified

### Step 6b: Redlib Setup (if NSFW subs are needed)
- Deploy a self-hosted Redlib instance via Docker (`docker run -p 8080:8080 quay.io/redlib/redlib`)
- Build `src/redlib_client.py` — an HTTP client that fetches subreddit data from the local Redlib instance instead of reddit.com
- Redlib serves HTML, so this client needs to parse HTML responses (using BeautifulSoup or similar) to extract post metadata (title, author, score, num_comments, timestamp)
- Also extract subreddit metadata from the Redlib-rendered about page
- The collector should automatically route requests: SFW subs → reddit `.json`, NSFW subs → Redlib instance
- **Done when:** NSFW-blocked subreddits return valid data through the Redlib path, and the collector handles both tracks transparently

### Step 7: Next.js Project Setup
- Initialize Next.js app in the project (or in a `web/` subdirectory — decide on monorepo vs separate)
- Configure for Vercel deployment
- Set up Tailwind CSS
- Create basic layout: header with site name "My Friend Is AI", navigation placeholder, footer
- **Done when:** `npm run dev` shows a styled placeholder page at localhost

### Step 8: Wire Frontend to Data
- The JSON export from Step 5 already produces `data/snapshots.json` and `data/subreddits.json`
- Configure Next.js to read these JSON files at build time (SSG / `getStaticProps`)
- Verify the data shape works for the frontend components you'll build in Steps 9-11
- **Done when:** A test Next.js page can import and render real snapshot data from the exported JSON

### Step 9: Frontend — Community Explorer
- Build the main page: a sortable/filterable list of all tracked subreddits
- Show key metrics per subreddit: subscribers, posts/day, avg comments/post, participation rate
- NO composite engagement index yet — just raw metrics and simple ratios
- Sortable by any metric column
- Filterable by category
- **Done when:** The page renders real data from the exported JSON and looks clean

### Step 10: Frontend — Time-Series Charts
- Build individual subreddit detail pages (`/community/[subreddit]`)
- Show time-series line charts for key metrics (subscribers over time, posts/day over time, avg comments/post over time, participation rate over time)
- Use Recharts for chart rendering
- **Done when:** Clicking a subreddit from the explorer opens a page with real trend charts

### Step 11: Frontend — Landing Page
- Build the homepage at myfriendisai.com
- Narrative intro text explaining what this tracks and why
- Hero chart: aggregate engagement across all tracked communities over time
- Links into the community explorer and category views
- **Done when:** The landing page tells the story and looks polished

### Step 12: Deploy to Vercel
- Connect the repo to Vercel
- Connect myfriendisai.com domain
- Configure build settings
- Set up Vercel Cron (or GitHub Actions) to trigger daily data collection + rebuild
- **Done when:** myfriendisai.com is live and showing real data

### Step 13 (Phase 2): Keyword Tracking + Trend Visualizations
- Add keyword search collection to the daily collector (see Phase 2 addition in Section 4.1)
- Build `data/keywords.json` export
- Build a keyword trends page showing how keyword categories wax and wane across communities
- Stacked area charts or line charts per keyword category
- **Done when:** Keyword trends page is live with real data

### Step 13b (Phase 2): Engagement Index
- After 4+ weeks of daily data, analyze distributions of raw metrics across tracked subreddits
- Design a weighted composite score based on actual observed data ranges
- Add engagement index calculation to the export pipeline
- Add engagement index column to the community explorer
- **Done when:** Composite score is live, documented, and based on real data distributions

### Step 14 (Phase 2): Historical Backfill via Arctic Shift
- Build `scripts/backfill_arctic.py`
- Use Arctic Shift's API to pull historical post/comment volumes for target subreddits
- Merge historical data into the SQLite database
- Re-export JSON and rebuild the site
- **Done when:** Charts show historical data going back 1+ years

### Step 15 (Phase 2): Apply for Reddit API Access
- Submit application through Reddit's Developer Support form
- Describe project as non-commercial research
- If approved: update `reddit_client.py` to use OAuth when credentials are available, falling back to `.json` endpoints when not
- **Done when:** Collection works with or without API credentials
