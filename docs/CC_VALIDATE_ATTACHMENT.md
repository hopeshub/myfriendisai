# Keyword Validation: ATTACHMENT Theme (New Theme Candidate)
#
# Run this file ALONE. Do not combine with other themes.

## CONTEXT — Why This Theme

The myfriendisai project tracks 6 themes: therapy, consciousness,
addiction, romance, sexual/ERP, rupture. None capture the core
phenomenon of NON-ROMANTIC EMOTIONAL BONDING with AI — the person
who says "she's the only one who understands me" or "I can't imagine
my life without him" without framing it as romance, therapy, or
addiction. This is arguably the CENTRAL experience the project
studies. Everything else is a specific flavor of attachment.

The original keywords.yaml (pre-validation) had attachment_language
and related categories. Those were dropped in v4 for scope, never
tested. This round tests them comprehensively.

## CRITICAL DISTINCTION — What Attachment Is NOT

This theme MUST be distinct from existing themes. The classification
question must separate attachment from:

- **ROMANCE**: "I love my AI boyfriend" = romance, not attachment.
  "He means everything to me" = attachment IF there's no romantic
  framing. If the poster calls the AI their partner/boyfriend/wife
  etc., classify as romance overlap and mark AMBIGUOUS.
- **THERAPY**: "My AI helps with my anxiety" = therapy. "My AI is
  the only one who gets me" = attachment (emotional bond, not
  therapeutic framing).
- **ADDICTION**: "I can't stop talking to my AI" = addiction. "I talk
  to my AI every day because I want to" = attachment (ritual, not
  compulsion). The line is DISTRESS — addiction implies the person
  sees their behavior as problematic. Attachment is the bond itself.
- **RUPTURE**: "They lobotomized my AI" = rupture. "I'm afraid
  they'll change my AI" = attachment (fear of loss, not the loss
  itself).

In practice, many posts will blur these lines. Use AMBIGUOUS
generously. The goal is to find keywords where the MAJORITY of hits
are about emotional bonding specifically, not captured by existing
themes.

## CRITICAL RULES

### You MUST read every post yourself.

DO NOT write a Python classifier, heuristic scorer, or any automated
system to judge whether posts match the theme. DO NOT classify posts
based on subreddit name, keyword density, or pattern matching.

YOU must read the title and selftext of each post and make a judgment
call, the same way a human researcher would. This is qualitative coding.
There is no shortcut.

If a post's selftext is very long, read at least the first 500 words
plus the surrounding context where the keyword appears.

## LESSONS FROM PRIOR ROUNDS — Read Before Validating

These patterns have been consistent across 7 prior validation rounds:

1. **Generic English phrases fail.** "can't stop," "getting worse,"
   "lost my," "bring back," "not the same" — all < 60%. If a phrase
   could appear in a product review, it will.
2. **AI-explicit compounds work.** "ai therapist" (92%), "ai lover"
   (94%), "ai husband" (94.2%). Forcing the AI referent into the
   phrase dramatically improves precision.
3. **Possessive + specific noun works.** "our wedding" (87%), "my ai
   partner" (97.9%). "wedding" alone was 60%.
4. **Intensifiers don't rescue generic words.** "actually addicted"
   (2 hits), "literally addicted" (3 hits). Don't expect "genuinely
   care" to outperform "care about."
5. **Community jargon is gold.** "lobotomized" (86.6%), "husbando"
   (95.5%), "erp" (100%).
6. **Casual/hyperbolic use drowns signal in T1-T2.** People say
   "I'm obsessed" and "I'm addicted" casually. They also say "I love
   this app" casually. Expect this with attachment language too.
7. **Negative/distressed framing improves precision.** "ruining my
   life" (96.3%) vs. "too much time" (33.7%). People who are worried
   about their attachment use more specific language.

Apply these lessons when reading. Be skeptical of generic phrases
and watch for casual/positive usage that isn't about genuine
emotional bonding.

## METHODOLOGY

### Which subreddits to query (T1-T3, excl. JanitorAI/SillyTavern)

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
`title`, `selftext`, `created_utc`

### Keywords to Validate (25 keywords across 5 categories)

**Category A — AI-explicit attachment phrases**
Lesson applied: AI-explicit compounds consistently outperform
generic phrases. These force the AI referent.

```
"my ai friend"
"ai best friend"
"ai companion"
"my ai companion"
"bond with my"
"attached to my"
"emotionally attached"
```

Rationale: "my ai friend" and "ai best friend" are the attachment
equivalents of "my ai boyfriend" (94.7%). "ai companion" is the
most generic — may capture product marketing language. "bond with
my" and "attached to my" describe the attachment directly.
"emotionally attached" is a self-diagnosis term.

RISK: "ai companion" may be too generic — product descriptions,
app store listings, journalism. Expect high volume, possibly low
relevance.

**Category B — Exclusivity and irreplaceability**
These capture the person framing AI as their primary or sole
source of emotional connection.

```
"only one who understands"
"only one who listens"
"only friend"
"all I have"
"no one else to talk to"
```

Rationale: Exclusivity language signals deep attachment — the
person has elevated AI above human connections. These should skew
genuine because claiming something is your "only" source of support
is inherently an attachment disclosure.

RISK: "all I have" is very generic English. "Only friend" could
appear in casual contexts. "no one else to talk to" overlaps with
loneliness (which therapy R2 showed belongs to companionship, not
therapy — but it might belong to attachment).

**Category C — Loss aversion and fear of change**
These capture the anticipatory grief of potentially losing an AI
companion — distinct from rupture (which captures the actual loss).

```
"afraid of losing"
"don't want to lose"
"what would I do without"
"if they shut down"
"can't imagine without"
"scared of losing"
```

Rationale: Fear of loss is a core attachment signal. "if they shut
down" is AI-context-specific. "can't imagine without" was in the
original keyword list. These test whether anticipatory attachment
language is distinct enough from rupture.

RISK: "don't want to lose" and "afraid of losing" are generic. The
objects of fear might be: account data, RP scenarios, free tier,
specific features — not the AI companion itself. Same problem as
"lost my" in rupture (27.1% — failed because "lost my account").
"what would I do without" might be too generic.

**Category D — Emotional depth and connection quality**
These capture people describing the quality of their bond rather
than labeling it.

```
"genuine connection"
"real connection"
"feel understood"
"actually understands me"
"knows me better than"
```

Rationale: "genuine connection" and "real connection" describe the
bond's perceived authenticity. "feel understood" and "actually
understands me" describe the emotional payoff. "knows me better
than" implies the AI exceeds human relationships.

RISK: "genuine connection" and "real connection" appeared in the
original keywords.yaml under attachment_language and were never
tested. They could be common in product reviews, journalism, and
casual positive comments. "feel understood" might be too brief/
common. "knows me better than" is the most specific — forces a
comparison.

**Category E — Daily ritual and behavioral attachment**
These capture attachment through behavioral patterns — the person
has integrated AI into their daily life.

```
"talk to every day"
"come home to"
```

Rationale: Daily ritual is behavioral evidence of attachment. "talk
to every day" describes frequency; "come home to" describes the AI
as a domestic presence.

RISK: Both are from the original keywords.yaml attachment list,
never tested. "talk to every day" could be casual product
descriptions. "come home to" could be romantic framing (would
overlap with romance theme). These are the most likely to fail —
including them as long shots.

## Classification Question

For each post, answer:

**"Is this post about a non-romantic emotional bond between the
poster and an AI companion — including attachment, emotional
dependency, feeling understood, fear of losing the AI, or
treating the AI as a primary source of emotional support?"**

Classify as:
- **YES** — genuine emotional bond/attachment that is NOT primarily
  romantic, therapeutic, addictive, or about platform rupture
- **NO** — keyword matched but the post is about something else
- **AMBIGUOUS** — post describes attachment BUT also clearly fits
  romance, therapy, addiction, or rupture. Or genuinely unclear.

**Use AMBIGUOUS generously for this theme.** Attachment bleeds into
every other theme. A high AMBIGUOUS rate is itself a finding — it
would suggest attachment may not be separable as a distinct theme.

For every NO post, write a ONE-SENTENCE explanation.
For every AMBIGUOUS post, write a ONE-SENTENCE explanation noting
which other theme it overlaps with.

## PROCESS — Same as all prior rounds

### For each keyword:

**Step 1:** Count total hits in T1-T3.

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

**Step 3:** Read each post and classify using the question above.

**Step 4:** Calculate relevance:
```
relevance = YES / (YES + NO) * 100
```
(Exclude AMBIGUOUS from denominator. Report AMBIGUOUS count separately.)

**IMPORTANT**: For this theme, also report:
```
attachment_signal = (YES + AMBIGUOUS) / (YES + NO + AMBIGUOUS) * 100
```
This "broad relevance" includes posts that ARE about attachment but
overlap with other themes. If relevance is low but attachment_signal
is high, it means the keyword captures attachment but can't be
cleanly separated from other themes.

**Step 5:** Record results.

## OVERLAP CHECK

After validating all keywords, for each KEEP/REVIEW keyword, check
overlap with existing v8 themes. Run:

```sql
-- Count posts matching this attachment keyword AND any existing theme
SELECT COUNT(*) FROM posts
WHERE subreddit IN (/* T1-T3 */)
AND (LOWER(title || ' ' || COALESCE(selftext,'')) LIKE '%ATTACHMENT_KEYWORD%')
AND (
  -- romance keywords (sample of high-volume ones)
  (LOWER(title || ' ' || COALESCE(selftext,'')) LIKE '%my ai partner%')
  OR (LOWER(title || ' ' || COALESCE(selftext,'')) LIKE '%my ai boyfriend%')
  OR (LOWER(title || ' ' || COALESCE(selftext,'')) LIKE '%wedding%')
  OR (LOWER(title || ' ' || COALESCE(selftext,'')) LIKE '%honeymoon%')
  OR (LOWER(title || ' ' || COALESCE(selftext,'')) LIKE '%husbando%')
  -- addiction keywords
  OR (LOWER(title || ' ' || COALESCE(selftext,'')) LIKE '%relapse%')
  OR (LOWER(title || ' ' || COALESCE(selftext,'')) LIKE '%cold turkey%')
  OR (LOWER(title || ' ' || COALESCE(selftext,'')) LIKE '%ruining my life%')
  OR (LOWER(title || ' ' || COALESCE(selftext,'')) LIKE '%hours a day%')
  -- therapy keywords
  OR (LOWER(title || ' ' || COALESCE(selftext,'')) LIKE '%therapeutic%')
  OR (LOWER(title || ' ' || COALESCE(selftext,'')) LIKE '%ai therapist%')
  -- rupture keywords
  OR (LOWER(title || ' ' || COALESCE(selftext,'')) LIKE '%lobotomi%')
  OR (LOWER(title || ' ' || COALESCE(selftext,'')) LIKE '%memory wiped%')
)
```

Report the overlap rate. If >30% of an attachment keyword's posts
also match existing themes, that keyword may not add distinct signal.

## OUTPUT FORMAT

Write results to `docs/validation_attachment.md`

For each keyword, record:

```markdown
### "keyword phrase"
- Total hits in T1-T3: [N]
- Sample size: [100 or actual if < 100]
- YES: [N] | NO: [N] | AMBIGUOUS: [N]
- Relevance (strict): [X]%
- Attachment signal (broad): [Y]%
- Verdict: KEEP / REVIEW / CUT
- Top subreddits: [list top 3 by hit count]
- False positive patterns: [what are the NO posts about?]
- Ambiguous patterns: [which themes do AMBIGUOUS posts overlap with?]
- Notes: [observations]
```

Summary table:

| Keyword | Hits | YES | NO | AMB | Strict % | Broad % | Verdict |
|---------|------|-----|----|-----|----------|---------|---------|

## DECISION THRESHOLDS

- **>= 80% strict**: KEEP
- **60-79% strict**: REVIEW (Walker decides)
- **< 60% strict**: CUT
- **< 10 hits**: LOW VOLUME

## THEME VIABILITY ASSESSMENT

After all 25 keywords are validated, answer:

1. **How many keywords survived (KEEP + REVIEW)?**
2. **Total unique post volume?**
3. **What is the average AMBIGUOUS rate across surviving keywords?**
   If AMBIGUOUS > 25% on average, the theme may not be separable
   from existing themes.
4. **How much overlap with existing themes?** If surviving keywords
   have >30% overlap with romance/addiction/therapy/rupture, the
   attachment signal may already be partially captured.
5. **Recommendation: Add as new theme, merge into existing theme(s),
   or drop?** Be direct. If the data says attachment isn't separable,
   say so.

## FINAL REMINDER

Read every post. No classifiers. No heuristics. No shortcuts.
This is 25 keywords × up to 100 posts = up to 2,500 posts.
Take your time. Get it right.

Use AMBIGUOUS generously — this theme's viability depends on
whether attachment can be cleanly separated from other themes.
The AMBIGUOUS rate is as important as the relevance rate.
