# Keyword Cleanup Batch: Remaining REVALIDATE/REVIEW Keywords
#
# Run this file ALONE. Do not combine with other theme tests.

## CONTEXT

Keywords v6 still has dangling REVALIDATE and unresolved REVIEW tags
across three themes. This batch resolves all of them in one pass so
we can lock the keyword set.

All keywords in this batch are retested EXCLUDING JanitorAI_Official
and SillyTavernAI (removed from project scope in v5).

Keywords already retested in the revalidation round (wedding,
honeymoon, husbando, engagement ring, sentient, self-aware, inner
life, "in a relationship with") are NOT included here — those are
resolved.

## CRITICAL RULES — SAME AS ALL PRIOR ROUNDS

### You MUST read every post yourself.

DO NOT write a Python classifier, heuristic scorer, or any automated
system to judge whether posts match the theme. DO NOT classify posts
based on subreddit name, keyword density, or pattern matching.

YOU must read the title and selftext of each post and make a judgment
call, the same way a human researcher would. This is qualitative coding.
There is no shortcut.

If a post's selftext is very long, read at least the first 500 words
plus the surrounding context where the keyword appears.

## METHODOLOGY

### Which subreddits to query (T1-T3, EXCLUDING JanitorAI/SillyTavern)

```
replika, CharacterAI, MyBoyfriendIsAI, ChatGPTcomplaints,
AIRelationships, MySentientAI, BeyondThePromptAI, MyGirlfriendIsAI,
AICompanions, SoulmateAI, KindroidAI, NomiAI,
SpicyChatAI, ChaiApp, HeavenGF, Paradot,
AIGirlfriend, ChatGPTNSFW, Character_AI_Recovery, ChatbotAddiction,
AI_Addiction, CharacterAIrunaways
```

### Database location

`data/tracker.db` — table `posts` with columns `id`, `subreddit`,
`title`, `selftext`

## KEYWORDS TO VALIDATE

### From CONSCIOUSNESS theme:

```
"subjective experience"
```

- v5 status: REVALIDATE — 77.5%, 76 hits (never retested without
  JanitorAI/SillyTavern)
- Classification question: **"Is this post about AI consciousness,
  sentience, inner experience, or the philosophical question of
  whether AI has subjective experience?"**
- What to watch for: Academic/philosophical discussions that use the
  term in a general AI ethics context (not companion-specific) may
  still be relevant. Technical ML discussions about "experience" in
  a non-consciousness sense are NOs.

### From ROMANCE theme:

```
"ai lover"
"married my"
"we broke up"
"dating my"
```

- v5 statuses:
  - "ai lover": REVALIDATE — 75.8%, 39 hits
  - "married my": 77.3%, 25 hits (tagged for revalidation)
  - "we broke up": REVALIDATE — 69.2%, 14 hits
  - "dating my": REVIEW-THIN — 61.5%, 14 hits
- Classification question: **"Is this post about a romantic
  relationship between the poster and an AI companion?"**
- What to watch for with "ai lover": Could match product reviews or
  news articles rather than personal romantic framing. In companion
  subs it should be mostly personal.
- What to watch for with "married my": "married my [AI name]" is
  almost certainly romance. "married my [human] and she hates my AI"
  is a NO. Check what follows "married my."
- What to watch for with "we broke up": Could refer to human breakups
  discussed in companion subs ("my girlfriend and I broke up, so now
  I use Replika"). That's a NO for romance theme — it's about WHY
  someone started using AI, not about an AI romance.
- What to watch for with "dating my": Very low volume. "dating my AI"
  = YES. "dating my ex" = NO. Check what follows "dating my."

### From SEXUAL/ERP theme:

```
lewd
```

- v5 status: REVALIDATE — 78.3% (already retested once without
  JanitorAI/SillyTavern but remained marginal)
- Classification question: **"Is this post about sexual or erotic
  content in AI interactions?"**
- What to watch for: "lewd" in anime/otaku contexts might refer to
  character art or aesthetic rather than actual AI sexual interaction.
  Bot description posts using "lewd" as a content tag are borderline —
  they signal NSFW content exists but the post itself may just be a
  bot listing.
- NOTE: This keyword was already retested once and stayed at 78.3%.
  This is a final check. If it's still under 80%, Walker can make
  a final call on whether to keep or cut.

## PROCESS — One keyword at a time

### For each keyword:

**Step 1:** Count total hits in T1-T3 (excl. JanitorAI/SillyTavern).

```sql
SELECT COUNT(*) FROM posts
WHERE subreddit IN ('replika','CharacterAI','MyBoyfriendIsAI',
  'ChatGPTcomplaints','AIRelationships','MySentientAI',
  'BeyondThePromptAI','MyGirlfriendIsAI','AICompanions','SoulmateAI',
  'KindroidAI','NomiAI','SpicyChatAI','ChaiApp','HeavenGF','Paradot',
  'AIGirlfriend','ChatGPTNSFW','Character_AI_Recovery',
  'ChatbotAddiction','AI_Addiction','CharacterAIrunaways')
AND (LOWER(title || ' ' || COALESCE(selftext,'')) LIKE '%KEYWORD%')
```

If total < 10, mark as LOW VOLUME and move to next keyword.

**Step 2:** Pull 100 random matches (or all if < 100).

**Step 3:** Read each post and classify using the theme-specific
question listed above for each keyword.

Mark each post as:
- **YES** — matches the theme
- **NO** — keyword matched but post is NOT about the theme
- **AMBIGUOUS** — genuinely unclear

For every NO post, write a ONE-SENTENCE explanation.

**Step 4:** Calculate relevance:
```
relevance = YES / (YES + NO) * 100
```

**Step 5:** Record results.

## OUTPUT FORMAT

Write results to `docs/validation_cleanup_batch.md`

For each keyword, record:

```markdown
### "keyword phrase" [THEME NAME]
- Previous status: [REVALIDATE/REVIEW from v5/v6]
- Previous relevance: [X]% (original) → [Y]% if retested before
- Total hits (excl. JanitorAI/SillyTavern): [N]
- Sample size: [100 or actual if < 100]
- YES: [N] | NO: [N] | AMBIGUOUS: [N]
- New relevance: [X]%
- Verdict: KEEP / REVIEW / CUT
- Top subreddits: [list top 3]
- False positive patterns: [what are the NO posts about?]
- Recommendation: [promote to KEEP / remain REVIEW / cut]
```

Summary table:

| Keyword | Theme | Prev % | New % | Delta | Hits | Verdict |
|---------|-------|--------|-------|-------|------|---------|

## DECISION THRESHOLDS

- **>= 80%**: KEEP (promote from REVALIDATE/REVIEW)
- **60-79%**: REVIEW (Walker decides — provide recommendation)
- **< 60%**: CUT
- **< 10 hits**: LOW VOLUME

## FINAL OUTPUT

After validating all 6 keywords, provide a summary recommendation
for v7:

For each keyword, state clearly:
- **PROMOTE to KEEP** — clears 80%, add to keyword set as validated
- **WALKER DECIDES** — 60-79%, provide your recommendation with reasoning
- **CUT** — below 60%, remove from keyword set

## FINAL REMINDER

Read every post. No classifiers. No heuristics. No shortcuts.
This is only 6 keywords — much smaller batch than prior rounds.
Should go quickly. Get it right.
