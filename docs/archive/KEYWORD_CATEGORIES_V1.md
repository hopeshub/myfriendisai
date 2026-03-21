# myfriendisai — v1 Keyword Categories

**Updated:** March 11, 2026  
**Purpose:** Defines the keyword categories used for trend tracking on the v1 site. All 15 categories from keywords.yaml are tagged in the backend. This document defines the **8 public-facing themes** and how they map to the underlying data.

---

## Design Principles

1. **Each theme answers a question a normal person would ask.** Not academic categories — questions that a journalist, policymaker, or curious visitor would want to see answered with data.

2. **Keyword reliability matters.** Every category must be defensible: the keywords should be strong proxies for the theme, with low false-positive rates in AI companion communities.

3. **The chart shows discourse volume, not opinion.** We're measuring how often a topic gets discussed, not what people believe. This is an important distinction to communicate on the site.

---

## Aggregation Scope

The v1 chart aggregates keyword hits across ALL tracked subreddits — no tier filtering. The tier structure in communities.yaml is organizational metadata, not a data filter. Tier-based filtering is a v2 feature.

---

## The Eight Themes

### 1. Intimacy
**Question:** "Are people falling in love with AI?"  
**What it tracks:** Romantic and sexual language directed at AI companions.  
**Display name:** Intimacy  
**Color:** `#F97316` (orange)  
**Source categories:** `romantic_language` + `sexual_erotic_language`  
**Reliability:** HIGH

### 2. Attachment
**Question:** "Are people forming real emotional bonds?"  
**What it tracks:** Language describing emotional closeness, missing the AI, feeling genuinely connected.  
**Display name:** Attachment  
**Color:** `#3B82F6` (blue)  
**Source categories:** `attachment_language`  
**Reliability:** MEDIUM-HIGH

### 3. Dependency
**Question:** "Is this addictive?"  
**What it tracks:** Self-reported addiction, compulsive use, AND attempts to quit or reduce use.  
**Display name:** Dependency  
**Color:** `#EF4444` (red)  
**Source categories:** `dependency_language` + `withdrawal_recovery_language`  
**Reliability:** HIGH

### 4. Consciousness
**Question:** "Do people think AI is alive?"  
**What it tracks:** Claims or beliefs about AI having feelings, being sentient, deserving rights.  
**Display name:** Consciousness  
**Color:** `#A855F7` (purple)  
**Source categories:** `sentience_consciousness_language`  
**Reliability:** MEDIUM-HIGH

### 5. Substitution
**Question:** "Is AI replacing human connection?"  
**What it tracks:** Explicit statements about preferring AI to humans.  
**Display name:** Substitution  
**Color:** `#22C55E` (green)  
**Source categories:** `substitution_language`  
**Reliability:** MEDIUM — consider methodology note on site

### 6. Therapy
**Question:** "Are people using AI as a therapist?"  
**What it tracks:** AI described as therapeutic support or therapist replacement.  
**Display name:** Therapy  
**Color:** `#EC4899` (pink)  
**Source categories:** `therapy_language`  
**Reliability:** HIGH

### 7. Memory
**Question:** "Does memory make AI feel more real?"  
**What it tracks:** Discussion of AI remembering or forgetting users, memory as a relationship feature.  
**Display name:** Memory  
**Color:** `#F59E0B` (amber)  
**Source categories:** `memory_continuity_language`  
**Reliability:** HIGH

### 8. Realism
**Question:** "Does AI feel human?"  
**What it tracks:** Language describing AI as human-like, lifelike, or socially present.  
**Display name:** Realism  
**Color:** `#06B6D4` (cyan)  
**Source categories:** `anthropomorphism_realism_language`  
**Reliability:** MEDIUM-HIGH

---

## Categories NOT on the v1 site (still tagged in database)

| Category | Why Not v1 |
|---|---|
| friendship_platonic_language | Too common/noisy |
| positive_experience_language | Generic terms, flat trend line |
| grief_rupture_language | Event-driven — becomes event annotations instead |
| filter_circumvention_language | Niche platform dynamics signal |
| mental_health_language | Too broad, needs more nuanced handling in v2 |

---

## Implementation Notes for CC

### Tagging
- Tag ALL 15 categories from keywords.yaml against every post
- A post can match multiple categories

### Export
- Export daily counts for ALL 15 categories to keyword_trends.json
- Include 7-day rolling averages
- Frontend filters to just these 8 themes

### Frontend merging
- Intimacy = sum of romantic_language + sexual_erotic_language daily counts
- Dependency = sum of dependency_language + withdrawal_recovery_language daily counts
- All other themes map 1:1 to a single backend category

---

## How to Use This Document

1. Location: `~/Projects/myfriendisai/docs/KEYWORD_CATEGORIES_V1.md`
2. For CC: "Read docs/KEYWORD_CATEGORIES_V1.md for category definitions"
3. keywords.yaml remains the source of truth for the tagging pipeline
