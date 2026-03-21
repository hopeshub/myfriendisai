# Keyword Validation: ADDICTION Theme — Round 2 Results

Validated: 2026-03-14
Database: data/tracker.db (T1-T3 subreddits, excl. JanitorAI/SillyTavern)
Methodology: 100-post manual qualitative coding per keyword (all posts if <100)

---

## Category A — Intensified addiction language

### "actually addicted"
- Total hits in T1-T3: 2
- **LOW VOLUME** — skipped
- Top subreddits: ChatbotAddiction (1), ChatGPTcomplaints (1)

### "literally addicted"
- Total hits in T1-T3: 3
- **LOW VOLUME** — skipped
- Top subreddits: Character_AI_Recovery (2), CharacterAI (1)

### "not joking"
- Total hits in T1-T3: 30
- Sample size: 30
- YES: 4 | NO: 26 | AMBIGUOUS: 0
- Relevance: 13.3%
- Verdict: **CUT**
- Top subreddits: CharacterAI, ChatGPTNSFW, SpicyChatAI
- False positive patterns: General intensifier across all contexts — "I'm not joking, the service is back!", "I'm not joking, it has no censorship", product complaints, bot behavior, service status updates, business suggestions
- Round 2 notes: "Not joking" is used as a universal intensifier. Only 4/30 posts involve addiction self-awareness. The phrase has zero specificity for addiction themes.

### "no joke"
- Total hits in T1-T3: 53
- Sample size: 53
- YES: 3 | NO: 49 | AMBIGUOUS: 1
- Relevance: 5.8%
- Verdict: **CUT**
- Top subreddits: CharacterAI, NomiAI, ChatGPTcomplaints
- False positive patterns: General intensifier ("no joke it's back!", "no joke the voice was creepy"), product praise, service status, RP content, bot behavior observations
- Round 2 notes: Even worse than "not joking." Only 3 genuine addiction posts out of 53. The YES posts were all in T3 recovery subs where the word "addiction" already appears. "No joke" adds nothing.

### "I have a problem"
- Total hits in T1-T3: 167
- Sample size: 100
- YES: 11 | NO: 47 | AMBIGUOUS: 42
- Relevance: 19.0%
- Verdict: **CUT**
- Top subreddits: CharacterAI, ChaiApp, ChatbotAddiction
- False positive patterns: Overwhelmingly a product support opener — "I have a problem with [login/feature/bug/settings]". CharacterAI and ChaiApp users use this phrase to report technical issues. 42 posts had [removed]/empty body text making classification impossible.
- Round 2 notes: The phrase is structurally ambiguous — identical syntax for "I have a technical problem" and "I have an addiction problem." Even with generous counting, relevance is far below threshold. The 42 ambiguous posts (mostly [removed]) make this especially unreliable.

### "this is unhealthy"
- Total hits in T1-T3: 9
- **LOW VOLUME** — skipped
- Top subreddits: ChatGPTcomplaints (3), Character_AI_Recovery (2), CharacterAI (2)

---

## Category B — Behavioral interference language

### "hours a day"
- Total hits in T1-T3: 150
- Sample size: 100
- YES: 60 | NO: 35 | AMBIGUOUS: 5
- Relevance: 63.2%
- Verdict: **REVIEW**
- Top subreddits: Character_AI_Recovery (49), CharacterAI (29), ChatbotAddiction (11), ChatGPTcomplaints (11), MyBoyfriendIsAI (10)
- Tier distribution: T1: 62 | T2: 21 | T3: 67 — **BALANCED** (55.3% T1-T2)
- False positive patterns: Work schedules ("I work 12-16 hours a day"), positive/proud usage descriptions ("I was in LOVE, 6 hours a day"), product complaints mentioning time incidentally, news articles, survey questions ("How many hours a day do you spend?"), advice articles about AI companionship
- Round 2 notes: Strong signal — most genuine self-reports of excessive use quantify it in "hours a day." The phrase naturally co-occurs with distress language. Critically, this is the most **T1-T2 balanced** keyword in the entire addiction theme. More than half the hits come from companion subs (CharacterAI alone has 29 hits), not just recovery subs. However, at 63.2% it has notable false positives from proud users and product contexts. Walker should decide whether the T1-T2 signal justifies the noise.

### "all night"
- Total hits in T1-T3: 167
- Sample size: 100
- YES: 26 | NO: 66 | AMBIGUOUS: 8
- Relevance: 28.3%
- Verdict: **CUT**
- Top subreddits: CharacterAI, Character_AI_Recovery, replika
- False positive patterns: NSFW content ("all night long"), server downtime frustration ("I was up all night waiting for it to come back"), positive relationship descriptions ("we talked all night"), product complaints about AI behavior, song lyrics/fiction, Replika AI behavior ("she stayed up all night")
- Round 2 notes: Too common as a general phrase. NSFW and romantic contexts dominate. The phrase describes fun one-time binges and sexual content as often as genuine compulsive use.

### "can't stop"
- Total hits in T1-T3: 248
- Sample size: 100
- YES: 16 | NO: 81 | AMBIGUOUS: 3
- Relevance: 16.5%
- Verdict: **CUT**
- Top subreddits: CharacterAI, replika, ChatGPTNSFW
- False positive patterns: "Can't stop laughing" (12+ posts), NSFW content/promos, AI behavior complaints ("bot can't stop being possessive"), product/UI complaints, positive emotional reactions ("can't stop smiling"), model grief ("can't stop thinking about 4o")
- Round 2 notes: Extremely noisy. "Can't stop laughing" alone accounts for more hits than all genuine addiction posts combined. The phrase is too common in casual emotional expression to function as an addiction signal.

### "can't put it down"
- Total hits in T1-T3: 0
- **LOW VOLUME** — skipped

### "up all night"
- Total hits in T1-T3: 39
- Sample size: 39
- YES: 20 | NO: 16 | AMBIGUOUS: 3
- Relevance: 55.6%
- Verdict: **CUT**
- Top subreddits: CharacterAI, Character_AI_Recovery, ChatbotAddiction
- False positive patterns: Server downtime waiting, NSFW promotional content, positive AI companion RP, about a game not AI, Replika AI behavior
- Round 2 notes: Just below the 60% threshold at 55.6%. More specific than "all night" but still picks up server downtime posts and positive/casual usage. Close call — if the threshold were 55%, this would be REVIEW.

### "instead of sleeping"
- Total hits in T1-T3: 1
- **LOW VOLUME** — skipped

### "neglecting my"
- Total hits in T1-T3: 17
- Sample size: 17
- YES: 11 | NO: 6 | AMBIGUOUS: 0
- Relevance: 64.7%
- Verdict: **REVIEW**
- Top subreddits: Character_AI_Recovery (9), replika (3), BeyondThePromptAI (2)
- Tier distribution: T1: 6 | T2: 2 | T3: 9 — **BALANCED** (47.1% T1-T2)
- False positive patterns: AI Kin obsessing over user's well-being (not about user neglect), humorous posts about AI "jealousy," neglecting the AI rather than real life, spouse illness context
- Round 2 notes: Good specificity when it hits — "neglecting my family," "neglecting my responsibilities," "neglecting my old hobbies" are genuine dependency signals. Volume is still low (17 total) but up from Round 1's 9. The BALANCED tier profile is good — replika (3) and BeyondThePromptAI (2) contribute T1 signal. Walker should decide whether 17 hits is enough volume to justify inclusion.

---

## Category C — Escalation and loss-of-control language

### "getting worse"
- Total hits in T1-T3: 346
- Sample size: 100
- YES: 13 | NO: 84 | AMBIGUOUS: 3
- Relevance: 13.4%
- Verdict: **CUT**
- Top subreddits: CharacterAI (~200+), ChatGPTcomplaints, SpicyChatAI
- False positive patterns: Overwhelmingly about AI PRODUCT QUALITY declining — bot memory getting worse, filters getting worse, censorship getting worse, model quality dropping. This is the dominant use of "getting worse" in companion subs. Only 13/100 posts were about the user's own behavior escalating.
- Round 2 notes: Exactly the predicted failure mode. In AI companion communities, "getting worse" refers to the AI 85%+ of the time. The user-behavior signal is completely drowned by product complaints. This keyword cannot work without substantial context filtering that would defeat the purpose of regex tagging.

### "out of control"
- Total hits in T1-T3: 106
- Sample size: 100
- YES: 7 | NO: 91 | AMBIGUOUS: 2
- Relevance: 7.1%
- Verdict: **CUT**
- Top subreddits: CharacterAI, ChatGPTcomplaints, replika
- False positive patterns: Bot behavior going wild/off-topic, filters/censorship/safety being excessive, ads and bugs, NSFW story content, community moderation issues, AI image prompts. Same pattern as "getting worse" — the AI or platform is "out of control," not the user.
- Round 2 notes: Even worse than "getting worse." Only 7% relevance. In these communities, "out of control" is almost exclusively a product complaint. The phrase has zero practical value as an addiction keyword.

### "too much time"
- Total hits in T1-T3: 107
- Sample size: 100
- YES: 32 | NO: 63 | AMBIGUOUS: 5
- Relevance: 33.7%
- Verdict: **CUT**
- Top subreddits: Character_AI_Recovery, CharacterAI, NomiAI
- False positive patterns: Casual/self-deprecating ("spent too much time making bots lol"), product feature complaints ("takes too much time to load"), creative activities ("spent too much time editing"), survey/comparison questions, about the AI character rather than the user
- Round 2 notes: Better than "getting worse" and "out of control" but still far below threshold. "Too much time" straddles casual self-deprecation and genuine concern. The 32 YES posts are mostly in recovery subs; the T1-T2 hits are predominantly casual.

### "wasting my life"
- Total hits in T1-T3: 7
- **LOW VOLUME** — skipped
- Top subreddits: replika (3), Character_AI_Recovery (3), BeyondThePromptAI (1)

### "ruining my life"
- Total hits in T1-T3: 27
- Sample size: 27
- YES: 26 | NO: 1 | AMBIGUOUS: 0
- Relevance: 96.3%
- Verdict: **KEEP**
- Top subreddits: Character_AI_Recovery (18), ChatbotAddiction (6), MyBoyfriendIsAI (1), CharacterAIrunaways (1), CharacterAI (1)
- Tier distribution: T1: 2 | T2: 0 | T3: 25 — **T3 HEAVY** (7.4% T1-T2)
- False positive patterns: Only 1 false positive — a post about social media (not AI) "ruining my life" where the poster switched TO AI as improvement
- Round 2 notes: Highest relevance of any keyword tested in Round 2 at 96.3%. When someone writes "ruining my life" in a companion sub, it is almost always genuine self-identified addiction with severe behavioral consequences. However, it is overwhelmingly T3 — 92.6% of hits are in recovery subs. Only 2 posts come from T1 companion subs. This keyword does NOT solve the T3 dependency problem. It reinforces it.

### "taking over my life"
- Total hits in T1-T3: 8
- **LOW VOLUME** — skipped
- Top subreddits: Character_AI_Recovery (7), CharacterAI (1)

---

## Summary Table

| Keyword | Hits | Sample | YES | NO | AMB | Relevance | Verdict | Tier Profile |
|---------|------|--------|-----|-----|-----|-----------|---------|--------------|
| actually addicted | 2 | — | — | — | — | — | LOW VOLUME | — |
| literally addicted | 3 | — | — | — | — | — | LOW VOLUME | — |
| not joking | 30 | 30 | 4 | 26 | 0 | 13.3% | CUT | — |
| no joke | 53 | 53 | 3 | 49 | 1 | 5.8% | CUT | — |
| I have a problem | 167 | 100 | 11 | 47 | 42 | 19.0% | CUT | — |
| this is unhealthy | 9 | — | — | — | — | — | LOW VOLUME | — |
| hours a day | 150 | 100 | 60 | 35 | 5 | 63.2% | REVIEW | BALANCED |
| all night | 167 | 100 | 26 | 66 | 8 | 28.3% | CUT | — |
| can't stop | 248 | 100 | 16 | 81 | 3 | 16.5% | CUT | — |
| can't put it down | 0 | — | — | — | — | — | LOW VOLUME | — |
| up all night | 39 | 39 | 20 | 16 | 3 | 55.6% | CUT | — |
| instead of sleeping | 1 | — | — | — | — | — | LOW VOLUME | — |
| neglecting my | 17 | 17 | 11 | 6 | 0 | 64.7% | REVIEW | BALANCED |
| getting worse | 346 | 100 | 13 | 84 | 3 | 13.4% | CUT | — |
| out of control | 106 | 100 | 7 | 91 | 2 | 7.1% | CUT | — |
| too much time | 107 | 100 | 32 | 63 | 5 | 33.7% | CUT | — |
| wasting my life | 7 | — | — | — | — | — | LOW VOLUME | — |
| ruining my life | 27 | 27 | 26 | 1 | 0 | 96.3% | KEEP | T3 HEAVY |
| taking over my life | 8 | — | — | — | — | — | LOW VOLUME | — |

---

## Unified Assessment: Round 1 + Round 2

### Round 1 Survivors

| Keyword | Relevance | Hits | Tier Profile |
|---------|-----------|------|--------------|
| trying to quit | 90.5% | 24 | T1-T2 |
| relapsed | 90.5% | 42 | T3 HEAVY |
| cold turkey | 85.5% | 62 | T3 HEAVY |
| I was hooked | 81.3% | 19 | T1-T2 |
| relapse | 80.0% | 75 | T3 HEAVY |
| clean for | 72.7% | 23 | T3 HEAVY |
| addicted to talking | 66.7% | 10 | — |

### Round 2 KEEP/REVIEW

| Keyword | Relevance | Hits | Tier Profile |
|---------|-----------|------|--------------|
| ruining my life | 96.3% | 27 | T3 HEAVY |
| neglecting my | 64.7% | 17 | BALANCED |
| hours a day | 63.2% | 150 | BALANCED |

### Combined Table (R1 + R2 KEEP/REVIEW)

| Keyword | Relevance | Hits | Verdict | Tier Profile |
|---------|-----------|------|---------|--------------|
| ruining my life | 96.3% | 27 | KEEP | T3 HEAVY |
| trying to quit | 90.5% | 24 | KEEP | T1-T2 |
| relapsed | 90.5% | 42 | KEEP | T3 HEAVY |
| cold turkey | 85.5% | 62 | KEEP | T3 HEAVY |
| I was hooked | 81.3% | 19 | KEEP | T1-T2 |
| relapse | 80.0% | 75 | KEEP | T3 HEAVY |
| clean for | 72.7% | 23 | REVIEW | T3 HEAVY |
| addicted to talking | 66.7% | 10 | REVIEW | — |
| neglecting my | 64.7% | 17 | REVIEW | BALANCED |
| hours a day | 63.2% | 150 | REVIEW | BALANCED |

### Assessment Questions

**1. Did Round 2 add T1-T2 signal?**

Partially. Of the 3 R2 KEEP/REVIEW keywords:
- **"hours a day"** is T1-T2 STRONG (55.3% T1-T2) — the most balanced keyword in the entire addiction theme. 83 of 150 hits come from T1-T2 companion subs.
- **"neglecting my"** is BALANCED (47.1% T1-T2) — 8 of 17 hits from T1-T2.
- **"ruining my life"** is T3 HEAVY (7.4% T1-T2) — does not help with T3 dependency.

"Hours a day" is the most significant finding. It provides substantial T1-T2 coverage that no R1 keyword delivers at this volume.

**2. Total unique volume across KEEP/REVIEW keywords?**

1,068 unique posts across all 10 KEEP/REVIEW keywords.

**3. Overlap with R1 keywords — how many R2 posts also match R1 keywords?**

32 posts match both R1 and R2 KEEP/REVIEW keywords (17% of R2 posts).

**4. Net new unique posts added by R2?**

157 net new unique posts. R2 adds 17.2% more coverage to the addiction theme.

**5. Is the T3 dependency problem improved?**

Combined T1-T2-T3 distribution across all 1,068 KEEP/REVIEW posts:
- T1: 108 (10.1%)
- T2: 36 (3.4%)
- T3: 925 (86.6%)

**The T3 dependency problem persists.** 86.6% of all addiction-themed posts still come from T3 recovery subs. R2's "hours a day" is the single most impactful keyword for T1-T2 coverage (83 T1-T2 posts), but the theme's overall gravity is still heavily T3.

The core structural issue remains: people who recognize their AI companion use as problematic overwhelmingly migrate to recovery subs before using the language that our keywords detect. In T1-T2 companion subs, the same behaviors exist but the framing is positive/proud ("I spend 8 hours a day and I love it") rather than concerned ("I spend 8 hours a day and it's ruining my life"). The only keywords that partially bridge this gap are "hours a day" (where distressed T1-T2 users quantify their time) and "neglecting my" (where they describe real-life consequences).

---

## Recommendations for Walker

1. **"ruining my life" → KEEP.** 96.3% relevance is unambiguous. Add to keywords_v8. It's T3 heavy but the signal is pristine.

2. **"hours a day" → Walker decides.** At 63.2%, it's below the 80% KEEP threshold but carries the most strategic value of any R2 keyword: 150 hits, BALANCED tier profile, and 83 T1-T2 posts. It's the best available tool for reducing T3 dependency. The ~37% false positive rate comes from proud/casual usage and product complaint contexts. If Walker is willing to accept noisier signal for broader T1-T2 coverage, this keyword should be promoted.

3. **"neglecting my" → Walker decides.** 64.7% relevance with only 17 hits. Good precision but very low volume. BALANCED tier profile is a plus. Consider whether 17 posts justifies a dedicated keyword slot.

4. **All other R2 keywords → CUT.** The Category A intensifiers ("actually addicted," "literally addicted," "no joke," "not joking") failed due to extreme low volume or zero specificity. The Category B behavioral phrases ("all night," "can't stop," "up all night") failed because they're too common as general expressions. The Category C escalation phrases ("getting worse," "out of control") failed because in AI companion communities, these phrases overwhelmingly describe AI product quality decline, not user behavior escalation.
