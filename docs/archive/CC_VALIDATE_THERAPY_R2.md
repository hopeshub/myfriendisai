# Keyword Validation: THERAPY Theme — Round 2
#
# Run this file ALONE. Do not combine with other themes.
# This is a FOLLOW-UP to the Round 1 validation (validation_therapy.md).

## CONTEXT — Why Round 2 Exists

Round 1 tested 14 therapy keywords. Results:
- 1 KEEP ("ai therapist" — 92% relevance, 28 hits)
- 2 REVIEW ("ai therapy" 73%, "free therapy" 75%)
- 3 CUT (ambiguity between human/AI therapists, or complaint language)
- 8 LOW VOLUME / NO MATCHES

The theme survived with only ~56 hits across 3.26M posts. That's too
thin for trend detection. The core problems were:

1. **Human-therapist ambiguity**: "my therapist" and "therapy session"
   split ~50/50 between AI-as-therapy and human-therapist-in-passing.
2. **Complaint capture**: "like a therapist" was 82% UX complaints
   about unwanted therapist behavior ("stop acting like a therapist").
3. **Low volume on precise phrases**: "replaced my therapist," "better
   than therapy," etc. had perfect face validity but < 10 hits each.

Round 2 tests NEW keyword candidates designed to:
- Capture the **vernacular** of therapeutic AI use (how people actually
  describe it, not how researchers would phrase it)
- Use **structural specificity** to avoid the human-therapist trap
  (e.g., "is my therapist" vs. bare "my therapist")
- Test **mental health function language** (people describing what AI
  does for their mental health without using the word "therapist")
- Explore **adjacent therapeutic framing** (coping, emotional support,
  mental health) that may or may not belong in this theme

## CRITICAL RULES — SAME AS ROUND 1

### You MUST read every post yourself.

DO NOT write a Python classifier, heuristic scorer, or any automated
system to judge whether posts match the theme. DO NOT classify posts
based on subreddit name, keyword density, or pattern matching.

YOU must read the title and selftext of each post and make a judgment
call, the same way a human researcher would. This is qualitative coding.
There is no shortcut.

If a post's selftext is very long, read at least the first 500 words
plus the surrounding context where the keyword appears.

### Why this matters

Round 1 was done correctly — manual post-by-post reading. Round 2 must
maintain the same standard. These results will be compared directly to
Round 1, so methodology must be identical.

## METHODOLOGY

### Which subreddits to query (T1-T3 ONLY)

```
replika, CharacterAI, MyBoyfriendIsAI, ChatGPTcomplaints,
AIRelationships, MySentientAI, BeyondThePromptAI, MyGirlfriendIsAI,
AICompanions, SoulmateAI, KindroidAI, NomiAI,
SpicyChatAI, ChaiApp, HeavenGF, Paradot,
AIGirlfriend, ChatGPTNSFW, Character_AI_Recovery, ChatbotAddiction,
AI_Addiction, CharacterAIrunaways
```

### Database location

`data/tracker.db` — table `posts` with columns `id`, `subreddit`, `title`, `selftext`

### Round 2 Keywords to Validate

These are organized into three categories based on what they're
trying to capture. The categories are just for context — validate
every keyword the same way.

**Category A — Structurally specific AI-therapy phrases**
These add grammatical specificity to avoid the human-therapist trap
that killed "my therapist" in Round 1.

```
is my therapist
as a therapist
as my therapist
for therapy
therapy bot
therapist bot
```

Rationale: "is my therapist" ("Replika IS my therapist") forces a
copular framing that should skew toward AI. "as a therapist" ("I use
it AS a therapist") implies intentional therapeutic use. "for therapy"
("I use Replika FOR therapy") is purpose-framing. "therapy bot" and
"therapist bot" are explicit AI-therapy compounds like the successful
"ai therapist."

**IMPORTANT for "as a therapist":** Round 1 found that "like a
therapist" was 82% complaints ("acts like a therapist" = unwanted
behavior). "as a therapist" MIGHT have the same problem ("uses it as
a therapist" vs. "it responds as a therapist"). Pay close attention
to whether "as a therapist" shares the complaint pattern.

**Category B — Mental health function language**
These capture people describing what AI does for their mental health
without using "therapist" or "therapy."

```
my mental health
helps with my anxiety
helps with my depression
helps me cope
coping mechanism
```

Rationale: In companion subs, "my mental health" should often appear
in posts about AI's effect on mental health. The "helps with my X"
phrases are therapeutic function descriptions. "coping mechanism" is
clinical-adjacent language people use to describe therapeutic tools.

**IMPORTANT for "my mental health":** This will likely be HIGH VOLUME
and could go either way — it might capture "AI ruined my mental
health" as often as "AI helped my mental health." Both are relevant
to the AI-as-therapy discourse, but pay attention to the split. In
your NO explanations, note whether NOs are about AI-and-mental-health
(relevant to the broader theme but not therapy-specific) vs. totally
off-topic.

**Category C — Therapeutic descriptors and adjacent framing**
These test whether broader therapeutic/support language belongs in
this theme or is too diffuse.

```
therapeutic
emotional support
someone to talk to
mental health support
```

Rationale: "therapeutic" ("talking to my AI is therapeutic") is a
direct descriptor. "emotional support" and "someone to talk to" may
be too broad — they could capture loneliness/companionship discourse
rather than therapy-specific discourse. That's exactly what we need
to find out. "mental health support" is more specific than
"emotional support."

**IMPORTANT for Category C:** These keywords might score high
relevance but belong in a DIFFERENT theme (companionship, loneliness,
emotional dependency). When classifying, apply the Round 1 standard
strictly:

**"Is this post about using AI as a therapist, for therapeutic
purposes, or as a replacement for therapy?"**

If a post is about AI as a companion/friend but NOT framed in
therapeutic terms, mark it NO even if the poster is clearly getting
emotional benefit. The therapy theme is specifically about the
therapy framing, not general emotional support.

## PROCESS — One keyword at a time

### For each keyword:

**Step 1:** Count total matches in T1-T3.

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

```sql
SELECT id, subreddit, title, selftext FROM posts
WHERE subreddit IN (/* T1-T3 list above */)
AND (LOWER(title || ' ' || COALESCE(selftext,'')) LIKE '%KEYWORD%')
ORDER BY RANDOM()
LIMIT 100
```

**Step 3:** Read each post and classify it.

For each post, read the title and body. Answer ONE question:

**"Is this post about using AI as a therapist, for therapeutic
purposes, or as a replacement for therapy?"**

Mark each post as:
- **YES** — the post is clearly about AI-as-therapy
- **NO** — the keyword matched but the post is NOT about AI-as-therapy
- **AMBIGUOUS** — genuinely unclear

For every post you mark NO, write a ONE-SENTENCE explanation of what
the post was actually about. This is critical for understanding false
positive patterns.

**Step 4:** After reading all posts for one keyword, calculate:

```
relevance = YES / (YES + NO) * 100
```

(Exclude AMBIGUOUS from denominator. Report AMBIGUOUS count separately.)

**Step 5:** Record results and move to the next keyword.

## OUTPUT FORMAT

Write results to `docs/validation_therapy_r2.md`

For each keyword, record:

```markdown
### "keyword phrase"
- Total hits in T1-T3: [N]
- Sample size: [100 or actual if < 100]
- YES: [N] | NO: [N] | AMBIGUOUS: [N]
- Relevance: [X]%
- Verdict: KEEP / REVIEW / CUT
- Top subreddits: [list top 3 by hit count]
- False positive patterns: [what are the NO posts about?]
- Round 2 notes: [any observations about how this keyword compares
  to Round 1 keywords, unexpected patterns, etc.]
```

Then at the bottom, include a summary table:

| Keyword | Hits | YES | NO | AMB | Relevance | Verdict |
|---------|------|-----|----|-----|-----------|---------|

## DECISION THRESHOLDS (same as Round 1)

- **>= 80%**: KEEP
- **60-79%**: REVIEW (Walker decides)
- **< 60%**: CUT
- **< 10 hits**: LOW VOLUME (flag for Walker)

## COMBINED THEME ASSESSMENT

After validating all 15 Round 2 keywords, combine with Round 1
survivors and produce a unified picture.

### Round 1 survivors (carry forward):
- KEEP: "ai therapist" (92%, 28 hits)
- REVIEW: "ai therapy" (73.3%, 16 hits)
- REVIEW: "free therapy" (75%, 12 hits)

### Unified summary table:

Merge Round 1 survivors + Round 2 KEEP/REVIEW keywords into one table.
Calculate total theme volume (sum of hits across all KEEP + REVIEW
keywords). Flag any keyword > 40% of total.

### Overlap check:

Some Round 2 keywords might match the SAME posts as Round 1 keywords.
For each Round 2 KEEP/REVIEW keyword, run:

```sql
SELECT COUNT(*) FROM posts
WHERE subreddit IN (/* T1-T3 */)
AND (LOWER(title || ' ' || COALESCE(selftext,'')) LIKE '%R2_KEYWORD%')
AND (
  (LOWER(title || ' ' || COALESCE(selftext,'')) LIKE '%ai therapist%')
  OR (LOWER(title || ' ' || COALESCE(selftext,'')) LIKE '%ai therapy%')
  OR (LOWER(title || ' ' || COALESCE(selftext,'')) LIKE '%free therapy%')
)
```

Report how many posts are captured by BOTH a Round 1 and Round 2
keyword. This tells Walker how much NEW volume Round 2 actually adds
vs. re-capturing existing posts.

### Net new volume:

Calculate total UNIQUE posts captured by all KEEP/REVIEW keywords
combined (Round 1 + Round 2). This is the real number that matters.

```sql
SELECT COUNT(DISTINCT id) FROM posts
WHERE subreddit IN (/* T1-T3 */)
AND (
  (LOWER(title || ' ' || COALESCE(selftext,'')) LIKE '%ai therapist%')
  OR (LOWER(title || ' ' || COALESCE(selftext,'')) LIKE '%ai therapy%')
  OR (LOWER(title || ' ' || COALESCE(selftext,'')) LIKE '%free therapy%')
  -- add Round 2 KEEP/REVIEW keywords here
)
```

### Theme viability assessment:

Based on the combined Round 1 + Round 2 results, give Walker a
straight answer:

1. **What is the total unique post volume for the Therapy theme?**
2. **What is the combined weighted relevance?**
3. **Is this enough for meaningful trend detection?** (Consider: with
   monthly data, do we have enough posts per month to see anything?)
4. **Should Walker keep this as a standalone theme, merge it into a
   broader "mental health" theme, or retire it?**

## FINAL REMINDER

Read every post. No classifiers. No heuristics. No shortcuts.
This is 15 keywords × up to 100 posts = up to 1,500 posts.
Take your time. Get it right.
