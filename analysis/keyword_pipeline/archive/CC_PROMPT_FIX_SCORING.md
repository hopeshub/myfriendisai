# Task: Fix Discovery Script Scoring and Matching

## Context
The discovery script (discover_keywords.py) is surfacing junk because the scoring and matching are fundamentally broken. This is a ranking fix, not a filter fix. Make these four changes in order.

## Change 1: Replace infinite ratio with smoothed scoring
**Files:** discover_keywords.py (around lines 208, 238, 252)

**Problem:** Terms with base_count == 0 get infinite lift scores, which guarantees rare artifacts and copypasta float to the top. "apple bad" isn't meaningful Rupture vocabulary — it's just absent from baseline.

**Fix:** Replace the raw ratio with smoothed log-odds or smoothed lift. At minimum, add pseudocounts so zero-in-baseline never produces infinity. Then change the final ranking (line 252) to sort by a composite score like `distinct_posts * smoothed_lift` instead of lift alone. This rewards terms that are both distinctive AND widespread.

## Change 2: Switch from token frequency to document frequency
**Files:** discover_keywords.py (around lines 109-125)

**Problem:** The script counts every token occurrence, so a single copypasta post with 40 repetitions of a word massively inflates that term. You already track distinct posts but don't use it as the primary statistic.

**Fix:** Make per-post document frequency the primary scoring input. Each post counts once per term, regardless of how many times the term appears in it. Raw token count can stay as a secondary/display field but should not drive the ranking.

## Change 3: Fix matching semantics to be consistent
**Files:** discover_keywords.py, utils.py (around line 180)

**Problem:** Discovery finds candidates at the token level, but the volume gating in utils.py uses substring LIKE matching. This means "lika" picks up every mention of "Replika." Discovery and validation are measuring different things.

**Fix:** Make discovery and validation use the same matching semantics:
- Single words: word boundary matching (not substring LIKE)
- Phrases: token-aware phrase matching
- Ideally create one shared matcher function used everywhere

## Change 4: Add concentration filter and sample snippets
**Files:** discover_keywords.py

**Problem:** Terms dominated by a single subreddit are likely community-specific artifacts, not cross-cutting theme vocabulary. Also, reviewing candidates requires opening the DB to see if they're junk.

**Fix:**
- Add a per-subreddit concentration filter: reject terms where one subreddit contributes >60% of positive posts
- Add a max within-post repetition cap: if a term appears 40 times in one post, count it once
- Add a "review samples" column to the CSV output: 3 short example snippets per candidate so junk is visible at a glance

## After making changes
1. Show me the key changed sections of code before re-running (I want to understand what changed)
2. After I review, re-run discovery on all six themes and show top 20 candidates per theme

## Important
Also update the README.md Phase 3 section to reflect these scoring changes — this is now part of the permanent pipeline design, not a patch.
