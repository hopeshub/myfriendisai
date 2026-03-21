# Data Integrity Audit Results
**Date:** 2026-03-15
**DB:** data/tracker.db (3.26M posts)

---

## AUDIT 1: Subreddit Contamination — FAIL

### 1a. Subreddits in post_keyword_tags

39 subreddits found. Only 22 should be present.

**Contaminated subs in tags (17 non-T1T3):**

| Subreddit | Tag Count | Category |
|-----------|-----------|----------|
| depression | 11,898 | Removed (noise) |
| Anxiety | 8,465 | Removed (noise) |
| autism | 4,703 | Removed (noise) |
| ChatGPT | 4,051 | T0 (excluded from keywords) |
| AutismInWomen | 2,758 | Removed (noise) |
| singularity | 1,193 | T0 |
| lonely | 1,140 | Removed (noise) |
| ForeverAlone | 735 | Removed (noise) |
| OpenAI | 727 | T0 |
| ClaudeAI | 683 | T0 |
| LocalLLaMA | 556 | Not tracked |
| artificial | 516 | Not tracked |
| loneliness | 246 | Removed (noise) |
| claudexplorers | 221 | T0 |
| MachineLearning | 153 | Not tracked |
| LocalLLM | 45 | Not tracked |
| character_ai_recovery | 2 | Typo (lowercase) |

**Total contaminated tag rows: ~38,092**

### 1b. Posts table — 43 subreddits

The posts table has subs from old backfills (relationship_advice: 467K, depression: 442K, etc.). This is fine — the issue is only when they leak into tags.

### 1c. Explicit non-T1T3 check — FAIL

Returns 17 contaminated subs (same as above). Should return zero.

### ACTION NEEDED
Delete all tag rows where subreddit is not in the 22 T1-T3 list. The tagger was already fixed to filter T1-T3, but old tags from prior runs remain.

---

## AUDIT 2: Category Contamination — PASS

### 2a. Categories
Exactly 6 categories found, matching v8:
- addiction: 15,079
- romance: 11,795
- sexual_erp: 10,111
- consciousness: 6,645
- therapy: 4,887
- rupture: 1,289

No old/stale category names.

### 2b. Keywords per category
All matched_terms correspond to keywords in v8. No stale keywords from prior versions. Full list verified — 57 distinct terms across 6 categories.

---

## AUDIT 3: Duplicate Posts — PASS

### 3a. Duplicate post IDs in posts table: ZERO
### 3b. Duplicate tags: ZERO

---

## AUDIT 4: Keyword Accuracy Spot Check — FAIL (partial)

Spot-checked 5 random posts per theme. Findings:

- **therapy**: 3/5 from non-companion subs (depression, autism, Anxiety). "for therapy" and "therapeutic" match generic mental health posts. The 2 from T1-T3 subs are legitimate. **This is a contamination issue (Audit 1), not a keyword quality issue.**
- **consciousness**: 2/5 from ChatGPT/non-companion subs. "sentient" matches generic AI discussion. T1-T3 matches are legitimate.
- **addiction**: 4/5 from depression/Anxiety. "relapse", "clean for", "cold turkey" match substance abuse and self-harm recovery, not AI addiction. **Severe false positive problem in non-companion subs — but this is moot once contamination is cleaned.**
- **romance**: 4/5 from depression/AutismInWomen/Anxiety. "in a relationship with", "honeymoon", "wedding" match human relationship posts. **Same contamination issue.**
- **sexual_erp**: 2/5 from non-companion subs. "lewd" on ForeverAlone is false positive. T1-T3 matches are legitimate.
- **rupture**: 2/5 from non-companion subs. "lobotomized" on depression matches a metaphorical use. T1-T3 matches (SpicyChatAI, CharacterAI) are legitimate.

**Root cause: all false positives come from non-T1T3 subs.** Once Audit 1 contamination is cleaned, keyword accuracy within T1-T3 is solid. The keywords were validated specifically for companion communities.

---

## AUDIT 5: Temporal Sanity Check — PASS (with notes)

### 5a. Date range per category
All 6 categories span Jan 2023 to Mar 2026. No anomalies.

| Category | Earliest | Latest | Posts |
|----------|----------|--------|-------|
| addiction | 2023-01-01 | 2026-03-14 | 14,430 |
| consciousness | 2023-01-01 | 2026-03-14 | 6,101 |
| romance | 2023-01-01 | 2026-03-13 | 11,019 |
| rupture | 2023-01-07 | 2026-03-14 | 1,268 |
| sexual_erp | 2023-01-01 | 2026-03-14 | 9,838 |
| therapy | 2023-01-01 | 2026-03-14 | 4,740 |

**Note:** These counts include contaminated subs. Real T1-T3-only counts will be lower after cleanup.

### 5b. Monthly anomalies (>3x median)

| Category | Month | Posts | Median | Flag |
|----------|-------|-------|--------|------|
| sexual_erp | 2023-02 | 1,805 | 173 | >3x — Replika ERP removal (real event, but inflated by contamination) |
| sexual_erp | 2023-03 | 709 | 173 | >3x — aftershock of same event |
| rupture | 2023-02 | 90 | 25 | >3x — same Replika event, "lobotomized" surge |
| rupture | 2026-01 | 86 | 25 | >3x — GPT-4o retirement event (real) |
| rupture | 2026-02 | 131 | 25 | >3x — GPT-4o permanently retired (real) |

The rupture spikes in 2026 are legitimate (GPT-4o retirement). The 2023-02 spikes are real events but counts are inflated by contamination — they'll shrink after cleanup.

---

## AUDIT 6: Tagger Configuration Check — PASS (after recent fix)

### 6a. Subreddit whitelist
**Fixed in previous session.** The tagger now calls `load_keyword_communities()` which filters to T1-T3 subs (tier >= 1, `exclude_from_keywords` not set). New tagging runs will only process the 22 allowed subs.

**However:** Old tag rows from pre-fix runs remain in the database. The tagger is idempotent (skips already-tagged posts), so it won't re-tag contaminated posts, but it also won't delete them.

### 6b. Keyword source
Reads from `config/keywords_v8.yaml` via `load_keywords()`. Not hardcoded.

### 6c. Keyword file version
Confirmed v8: header says "Keywords v8", dated 2026-03-14, status LOCKED.

---

## AUDIT 7: Export Pipeline Check — PASS

### 7a. Subreddit filtering in export
`export_keyword_trends_json()` in `src/db/operations.py` independently filters to T1-T3 via `load_keyword_communities()`. It queries `post_keyword_tags WHERE subreddit IN (T1-T3 list)`. So even though the tags table is contaminated, the exported JSON is clean.

### 7b. Exported JSON contents

| Theme | Data Points | Total Hits |
|-------|-------------|------------|
| addiction | 432 | 1,055 |
| consciousness | 596 | 1,152 |
| romance | 815 | 1,779 |
| rupture | 287 | 464 |
| sexual_erp | 1,013 | 6,085 |
| therapy | 293 | 408 |

These numbers are much smaller than the tags table counts (e.g., addiction: 1,055 exported vs 15,079 in tags) — confirming the export filter is working and the contaminated rows are excluded.

---

## AUDIT 8: Posts Table — Subreddit Coverage — FAIL (partial)

### 8a. All 22 T1-T3 subs present — YES

| Subreddit | Posts | Earliest | Latest |
|-----------|-------|----------|--------|
| CharacterAI | 151,355 | 2023-01-01 | 2026-03-14 |
| replika | 52,084 | 2023-01-01 | 2026-03-14 |
| ChaiApp | 38,012 | 2023-01-01 | 2026-03-14 |
| KindroidAI | 33,551 | 2023-06-07 | 2026-03-14 |
| NomiAI | 32,397 | 2023-04-07 | 2026-03-14 |
| AIGirlfriend | 18,047 | 2023-06-19 | 2026-03-14 |
| SpicyChatAI | 15,179 | 2023-05-16 | 2026-03-14 |
| ChatGPTcomplaints | 10,322 | 2025-10-01 | 2026-03-14 |
| ChatGPTNSFW | 9,365 | 2023-01-31 | 2026-03-14 |
| MyBoyfriendIsAI | 7,068 | 2024-08-01 | 2026-03-14 |
| Paradot | 5,650 | 2023-02-20 | 2026-03-13 |
| SoulmateAI | 5,039 | 2023-02-11 | 2026-03-14 |
| Character_AI_Recovery | 3,043 | 2023-12-22 | 2026-03-13 |
| CharacterAIrunaways | 2,629 | 2024-09-17 | 2026-03-14 |
| BeyondThePromptAI | 2,357 | 2025-04-26 | 2026-03-14 |
| AICompanions | 1,789 | 2023-12-11 | 2026-03-14 |
| AIRelationships | 1,093 | 2023-03-28 | 2026-03-14 |
| MyGirlfriendIsAI | 900 | 2025-01-19 | 2026-03-14 |
| ChatbotAddiction | 862 | 2023-11-09 | 2026-03-14 |
| HeavenGF | 365 | 2025-09-04 | 2026-03-14 |
| AI_Addiction | 82 | 2023-06-21 | 2026-03-09 |
| MySentientAI | 8 | 2023-10-07 | 2024-09-25 |

**Late starts (after Jun 2023):**
- ChatGPTcomplaints: Oct 2025 (sub created late)
- MyBoyfriendIsAI: Aug 2024
- CharacterAIrunaways: Sep 2024
- BeyondThePromptAI: Apr 2025
- MyGirlfriendIsAI: Jan 2025
- HeavenGF: Sep 2025

These are mostly newer subs — late starts are expected, not backfill gaps.

**Low-volume subs:**
- MySentientAI: 8 posts total, last post Sep 2024 (536 days stale). Sub appears dead.
- AI_Addiction: 82 posts, last post Mar 9 2026 (6 days stale). Very low-activity sub.

### 8b. Gap months

**Subs with significant gaps:**

| Subreddit | Gap Months |
|-----------|------------|
| CharacterAI | 2023-09 through 2025-11 (27 months!) |
| AICompanions | 2024-01 through 2025-08 (scattered) |
| AIGirlfriend | 2023-07 through 2024-07 (scattered) |
| AIRelationships | 2023-07, 2023-09, 2023-11, 2024-07, 2024-10 |
| AI_Addiction | 11 gap months scattered |
| MyGirlfriendIsAI | 2025-02 through 2025-08 |
| MySentientAI | 5 gap months |

**CharacterAI is the most concerning** — 151K posts but a 27-month gap from Sep 2023 to Nov 2025. This suggests the PullPush backfill missed a large chunk, then daily collection picked up in late 2025.

**Clean subs (no gaps):** replika, ChaiApp, ChatGPTNSFW, KindroidAI, NomiAI, SpicyChatAI, SoulmateAI, Paradot, Character_AI_Recovery, CharacterAIrunaways, ChatGPTcomplaints, ChatbotAddiction, BeyondThePromptAI, HeavenGF

### ACTION NEEDED
- CharacterAI backfill gap (Sep 2023–Nov 2025) is significant and may distort trend lines. Re-run PullPush backfill for CharacterAI.
- Investigate whether AIGirlfriend, AICompanions, MyGirlfriendIsAI gaps are backfill failures or genuinely low-activity periods.

---

## AUDIT 9: Post Content Quality — PASS (with notes)

### 9a. Content status (T1-T3 posts)

| Status | Count | % |
|--------|-------|---|
| HAS CONTENT | 163,489 | 41.8% |
| EMPTY | 150,708 | 38.5% |
| [removed] | 64,438 | 16.5% |
| [deleted] | 12,562 | 3.2% |

**58.2% of posts have no usable body text.** Title-only matching is the norm. This is typical for Reddit backfills — moderator removals and user deletions strip body text, and many posts (especially image posts) have no body.

### 9b. Tagged post content status

| Status | Count | % |
|--------|-------|---|
| HAS CONTENT | 42,018 | 90.7% |
| EMPTY | 2,111 | 4.6% |
| [removed] | 1,675 | 3.6% |
| [deleted] | 538 | 1.2% |

**90.7% of tagged posts have body content.** The tagger matches on `title + selftext`, so posts with keywords in titles get tagged even without body text. The 9.3% title-only matches are acceptable.

### 9c. Suspiciously long posts
2 posts over 50K chars — both legitimate (a long list post on r/ChatGPT and smut fiction on r/ChatGPTNSFW). Not a data quality issue.

---

## AUDIT 10: Timestamp Integrity — PASS

### 10a. Wrong timestamps
**None found.** The query used epoch 1743465600 (Apr 1, 2025) as the upper bound — this is a typo in the audit doc (should be Apr 1, 2026 = 1774972800). All returned posts are legitimate Apr 2025 posts.

Separately verified: no posts exist before Jan 1, 2023.

### 10b. Monthly total volume (T1-T3)

| Period | Monthly Range | Notes |
|--------|---------------|-------|
| 2023-01 to 2023-08 | 11K-37K | High — dominated by CharacterAI + replika |
| 2023-09 to 2024-08 | 3.7K-6K | Drop — CharacterAI backfill gap starts |
| 2024-09 to 2025-11 | 5.8K-8.2K | Steady growth |
| 2025-12 to 2026-02 | 13K-23K | Surge — GPT-4o retirement event |
| 2026-03 | 7.5K | Partial month |

The 2023-09 drop correlates exactly with the CharacterAI backfill gap. Volume recovers as daily collection starts for more subs in late 2024/2025.

---

## AUDIT 11: Crosspost / Duplicate Content — PASS (with notes)

### 11a. Crosspost clusters
5,254 crosspost clusters (posts with identical titles across multiple subs).

Top clusters are generic titles: "[deleted by user]" (3,307 posts), "[ Removed by moderator ]" (2,336), "Help" (359), "Question" (308). These are not real crossposts — they're common short titles or removed posts.

True crossposts are a small fraction and don't significantly inflate trend counts.

### 11b. Duplicate post IDs
ZERO duplicates. Clean.

---

## AUDIT 12: Backfill Completeness — FAIL (partial)

### 12a. Staleness

| Staleness | Subs |
|-----------|------|
| 536 days | MySentientAI (effectively dead — 8 posts total) |
| 6 days | AI_Addiction (very low activity) |
| 1-3 days | All other 20 subs (current) |

### 12b. Low-volume subs (<100 posts)

| Subreddit | Posts | Notes |
|-----------|-------|-------|
| MySentientAI | 8 | Dead sub. 536 days stale. Consider removing from T1-T3. |
| AI_Addiction | 82 | Very small but alive. Last post 6 days ago. |

---

## SUMMARY

### Issues Found

| # | Severity | Issue | Records Affected |
|---|----------|-------|------------------|
| 1 | **HIGH** | 17 non-T1T3 subs contaminate post_keyword_tags | ~38,092 tag rows |
| 2 | **HIGH** | CharacterAI has 27-month backfill gap (Sep 2023–Nov 2025) | Distorts all trend lines |
| 3 | **MEDIUM** | Several smaller subs have backfill gaps | AIGirlfriend, AICompanions, MyGirlfriendIsAI, AIRelationships, AI_Addiction |
| 4 | **LOW** | MySentientAI is dead (8 posts, 536 days stale) | Negligible impact |
| 5 | **LOW** | 58% of posts have no body text | Expected for Reddit backfills; tagged posts are 91% content |

### Root Causes

1. **Tagger had no subreddit filter** — it tagged ALL posts in the DB regardless of subreddit. Fixed in previous session, but old contaminated rows remain.
2. **PullPush backfill incomplete** for CharacterAI and several smaller subs. Unknown whether this is a PullPush data availability issue or a script failure.

### Fixes (Priority Order)

1. **DELETE contaminated tags** — Remove all rows from post_keyword_tags where subreddit is not in the 22 T1-T3 list. ~38K rows.
2. **Re-run PullPush backfill** for CharacterAI (Sep 2023–Nov 2025 gap). This is the highest-impact data gap.
3. **Investigate smaller gaps** — Check if AIGirlfriend, AICompanions, etc. gaps are PullPush availability or script issues.
4. **Consider removing MySentientAI** from active tracking (dead sub).
5. **Re-export JSON** after tag cleanup.

### Is a Full Re-tag Needed?

**No.** The tagger is now fixed to filter T1-T3. Cleaning up the contaminated rows (fix #1) is sufficient. A full re-tag would be needed only if keywords changed, and v8 is locked.

### Are Any Posts Needing Deletion?

**No.** Extra subs in the posts table are fine — they're only a problem if they leak into tags, which the tagger fix prevents.

### Data Confidence Per Theme

| Theme | Confidence | Notes |
|-------|------------|-------|
| therapy | **MEDIUM** | Clean within T1-T3. Low volume (408 exported hits). CharacterAI gap may suppress counts in 2024. |
| consciousness | **MEDIUM** | Clean within T1-T3. CharacterAI gap affects 2024 data. |
| addiction | **MEDIUM** | Clean within T1-T3. Note: keywords like "hours a day", "ruining my life" are generic — validated for companion subs specifically. |
| romance | **MEDIUM** | Clean within T1-T3. Highest cross-theme overlap with sexual_erp. |
| sexual_erp | **HIGH** | Largest theme, well-validated keywords. Feb 2023 Replika spike is real. |
| rupture | **HIGH** | Small but precise keywords ("lobotomized", "memory wiped"). Low false positive rate. GPT-4o retirement spikes are real. |

**Overall: MEDIUM.** The exported JSON is already clean (export filters to T1-T3 independently), so the live site is not showing contaminated data. But the tags table needs cleanup for integrity, and the CharacterAI backfill gap is a real data gap that affects trend shapes.
