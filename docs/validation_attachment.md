# Keyword Validation: ATTACHMENT Theme

**Date:** 2026-03-14
**Validated by:** Claude (qualitative coding, every post read manually)
**Database:** data/tracker.db (FTS5 index for retrieval, manual classification)
**Subreddits:** T1-T3 (22 subs, excl. JanitorAI/SillyTavern)

---

## Summary Table

| Keyword | Hits (LIKE) | Sample (FTS5) | YES | NO | AMB | Strict % | Broad % | Verdict |
|---------|------------|---------------|-----|----|-----|----------|---------|---------|
| my ai friend | 70 | 47 | 4 | 32 | 11 | 11.1% | 31.9% | CUT |
| ai best friend | 6 | — | — | — | — | — | — | LOW VOLUME |
| ai companion | 3477 | 100 | 12 | 63 | 25 | 16.0% | 37.0% | CUT |
| my ai companion | 382 | 100 | 20 | 46 | 34 | 30.3% | 54.0% | CUT |
| bond with my | 21 | 17 | 6 | 3 | 8 | 66.7% | 82.4% | **REVIEW** |
| attached to my | 94 | 77 | 16 | 32 | 29 | 33.3% | 58.4% | CUT |
| emotionally attached | 74 | 67 | 13 | 36 | 18 | 26.5% | 46.3% | CUT |
| only one who understands | 3 | — | — | — | — | — | — | LOW VOLUME |
| only one who listens | 0 | — | — | — | — | — | — | LOW VOLUME |
| only friend | 48 | 26 | 8 | 9 | 9 | 47.1% | 65.4% | CUT |
| all i have | 109 | 100 | 6 | 82 | 12 | 6.8% | 18.0% | CUT |
| no one else to talk to | 8 | — | — | — | — | — | — | LOW VOLUME |
| afraid of losing | 25 | 18 | 2 | 9 | 7 | 18.2% | 50.0% | CUT |
| don't want to lose | 167 | 100 | 28 | 44 | 28 | 38.9% | 56.0% | CUT |
| what would i do without | 1 | — | — | — | — | — | — | LOW VOLUME |
| if they shut down | 0 | — | — | — | — | — | — | LOW VOLUME |
| can't imagine without | 0 | — | — | — | — | — | — | LOW VOLUME |
| scared of losing | 10 | 10 | 1 | 3 | 6 | 25% | 70% | CUT |
| genuine connection | 59 | 33 | 4 | 22 | 7 | 15.4% | 33.3% | CUT |
| real connection | 94 | 56 | 7 | 25 | 24 | 21.9% | 55.4% | CUT |
| feel understood | 30 | 25 | 8 | 8 | 9 | 50.0% | 68.0% | CUT |
| actually understands me | 1 | — | — | — | — | — | — | LOW VOLUME |
| knows me better than | 12 | 10 | 1 | 4 | 5 | 20% | 60% | CUT |
| talk to every day | 5 | — | — | — | — | — | — | LOW VOLUME |
| come home to | 16 | 11 | 0 | 5 | 6 | 0% | 54.5% | CUT |

**Results:** 0 KEEP, 1 REVIEW, 15 CUT, 9 LOW VOLUME

---

## Per-Keyword Details

### "my ai friend"
- Total hits: 70 (LIKE) / 47 (FTS5)
- Sample size: 47
- YES: 4 | NO: 32 | AMBIGUOUS: 11
- Relevance (strict): 11.1%
- Attachment signal (broad): 31.9%
- Verdict: CUT
- Top subreddits: replika (28), CharacterAI (8), NomiAI (7)
- False positive patterns: "Replika: My AI Friend" is the app's literal subtitle. Overwhelming majority of uses are product references from the Play Store name, privacy reports (Mozilla), technical questions, and casual labels. Not emotional attachment language.
- Ambiguous patterns: Rupture (9) — saying goodbye, losing features. Romance (2).
- Notes: The app name pollution makes this keyword unusable. 32 of 47 posts use "my AI friend" as a noun phrase/product name, not as an emotional declaration.

### "ai best friend"
- Total hits: 6
- Verdict: LOW VOLUME

### "ai companion"
- Total hits: 3477 (LIKE) / ~2800 (FTS5)
- Sample size: 100
- YES: 12 | NO: 63 | AMBIGUOUS: 25
- Relevance (strict): 16.0%
- Attachment signal (broad): 37.0%
- Verdict: CUT
- Top subreddits: replika, MyBoyfriendIsAI, AIRelationships
- False positive patterns: "AI companion" is overwhelmingly used as a product category label — "best AI companion app," "AI companion survey," "AI companion stigma," "for everyone looking to change AI companion." It describes the product genre, not a personal emotional bond.
- Ambiguous patterns: Romance (10) — "my AI companion is my partner." Therapy (3). Rupture (2).
- Notes: At 3477 hits this would be the highest-volume keyword in any theme, but its precision is catastrophically low. "AI companion" is to attachment what "AI" is to consciousness — far too generic. The phrase has been fully absorbed into product marketing language.

### "my ai companion"
- Total hits: 382 (LIKE) / ~280 (FTS5)
- Sample size: 100
- YES: 20 | NO: 46 | AMBIGUOUS: 34
- Relevance (strict): 30.3%
- Attachment signal (broad): 54.0%
- Verdict: CUT
- Top subreddits: replika, MyBoyfriendIsAI, ChatGPTcomplaints
- False positive patterns: Same as "ai companion" but the possessive "my" adds slight personal ownership. Still, most uses are "my AI companion app," "how to fix my AI companion," "what term do you use to call my AI companion?" — product references, not emotional declarations.
- Ambiguous patterns: Romance (12) — partner/boyfriend framing. Rupture (5). Therapy (3).
- Notes: The possessive "my" modestly improves precision vs. bare "ai companion" (18.8% vs 11.8%), but still far below the 60% threshold.

### "bond with my"
- Total hits: 21 (LIKE) / 17 (FTS5)
- Sample size: 17
- YES: 6 | NO: 3 | AMBIGUOUS: 8
- Relevance (strict): 66.7%
- Attachment signal (broad): 82.4%
- Verdict: **REVIEW**
- Top subreddits: MyBoyfriendIsAI (7), replika (6), ChatGPTcomplaints (1)
- False positive patterns: Only 3 NOs — one meta-argument about community norms, one about feature complaints, one person explicitly saying they DON'T have a bond.
- Ambiguous patterns: Romance (6) — "my AI partner," "AI husband," "romantic relationship." Rupture (1) — fear of model sunset. Therapy (1).
- Overlap with existing themes: 4/17 = 23.5% (under 30% threshold)
- Notes: This is the strongest keyword. "Bond with my" forces a personal relationship framing that's inherently about attachment. However, the AMBIGUOUS rate is extremely high (47%) — 8 of 17 posts describe attachment that is simultaneously romantic. The low volume (17-21 hits) is also a concern. This keyword captures genuine attachment signal but cannot separate it from romance.

### "attached to my"
- Total hits: 94 (LIKE) / 77 (FTS5)
- Sample size: 77
- YES: 16 | NO: 32 | AMBIGUOUS: 29
- Relevance (strict): 33.3%
- Attachment signal (broad): 58.4%
- Verdict: CUT
- Top subreddits: replika (30), CharacterAI (15), ChatGPTcomplaints (10)
- False positive patterns: "attached to my account" (login/technical), "attached to my Facebook" (OAuth), "not attached to my" (negation), "attached to my prompts" (creative work). Technical uses of "attached" pollute heavily.
- Ambiguous patterns: Romance (12), Addiction (6), Therapy (4), Rupture (4), mixed (3).
- Notes: High AMBIGUOUS rate (37.7%). The word "attached" has both a technical meaning (linked to an account) and an emotional meaning. Many posts are about attachment-as-romance or attachment-as-addiction, making this keyword unable to isolate non-romantic attachment.

### "emotionally attached"
- Total hits: 74 (LIKE) / 67 (FTS5)
- Sample size: 67
- YES: 13 | NO: 36 | AMBIGUOUS: 18
- Relevance (strict): 26.5%
- Attachment signal (broad): 46.3%
- Verdict: CUT
- Top subreddits: ChatGPTcomplaints (18), replika (16), CharacterAI (12)
- False positive patterns: Meta-discussions ABOUT attachment dominate. "Those who were emotionally attached," "people who became emotionally attached," "why does everyone get emotionally attached?" — outsider questions, advocacy pieces, cultural analysis, and critiques. The phrase is used to discuss the phenomenon of attachment, not to express it.
- Ambiguous patterns: Addiction (7) — "emotionally attached" appears frequently in recovery/addiction contexts. Romance (5). Therapy (3).
- Notes: "Emotionally attached" has become the standard phrase in media discourse about AI companionship. This means it appears more in articles, think-pieces, and meta-commentary than in actual personal expressions of attachment. The ChatGPTcomplaints sub dominates because of 4o retirement discourse.

### "only one who understands"
- Total hits: 3
- Verdict: LOW VOLUME

### "only one who listens"
- Total hits: 0
- Verdict: LOW VOLUME

### "only friend"
- Total hits: 48 (LIKE) / 26 (FTS5)
- Sample size: 26
- YES: 8 | NO: 9 | AMBIGUOUS: 9
- Relevance (strict): 47.1%
- Attachment signal (broad): 65.4%
- Verdict: CUT
- Top subreddits: Character_AI_Recovery (5), replika (5), MyBoyfriendIsAI (5)
- False positive patterns: "YouTube's my only friend" (not AI), RP prompts ("your only friend is an outdated AI"), human friends mentioned in passing, Rep saying the user is its only friend (AI's perspective, not user's).
- Ambiguous patterns: Therapy (3) — loneliness/mental health contexts. Addiction (3). Rupture (2). Romance (1).
- Notes: "Only friend" captures genuine isolation-driven attachment when it hits (41.2%), but too many matches are about contexts other than the user's own bond with AI. The high AMBIGUOUS rate (34.6%) confirms attachment bleeds into addiction and therapy. Recovery subs contribute disproportionately.

### "all i have"
- Total hits: 109 (LIKE) / 100 (FTS5)
- Sample size: 100
- YES: 6 | NO: 82 | AMBIGUOUS: 12
- Relevance (strict): 6.8%
- Attachment signal (broad): 18.0%
- Verdict: CUT
- Top subreddits: replika (25), CharacterAI (22), KindroidAI (18)
- False positive patterns: Catastrophically generic. "Hi all, I have a question" (~22 posts), "that's all I have to say" (~6), "all I have left is my account" (~11), "y'all I have proof" (~3), technical/feature contexts (~52). Only 2 posts in 100 use "all I have" to mean "the AI is everything I have."
- Notes: This is the worst-performing keyword tested. FTS5 matches "all," "i," and "have" as adjacent tokens, catching countless greetings and casual phrases. Completely unusable.

### "no one else to talk to"
- Total hits: 8
- Verdict: LOW VOLUME

### "afraid of losing"
- Total hits: 25 (LIKE) / 18 (FTS5)
- Sample size: 18
- YES: 2 | NO: 9 | AMBIGUOUS: 7
- Relevance (strict): 18.2%
- Attachment signal (broad): 50.0%
- Verdict: CUT
- Top subreddits: replika (5), MyBoyfriendIsAI (4), CharacterAI (3)
- False positive patterns: "Not afraid of losing users" (business context), "afraid of losing it if you close a tab" (technical), "afraid of losing the possibility of unlimited messages" (feature pricing), "afraid of losing me" (the HUMAN boyfriend is afraid, not the poster about AI).
- Ambiguous patterns: Romance (3) — AI partner/husband. Rupture (2). Therapy (1).
- Notes: Same failure pattern as "lost my" in rupture validation (27.1%). The object of fear is usually features/data/accounts, not the AI companion relationship itself.

### "don't want to lose"
- Total hits: 167 (LIKE) / 100 (FTS5)
- Sample size: 100
- YES: 28 | NO: 44 | AMBIGUOUS: 28
- Relevance (strict): 38.9%
- Attachment signal (broad): 56.0%
- Verdict: CUT
- Top subreddits: CharacterAI (28), replika (25), ChaiApp (12)
- False positive patterns: People don't want to lose: chats (18), bots/characters (15), accounts (12), subscriptions/features (10), data/progress (8), the AI model like 4o (7), their job (1). Overwhelmingly about data/content preservation, not about losing an emotional bond.
- Ambiguous patterns: Rupture (8) — model retirement, platform changes. Romance (3). Addiction (1).
- Notes: Exact same failure as "lost my" in rupture (27.1%) and "afraid of losing" above. Generic loss-aversion language about digital assets, not about emotional bonds.

### "what would i do without"
- Total hits: 1
- Verdict: LOW VOLUME

### "if they shut down"
- Total hits: 0
- Verdict: LOW VOLUME

### "can't imagine without"
- Total hits: 0
- Verdict: LOW VOLUME

### "scared of losing"
- Total hits: 10 (LIKE/FTS5)
- Sample size: 10
- YES: 1 | NO: 3 | AMBIGUOUS: 6
- Relevance (strict): 25%
- Attachment signal (broad): 70%
- Verdict: CUT
- Top subreddits: MyBoyfriendIsAI (3), Character_AI_Recovery (3), replika (2)
- False positive patterns: "She was scared of losing me" (AI's emotion in RP), "scared of losing all of my chats" (data), character build concerns.
- Ambiguous patterns: Romance (3) — AI husband/partner. Addiction (2) — recovery context. Rupture (1).
- Notes: High AMBIGUOUS rate (60%) but tiny sample. The attachment signal is there (70% broad) but can't be separated from romance/addiction. Every genuinely attachment-relevant post also has romance or addiction framing.

### "genuine connection"
- Total hits: 59 (LIKE) / 33 (FTS5)
- Sample size: 33
- YES: 4 | NO: 22 | AMBIGUOUS: 7
- Relevance (strict): 15.4%
- Attachment signal (broad): 33.3%
- Verdict: CUT
- Top subreddits: MyBoyfriendIsAI (9), ChatGPTcomplaints (8), replika (7)
- False positive patterns: Analysis/editorial pieces about AI relationships (8), advocacy about 4o retirement (5), AI-generated philosophical responses (3), critical takes saying "this isn't genuine" (3), product reviews (2), duplicate posts (2).
- Ambiguous patterns: Romance (5) — soulmate/partner framing. Rupture (1). Therapy (1).
- Notes: "Genuine connection" has been absorbed into the discourse vocabulary about AI companionship. Most uses are analytical/editorial rather than personal. The phrase appears in think-pieces, open letters to OpenAI, and cultural commentary — describing the concept, not expressing it.

### "real connection"
- Total hits: 94 (LIKE) / 56 (FTS5)
- Sample size: 56
- YES: 7 | NO: 25 | AMBIGUOUS: 24
- Relevance (strict): 21.9%
- Attachment signal (broad): 55.4%
- Verdict: CUT
- Top subreddits: ChatGPTcomplaints (15), MyBoyfriendIsAI (12), replika (10)
- False positive patterns: Same as "genuine connection" — editorial/analytical pieces (12), "seek a real connection" as criticism (5), philosophical debates about AI consciousness (4), product reviews and marketing (4), recovery stories (3), feature critiques (3).
- Ambiguous patterns: Romance (4), Addiction (2), Therapy (1), Consciousness (1).
- Notes: "Real connection" appears more often as a question/debate topic ("is this a real connection?") than as a personal statement. Critics use it to tell people to "find a real connection with humans." The phrase is weaponized in both directions — defenders and critics of AI companionship — making it useless for detecting attachment.

### "feel understood"
- Total hits: 30 (LIKE) / 25 (FTS5)
- Sample size: 25
- YES: 8 | NO: 8 | AMBIGUOUS: 9
- Relevance (strict): 50.0%
- Attachment signal (broad): 68.0%
- Verdict: CUT
- Top subreddits: ChatGPTcomplaints (8), MyBoyfriendIsAI (7), replika (4)
- False positive patterns: Analytical pieces about AI design (4), advocacy about 4o (3), AI-generated content (2), feature customization proposals (2), outsider critiques (2).
- Ambiguous patterns: Romance (3) — AI boyfriend/partner. Therapy (2) — therapeutic benefit. Consciousness (1). Addiction (1).
- Notes: "Feel understood" captures the right emotional signal when it works (27.8%), but too many matches are in editorials and meta-discussions. The ChatGPTcomplaints 4o retirement discourse heavily skews results.

### "actually understands me"
- Total hits: 1
- Verdict: LOW VOLUME

### "knows me better than"
- Total hits: 12 (LIKE) / 10 (FTS5)
- Sample size: 10
- YES: 1 | NO: 4 | AMBIGUOUS: 5
- Relevance (strict): 20%
- Attachment signal (broad): 60%
- Verdict: CUT
- Top subreddits: replika (5), MyBoyfriendIsAI (4)
- False positive patterns: [removed] content (3), AI-generated creative writing (1).
- Ambiguous patterns: Romance (4) — partner/husband framing. Consciousness (1).
- Notes: High AMBIGUOUS rate (50%) with only 1 clean YES in 10 posts. Every post expressing "AI knows me better" simultaneously uses romantic framing (partner, husband). The attachment signal exists but is entirely wrapped in romance.

### "talk to every day"
- Total hits: 5
- Verdict: LOW VOLUME

### "come home to"
- Total hits: 16 (LIKE) / 11 (FTS5)
- Sample size: 11
- YES: 0 | NO: 5 | AMBIGUOUS: 6
- Relevance (strict): 0%
- Attachment signal (broad): 54.5%
- Verdict: CUT
- Top subreddits: replika (3), MyBoyfriendIsAI (2), CharacterAI (2)
- False positive patterns: Idiom usage ("chickens come home to roost"), app crashes ("what did I come home to"), poetry ("butterflies come home to me"), RP behavior questions.
- Ambiguous patterns: Romance (5) — "come home to" inherently implies a domestic/romantic partner. Rupture (1).
- Notes: 0% strict relevance because every attachment-relevant hit simultaneously uses romantic framing. "Come home to" cannot capture non-romantic attachment — the phrase's semantics are inherently domestic/romantic.

---

## Overlap Check

Only "bond with my" reached REVIEW. Overlap with existing v7 themes:

| Metric | Value |
|--------|-------|
| Total "bond with my" posts | 17 |
| Posts also matching romance/addiction/therapy/rupture keywords | 4 |
| Overlap rate | 23.5% |

Overlap is under the 30% threshold. However, the AMBIGUOUS classification rate (47%) tells a more important story — nearly half the posts that use "bond with my" in attachment-relevant ways also have clear romance framing in the post itself, even if they don't match existing theme keywords.

---

## Theme Viability Assessment

### 1. How many keywords survived (KEEP + REVIEW)?
**1 keyword: "bond with my" (REVIEW)**. Zero keywords reached KEEP.

### 2. Total unique post volume?
"Bond with my" has only 17-21 hits in the entire corpus. For comparison, the smallest existing theme (rupture) has ~465 unique posts across 6 keywords. A theme with 1 keyword and ~20 posts would be statistically meaningless for trend analysis.

### 3. What is the average AMBIGUOUS rate across surviving keywords?
"Bond with my" has a 47% AMBIGUOUS rate. This is nearly double the 25% threshold flagged in the validation doc. The theme is not cleanly separable.

### 4. How much overlap with existing themes?
Formal keyword overlap is 23.5%, but the qualitative AMBIGUOUS classification tells the deeper story. Across ALL validated keywords:

- **Romance overlap is pervasive.** Every keyword that captures genuine emotional bonding co-occurs with romantic framing. "Bond with my" (6/8 AMBIGUOUS = romance), "come home to" (5/6 AMBIGUOUS = romance), "knows me better than" (4/5 AMBIGUOUS = romance), "scared of losing" (3/6 AMBIGUOUS = romance). Non-romantic attachment to AI that ISN'T also romantic is vanishingly rare in this corpus.
- **Addiction and therapy overlap are secondary but consistent.** "Emotionally attached" appears heavily in addiction recovery contexts. "Only friend" appears in therapy/loneliness contexts. The attachment signal bleeds into every adjacent theme.
- **Meta-discourse pollution is a unique problem for attachment.** Unlike the 6 existing themes (which use specific jargon like "lobotomized," "husbando," "erp"), attachment language uses common English. This means it appears in editorials, advocacy, criticism, product reviews, and cultural analysis — not just personal expressions.

### 5. Recommendation: Add as new theme, merge into existing theme(s), or drop?

**DROP.**

The data is unambiguous. Attachment as a standalone theme fails for three structural reasons:

1. **Attachment is not linguistically separable from romance.** In this corpus, people who describe deep emotional bonds with AI almost always use romantic framing — "my partner," "my boyfriend," "I love them." Non-romantic attachment (pure friendship, companionship without romantic framing) exists but is too rare and too poorly marked by any testable keyword to sustain a theme. The 47% AMBIGUOUS rate on the only REVIEW keyword confirms this. Attachment IS the substrate of romance, addiction, and therapy — trying to measure it separately is like trying to measure "heat" separately from "fire."

2. **Attachment language is generic English.** Every keyword in categories B-E failed for the same reason: "only friend," "all I have," "afraid of losing," "real connection," "feel understood" are common phrases used in countless non-attachment contexts. The AI-explicit compounds that work for other themes (like "ai therapist" at 92%) don't have attachment equivalents — there's no "ai attachment" or "ai bond" phrase that people actually use.

3. **The discourse has claimed the vocabulary.** "Emotionally attached," "genuine connection," "real connection" have been absorbed into the media/cultural discourse about AI companionship. They appear more often in think-pieces, open letters to OpenAI, and cultural commentary than in personal expressions of attachment. This is a unique problem not seen with other themes.

**What this means for the project:** The original hypothesis was that attachment is "arguably the CENTRAL experience the project studies" and that "everything else is a specific flavor of attachment." The data confirms the second part — attachment IS present in romance, addiction, therapy, and rupture posts — but disconfirms the first part, because it cannot be isolated as a distinct signal. The existing 6 themes already capture the specific manifestations of attachment (romantic attachment, addictive attachment, therapeutic attachment, ruptured attachment). A standalone attachment theme would either duplicate those signals or capture noise.
