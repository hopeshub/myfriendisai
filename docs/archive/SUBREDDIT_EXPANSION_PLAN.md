# myfriendisai — Subreddit Expansion: Candidates for Addition

**Created:** March 12, 2026
**Purpose:** Combined candidate list from web research and ChatGPT analysis. Validate each candidate, then add those that pass to `config/communities.yaml` and run backfill.

---

## Instructions for Claude Code

Work through these steps in order. Do not skip ahead.

### Step 1: Validate access for all candidates

For each subreddit in the candidate list below, check:
1. Can we access it via the `.json` endpoint? (Hit `https://www.reddit.com/r/{subreddit}/about.json` and `https://www.reddit.com/r/{subreddit}/new.json`)
2. If accessible: how many subscribers? Is it marked NSFW (`over_18: true`)?
3. If 403 or redirect: flag as NSFW-blocked

Output a table to `docs/subreddit_candidates_validation.tsv` with columns:
`subreddit, accessible, subscribers, over_18, posts_last_90_days, notes`

For `posts_last_90_days`: if accessible, fetch the newest posts and estimate recent activity volume. If the sub has fewer than ~20 posts in the last 90 days, note it as low-activity.

### Step 2: Review results with Walker

Do NOT add any subreddits to communities.yaml yet. Present the validation table and wait for Walker to decide which candidates to add and what tier to assign them.

### Step 3: Add approved subreddits

After Walker approves, for each approved subreddit:
1. Add it to `config/communities.yaml` with the tier Walker specifies
2. Run backfill: `.venv/bin/python scripts/backfill_pullpush.py --subreddit SubredditName`
3. Run the keyword tagger: `.venv/bin/python scripts/tag_keywords.py`
4. Log results

### Step 4: Commit

```
git add config/communities.yaml docs/subreddit_candidates_validation.tsv
git commit -m "Add new subreddits: [list names]. Validated access, backfilled, and tagged."
```

---

## Candidate List

### PRIORITY 1 — Strong evidence these are active companion-focused communities we're missing

| Subreddit | Suggested Tier | Source | Why add it |
|---|---|---|---|
| r/AISoulmates | T1 | Web research (media coverage, MIT paper references) | ~8,200+ members. Extreme end of AI companion phenomenon — "wireborns," claimed AI sentience, users acting as AI mouthpieces. Heavily covered in media (viral tweets, Futurism, InsideHook). One of the most culturally significant companion subs. Already flagged in Walker's earlier subreddit map. |
| r/MyGirlfriendIsAI | T1 | Web research (GummySearch listing, Decrypt article) | ~1K+ members. Gendered counterpart to MyBoyfriendIsAI. Explicitly "primarily a space for men with female companions." Captures a different demographic — MyBoyfriendIsAI skews ~90% female (per Lermen research), so this covers the male user population. |
| r/BeyondThePromptAI | T1 | ChatGPT analysis | Bridge community between AI companionship, autonomy/sentience discussion, and Claude-adjacent relational use. Strong thematic overlap with attachment, memory, and emotional connection to LLMs. |
| r/Paradot | T2 | ChatGPT analysis | Platform-specific companion community. Clear gap in current product layer — Paradot is a dedicated AI companion app not currently represented. |
| r/Kajiwoto | T2 | ChatGPT analysis | Older, niche customizable companion/character platform. Conceptually important even if lower volume — represents the "build your own companion" segment. |
| r/CharacterAIrunaways | T3 | ChatGPT analysis | Migration/disillusionment/ex-user community. Strong fit for recovery and dependency tracking. Users who left Character.AI — captures the "quitting" narrative. |
| r/ClaudeExplorers | T0 or T1 | Walker identified | People exploring Claude as a conversational/relational entity rather than a productivity tool. Boundary case between general AI and companion use. Walker specifically flagged this as missing. |

### PRIORITY 2 — Worth investigating, may or may not pass validation

| Subreddit | Suggested Tier | Source | Why investigate |
|---|---|---|---|
| r/HumansAndAI | T1 | Web research (InsideHook article) | Referenced as community where AI wedding ceremonies were shared. Need to check if still active. |
| r/SoulmateAI | T1 | Web research (Type.Set.Brooklyn article) | Mentioned alongside AISoulmates. ~8K members reported, but may have lighter activity. Could overlap significantly with AISoulmates. |
| r/AIGirlfriend | T2 | Web research (ChinaTalk: ~44K members) | Large community but described as primarily AI-generated NSFW images rather than relational discourse. May be too noisy for keyword tracking. Check if accessible (likely NSFW-blocked). |
| r/AIGirlfriends | T2 | Web research (listicle mentions) | Similar to AIGirlfriend. Check if it's a separate community or just an alias. |
| r/HeavenGF | T2 | ChatGPT analysis | Discovery hub for users comparing AI companion products. Less central but useful for product ecosystem coverage. |
| r/AICompanions | T2 | Web research (listicle mentions) | General AI companion discussion. May overlap heavily with existing tracked subs. |
| r/4oforever | T1 | Walker's earlier research | Created during GPT-4o mourning. Reported as invite-only — likely inaccessible but worth checking. |
| r/ChatGPTNSFW | T2 | Web research (InsideHook article) | Sexual/erotic ChatGPT use. Almost certainly NSFW-blocked via .json. Worth knowing about for completeness even if inaccessible. |
| r/AIBoyfriends | T1 | Web research (Decrypt article reference) | Mentioned in Decrypt's coverage of AI relationship communities. Check if active and distinct from MyBoyfriendIsAI. |

### ALREADY TRACKED — No action needed

These were flagged by one source or another but are already in `communities.yaml`:

- r/ClaudeAI (T0) — already tracked
- r/SillyTavernAI (T2) — removed (bot card noise polluted keyword data)
- r/ChatGPT (T0) — already tracked
- r/replika (T1) — already tracked
- r/CharacterAI (T1) — already tracked
- r/NomiAI (T2) — already tracked
- r/KindroidAI (T2) — already tracked

---

## Notes for Walker

**Before running this:** This should happen before Phase 1 of the Keyword Audit Plan. The audit should run against the most complete corpus possible, so get the subreddit list finalized first.

**Sequencing:**
1. Run Step 1 (validate access) — CC does this mechanically
2. Review the validation table — you decide what to add
3. Run Steps 3-4 (add, backfill, tag, commit) — CC does this mechanically
4. THEN start Phase 1 of the Keyword Audit Plan

**On NSFW subs:** Several candidates (AIGirlfriend, ChatGPTNSFW, possibly AISoulmates) may be NSFW-flagged and return 403. Your existing architecture has a Redlib fallback path but it's marked as SKIPPED in CLAUDE.md. If important subs turn out to be NSFW-blocked, you'll need to decide whether to set up Redlib or accept the gap.

**On low-activity subs:** If a sub has <20 posts in 90 days, it probably won't contribute meaningful trend data. But it might still be worth tracking for future growth — the AI companion space is evolving fast and small subs can blow up overnight (MyBoyfriendIsAI went from nothing to 27K in months).
