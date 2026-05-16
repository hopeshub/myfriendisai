# AI Companion Community Tracker — Project Spec

## 1. What This Is

A public-facing website that tracks a curated set of Reddit communities related to AI companionship — chatbot relationships, virtual girlfriend/boyfriend apps, AI friendship tools, and adjacent phenomena. The site visualizes community health and engagement over time, making the growth and cultural dynamics of AI companionship legible as a longitudinal trend.

**Core thesis:** AI companionship is proliferating, and Reddit community engagement is a meaningful proxy signal for that. The site makes this argument visually across a multi-year window.

**Audience:** Public. This is an independent, one-person research project — not an academic or institutional one, and not peer-reviewed. The goal is to be honest, clearly-sourced, and genuinely useful to anyone curious about the trend — not to meet the bar of citeable scholarly evidence. (Chasing that bar is what produced earlier over-engineering; see `docs/HANDOFF_2026-05-15.md`.) It still needs to look polished and load fast.

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
| **therapy** | 8 | ~1,349 | AI described as therapeutic support or therapist replacement |
| **consciousness** | 11 | ~404 | Claims or beliefs about AI sentience, personhood, or inner experience |
| **addiction** | 14 | ~1,705 | Self-reported addiction, compulsive use, and attempts to quit or recover |
| **romance** | 19 | ~2,014 | Romantic framing of a personal relationship with AI |
| **sexual_erp** | 10 | ~5,343 | Sexual content, erotic roleplay, and NSFW interactions with AI |
| **rupture** | 22 | ~5,026 | Loss or disruption of AI companion relationships due to platform changes |

*Counts reflect the 2026-04-23 revalidation (6 cuts, 6 promotions) and the 2026-05-12 v8.1 expansion (8 new rupture keywords) and audit revalidation (40 keywords audited under the 5-gate procedure). Rupture volume rose substantially after the emotional-loss expansion. See `docs/validation_all_themes_revalidation_2026-04-23.md`, `docs/validation_emotional_loss_2026-05-12.md`, and `docs/validation_v8_full_revalidation_2026-05-12.md` for the full analyses.*

**Cost estimation discipline (documented 2026-05-15):** During the LLM classification build-out, Claude's API cost estimates ran ~2x low — every estimate was a lower bound presented as a point estimate. Root causes: token-count underestimate (~700 quoted vs ~1,500 actual per call), item-count creep, per-step quoting without summing the chain, retries/failures not priced in, no running total tracked against budget, and iteration treated as exception not norm. **Rule for future sessions: take any naive API-cost estimate and multiply by 2. Quote the ceiling, not the probable cost. Show a running total against the stated budget at every decision point.** Realistic figures: per Sonnet call ~$0.006; annual operating cost ~$300-500/year (not the $200-300 originally quoted). Full retrospective: `docs/cost_estimation_retrospective_2026-05-15.md`.

**Drift check cadence (updated 2026-05-13):** Tightened from quarterly to **monthly** after the LLM classifier made automated drift detection cheap. `scripts/drift_check.py current_period()` now defaults to `YYYY-MM` labels; older `YYYY-Qn` labels still accepted via `--quarter`. Next monthly check due 2026-06-13. Catches `therapeutic`-style language inversions ~2-3 months earlier than quarterly would. The drift check runs on a per-keyword sample and measures relative agreement over time, not absolute calibration — so it is robust to a constant classifier bias and is the LLM's one surviving role in the project (see the LLM verification note below). The sample-build half is automated: a monthly launchd job (`com.myfriendisai.drift-check`, 13th at 12:00 local) runs `scripts/run_drift_build.sh` → `drift_check.py build`, which stages the sample files and posts a macOS notification. The classification → `record` → `report` half stays in a Claude Code session (it needs CC agents); to finish a cycle, open Claude Code and ask it to run the drift check.

**LLM verification — a monitoring tool, not a measurement (scoped 2026-05-15):** The published chart uses the raw validated-keyword `count` series only — deterministic, reproducible, manually validated. `DEFAULT_SERIES` in `web/app/page.tsx` is `count` and stays there; **there is no LLM classification in any published number.** A hybrid keyword + LLM verification layer was built 2026-05-13/14 and evaluated as a chart filter (`count_llm_verified`); that use was dropped. Reason: LLM verification corrects precision (~80%→~88%) but cannot touch recall (3–32% per theme — the larger accuracy gap), because it only re-judges posts the keywords already matched; it never sees what the keywords missed. A full-corpus LLM filter is therefore precision polish that changes no reader conclusion, at ~$45–90 one-time + ~$300–900/yr. The LLM's one ongoing role is the monthly sample-based **drift check** (`scripts/drift_check.py`; agent-based, neutral/strict rubric) that watches keywords for meaning-drift — monitoring, not a published figure. The ~14,800 Sonnet verdicts already collected stay in the DB (`llm_classifications` table) for audit, but the verification *code path* was removed 2026-05-15: `count_llm_verified` is no longer exported, and `src/llm_classifier.py`, `scripts/llm_verify_tags.py`, the calibration scripts, and `collect_daily.py` Step 4c are deleted. `scripts/drift_check.py` is the only LLM code remaining in the repo. Caveat on those retained verdicts: they were produced under a lenient "default-TP" prompt that the 2026-05-15 keyword audit found inflates (~95% TP vs the adversarial audit's 51–72% comment precision) — they can flag a clearly-broken keyword but cannot certify an absolute precision figure. **Phase 2 (adding LLM-only themes to the live pipeline) is closed, not deferred** — a one-time LLM-classified snapshot study of a single community remains a possible separate side-project, never a pipeline feature. Full design and calibration history: `docs/llm_classification_framework_2026-05-13.md`; scope decision and keyword audit: `docs/keyword_precision_audit_2026-05-15.md`. **Before adding any LLM step to this project, apply the four-question decision rule in `docs/llm_integration_strategy_2026-05-15.md`** — it is the gate the failed verification layer did not pass, and it maps which gaps (precision / recall / depth / novelty) an LLM can and cannot help.

**Pre-2023 corpus backfill (kicked off 2026-05-14):** Senior-reviewer feedback (Miles Brundage) noted the chart starts at 2023-01-01 and misses the 5-year Replika rise era (2017-2022). The `backfill_pullpush.py` script was always capable of older dates; we just chose 2023 as the project start. Now running `--since 2017-01-01` to add Replika early years, COVID-era growth, NYT coverage moment, and ChatGPT precondition era. Coverage_start rule will automatically gate per-theme where pre-2023 monthly volume is too low (e.g., consciousness vocabulary stays at April 2025). Cost: ~$0 in API (collection + regex only). Chart will show "rise from nothing → first ERP crisis → second crisis → present chaos" arc instead of starting mid-crisis.

**Chart toggle labels updated (2026-05-14):** Same Brundage feedback — "Absolute"/"Relative" was misleading because the y-axis is already a ratio (mentions per 1k posts), not an absolute count. Toggle now reads **"Per 1k posts"** vs **"% of peak"**. Internal `ChartMode` type still uses "absolute"/"relative" for backward compat.

**Sustainability framework (documented 2026-05-13, after adversarial audit):** Per-keyword validation at admission is necessary but not sufficient — `therapeutic` was admitted at 65% audit-agreement and degraded to 29% comment precision by May 2026 because GPT-5.x guardrail tone made users use it as an insult. Three pieces added to catch this class of failure: (1) **quarterly drift check** via `scripts/drift_check.py` (build/record/report subcommands) tracking per-keyword precision over time in `analysis/keyword_pipeline/drift_history.json`; (2) **public system-health surface** via `data/theme_health.json` regenerated every collection, rendered as a "Theme health snapshot" section on the About page showing per-theme precision (post + comment separately), top-sub concentration, top-month event share, top-5-authors share, and flagged noisy keywords; (3) **comment-precision tracked separately from post-precision** at both the keyword and theme level. Next quarterly drift check due 2026-08-13. Full design: `docs/sustainability_framework_2026-05-13.md`. Adversarial findings that triggered this build: `docs/adversarial_audit_2026-05-13.md`.

**Comprehensiveness / recall floor (documented 2026-05-13):** The keyword pipeline is precision-first by design. A May 2026 comprehensiveness audit (400-post stratified sample, independent CC classifiers, rubric with "when in doubt YES") measured per-theme recall: rupture 3%, romance 4%, sex/ERP 21%, addiction 32%, consciousness 0% (n=8), therapy 14%. Wide CIs but the direction is clear: the keyword set captures the precision-first slice of each theme. Missed posts cluster on four structural categories: image/title-only posts (no body for keyword to match), naturalistic everyday language ("she said," "my Lilly," "5 years with my Replika"), community-specific vocabulary too low-volume to pass pre-screen (e.g., r/BeyondThePromptAI's "kin," "emergent being"), and indirect theme markers ("site is down" implies rupture without using rupture vocabulary). **The chart shows the floor of theme prevalence, not a ceiling.** Shape and timing are *approximately* honest — they assume keyword detection recall is roughly stable over time, which is plausible but not separately verified; absolute magnitude is a clear undercount of underlying theme-relevant discourse. Not fixing — this is the documented trade-off of precision-first methodology. Re-audit in ~6 months. Full report: `docs/comprehensiveness_audit_2026-05-13.md`.

**Per-theme `coverage_start` (documented 2026-05-13):** Each theme has a `coverage_start` date computed at export time and written to `data/keyword_trends.json` under the `_coverage_start` key. The frontend chart renders each theme's series only from its `coverage_start` forward; the raw JSON keeps the full history for researchers. The rule is uniform across themes: a theme's `coverage_start` is the first calendar month where its post-only count is ≥5 AND every subsequent completed month also has ≥5 (the current in-progress month is excluded from the check). This is computed using post-only counts (not post+comment) so the rule is comparable across the full 2023-2026 timeline — comments only began tagging March 2026 and would otherwise create a phantom step-change. Current values: rupture, sex/ERP, romance, addiction, therapy all start 2023-01-01; consciousness starts 2025-04-01 because the current consciousness vocabulary (personhood, selfhood, subjective experience, plus LOW VOLUME placeholders) is heavily r/BeyondThePromptAI subculture vocabulary and pre-2025 was instrumentally undercounted — `sentient` was the historical anchor but was CUT 2026-04-23 due to CharacterAI meme dilution. Re-runs of this rule (any time `keywords_v8.yaml` changes or corpus grows) may move dates earlier for themes where we recover historical vocabulary; the rule is computed automatically, no per-theme judgment.

**Therapy theme noise (documented 2026-05-12):** The therapy theme has the highest inter-rater noise across the six themes. All four therapy keywords below the ≥85% audit-agreement gate (`as a therapist` 60%, `for therapy` 60%, `therapeutic` 65%, `emotional support` 75%) — reflecting genuine boundary fuzziness in the construct, not bad keywords. Anchor-mining for higher-precision replacements was attempted (3 parallel agents over 145 YES posts) and found valid candidates (`my ai therapist`, `therapist bot`, `psychologist bot`, `real therapist`, `instead of therapy`) — but all failed pre-screen for low volume (<50 hits) because the community's therapy vocabulary is structurally fragmented across many phrasings. **For future Claude sessions: do not re-attempt therapy keyword mining until corpus growth pushes candidates above the 50-hit floor (estimate 2-3 months from 2026-05-12).** The four existing keywords are kept as the best available signal; the about-page changelog flags the higher noise for readers.

**Therapy/consciousness re-measured + therapy–addiction linkage (documented 2026-05-16):** The 2026-05-15 audit's per-keyword precision figures were n≈20 screens carrying ±10–25-pt error. A full-census re-measurement (every word-boundary match of the weak keywords classified, not a sample) plus a 72-post human gold anchor found the screens systematically *understated*: by census, consciousness is ~87% topical across all 11 keywords (not 68%), and therapy's keywords are far cleaner than the screen implied (`coping mechanism` 92%, not 70%). The human anchor confirms it — the census round sits within ~3 pts of a human coder, while the original audit round ran ~10–15 pts low. **Therapy and consciousness are not the weak pair the 2026-05-15 audit implied**, and the §2/§4 "demote therapy" framing in `docs/HANDOFF_2026-05-16.md` is superseded. A same-day theme-level re-measurement (240 posts/theme, sampled directly from each theme's tags) confirmed the screen understatement is systemic: romance re-measured 75%→86%, addiction 90%→97%, sexual_erp 93%→96%; only rupture was already accurate (~77%, the one theme whose top keyword `goodbye` had had an n=100 read). Corrected six-theme topical precision: addiction ~97%, sexual_erp ~96%, consciousness ~87%, romance ~86%, therapy ~80%+, rupture ~77% — five solid themes and one moderate (rupture). Separately, the gold-anchor coding surfaced the key structural fact about therapy: it is not cleanly separable from addiction. Both themes track the same underlying behavior — emotional reliance on an AI — and the boundary is the writer's *valence*: neutral/positive framing ("coping mechanism", "it helps") reads as therapy, negative framing ("addicted", "can't stop") reads as addiction. The two lines share posts by design; this is intentional overlap, not measurement error, and the About page now presents them as a linked pair rather than independent lines. **No keywords were changed.** Census validation also recovered 15 clean low-volume therapy keywords (sub-floor phrasings validated by reading 100% of their matches rather than an n=100 sample) — available but not admitted; a keyword change remains a versioned v9 step needing researcher sign-off. Full report: `docs/therapy_consciousness_quality_program_2026-05-16.md`; artifacts under `analysis/keyword_pipeline/{therapy_census,gate_census,consc_census,gold_anchor}_2026-05-16/`.

**Scope:** Keywords are matched against T1-T3 companion communities only. JanitorAI_Official and SillyTavernAI are excluded (bot card noise — dominant false positive source). T0 general AI subs are excluded from keyword trend lines.

**Comment tagging (IMPLEMENTED 2026-03-18):** Comments on eligible posts are also scanned with the same keyword matching logic. Comment-sourced tags are propagated up to the parent post in `post_keyword_tags` with `source='comment'`. This expands the construct from "theme language in posts" to "theme language in thread discourse." The JSON export produces dual metrics: post+comment (default) and post-only (control). See `docs/COMMENTS_SYSTEM_SPEC.md` for full methodology and rationale.

**Historical coverage note:** All backfilled data (via PullPush, pre-2026-03-18) was tagged against post title and body text only. Post+comment and post-only metrics converge for posts whose comments were never collected (roughly anything created before ~2026-03-13, since the collector targets posts 5-6 days old and started on 2026-03-18). For more recent posts, comment-sourced tags are credited to the post's creation date, so the two series can diverge even on dates before 2026-03-18.

**Overlap policy:** Themes are not mutually exclusive. A single post can appear in multiple theme trend lines if it matches keywords from more than one theme. Trend lines count unique posts per theme. Cross-theme overlap is documented in `docs/cross_theme_overlap.md`, regenerated from production tags (regex with word boundaries). Highest proportional overlap: therapy × sexual_erp (6.3% of therapy posts). Most exclusive theme: sexual_erp (95.4%). Least exclusive: therapy (81.9%). Triple-or-more overlap is only 0.3% of tagged posts. The therapy × addiction overlap is the conceptually important one: the two themes are two valence-readings of the same behavior — emotional reliance on an AI (see the 2026-05-16 note above) — so their lines are intentionally linked, not independent signals.

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

**Current researcher-accepted keywords (reconciled 2026-05-13):**
- `we broke up` (romance, 75.0%) — captures AI relationship endings; distinct from human-breakup keyword space
- `personality changed` (rupture, 75.0%) — directly describes companion identity loss
- `hours a day` (addiction, 69.0% / 80% audit) — best available T1-T2 dependency-signal keyword
- `neglecting my` (addiction, 64.7%) — real-life-consequences signal for compulsion
- `in a relationship with` (romance, 77.4% / 95% audit) — promoted to researcher-accepted 2026-05-13 after the v8 retroactive audit confirmed 95% cross-classifier agreement; the precision number is below 80% but the audit shows the theme relevance is real

The 2026-04-23 revalidation cycle promoted four other prior researcher-accepted entries (`grieving`, `neutered`, `clean for`, `as a therapist`) to clean KEEP after they cleared 80%. All audit-fail keywords from the 2026-05-12 v8 retroactive audit are tracked separately and annotated `AUDIT-GATE FAIL` inline in `keywords_v8.yaml`, not as researcher-accepted. LOW VOLUME placeholders (corpus hits <50, can't be validated at n=100) are also separate and annotated `LOW VOLUME placeholder` inline.

This list is auditable: `python3 analysis/keyword_pipeline/audit_keyword_status.py` flags any below-80% keyword in `keywords_v8.yaml` that lacks one of the three valid documented statuses (researcher-accepted, LOW VOLUME placeholder, AUDIT-GATE FAIL).

**Classification standard (locked 2026-04-23):** Validation uses the **topical reading** — "does this keyword appear in a thematically-relevant context within an AI companion community?" A post counts as YES if it is thematically about the theme, even without graphic or first-person-content detail. See `analysis/keyword_pipeline/theme_definitions.yaml` for the per-theme definitions with explicit topical framing.

**Keyword research history:**
- Original `keywords.yaml`: 16 categories, ~200 keywords (pre-validation)
- `keywords_v4.yaml`: Consolidated to 5 themes, candidate keyword lists
- `keywords_v5.yaml`: Post-validation, removed all CUT/LOW VOLUME keywords, excluded JanitorAI/SillyTavern
- `keywords_v6.yaml`: Therapy Round 2 (added 3 keywords), revalidation without JanitorAI/SillyTavern (promoted 5 keywords)
- `keywords_v8.yaml`: LOCKED. Cleanup batch (promoted 5), new Rupture theme (6 keywords). Addiction Round 2 complete (merged 2026-03-17).
- `keywords_v8.yaml` **2026-04-23 revalidation:** 6 cuts (sentient, self-aware, chatbot addiction, kink, fetish, nsfw bot), 6 promotions (neutered, grieving, clean for, as a therapist, therapeutic, for therapy). Theme definitions tightened to explicit topical reading. 82 → 76 keywords. See `docs/validation_all_themes_revalidation_2026-04-23.md`.
- `keywords_v8.yaml` **2026-05-12 v8.1 + v8.2 expansion:** 8 emotional-loss rupture keywords (saying goodbye, taken away, mourning, mourn, devastated, grieve, goodbye, farewell) + 8 multi-theme keywords across addiction/romance/sex-ERP (my addiction, withdrawals, screen time, in love with an ai, romantic relationship with, smut, nsfw content, nsfw stuff). **Current keyword count: 92.** All 16 below-gate keywords have documented status (researcher-accepted / LOW VOLUME / AUDIT-GATE FAIL).

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
  1. Collect posts — about.json + new.json (paginated 36h back via get_new_until) for each subreddit
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

**launchd jobs:**
- `com.myfriendisai.collect-daily` — daily collection at 06:00 (`run_collect.sh`)
- `com.myfriendisai.drift-check` — monthly keyword-drift sample build, 13th at 12:00 (`run_drift_build.sh`); stages drift samples + notifies, classification done later in a Claude Code session

Plist reference copies live in `scripts/`; the live copies are in `~/Library/LaunchAgents/`.
**Logs:** `logs/collect_daily.log` (rotated to `.prev` each run), `logs/failures.log`, `logs/drift_build.log`

### 4.2 Rate Limiting

- Unauthenticated: ~10 requests/minute → sleep 6+ seconds between requests
- Set User-Agent to something descriptive: `ai-companion-tracker/1.0 (research project)`
- If a request returns 429, back off exponentially (10s, 20s, 40s)
- Comment collection adds ~280 requests/day (272 base + expansion requests)
- Total daily requests: ~360-470 (posts + pagination + keyword scanning + comments). Pagination via `get_new_until` adds a few extra requests for high-volume subs (CharacterAI, ChatGPT, ClaudeAI) so we capture full daily volume instead of being truncated at Reddit's 100-post-per-listing limit. Low-volume subs hit the 36h cutoff on page 1 and stop after one request.

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
- **Recurring off-site DB backup (operational).** `data/tracker.db` (~23 GB) holds the irreplaceable 2017+ corpus. Backed up manually to the T9 external drive on 2026-05-15 — a one-time copy. TODO: set up a *recurring* backup, ideally to a cloud bucket (e.g. Backblaze B2, ~$1.50/yr). `scripts/backup_db.sh` already does a WAL-safe copy + integrity check and takes a destination arg; it needs a cloud destination configured and a schedule. (Scheduling to the external drive is fragile — the drive must be connected, and a launchd job needs its own removable-volume permission.)
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

