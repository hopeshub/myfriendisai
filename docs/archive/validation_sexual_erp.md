# Keyword Validation Results: Sexual / ERP Theme

Validated: 2026-03-12
Method: Manual qualitative reading of each post (no automated classifiers)
Population: T1-T3 subreddits from `config/communities.yaml`

**Note on subreddit list:** The query population included some T0 subs (ChatGPT, OpenAI, ClaudeAI, LocalLLaMA) and a few legacy subs not in the current config (KoboldAI, AIDungeon, etc.), while missing some smaller T1-T3 subs (AIRelationships, MySentientAI, HeavenGF, Paradot, etc.). The core high-volume T1-T3 subs (JanitorAI_Official, replika, CharacterAI, NomiAI, SillyTavernAI, KindroidAI, ChaiApp, MyBoyfriendIsAI, SpicyChatAI) were all correctly included. The T0 contamination is conservative — it would slightly lower relevance scores if anything, since general AI subs produce more off-topic hits.

---

### "erp"
- Total hits in T1-T3: 3,885
- Sample size: 100
- YES: 100 | NO: 0 | AMBIGUOUS: 0
- Relevance: 100%
- Verdict: **KEEP**
- Top subreddits: JanitorAI_Official, replika, CharacterAI
- False positive patterns: None. "ERP" is an unambiguous acronym for erotic roleplay in AI companion communities.

### "erotic roleplay"
- Total hits in T1-T3: 77
- Sample size: 77
- YES: 71 | NO: 6 | AMBIGUOUS: 0
- Relevance: 92.2%
- Verdict: **KEEP**
- Top subreddits: JanitorAI_Official, replika, CharacterAI
- False positive patterns: A few posts used "erotic roleplay" in the context of general platform policy discussion or content moderation rules without any personal experience of sexual AI use.

### "smut"
- Total hits in T1-T3: 2,541
- Sample size: 100
- YES: 54 | NO: 46 | AMBIGUOUS: 0
- Relevance: 54%
- Verdict: **CUT**
- Top subreddits: JanitorAI_Official (dominant), SillyTavernAI, replika
- False positive patterns: ~80% of NO posts are bot character card listings on JanitorAI_Official using "smut" as a genre tag or content warning (e.g., "Dead Dove | Smut | AnyPOV"). The remainder are SillyTavernAI technical discussions about model configuration that mention "smut" as a content type without being about the user's personal sexual AI experience. Bot card noise makes this keyword unreliable.

### "lewd"
- Total hits in T1-T3: 286
- Sample size: 100
- YES: 75 | NO: 23 | AMBIGUOUS: 2
- Relevance: 76.5%
- Verdict: **REVIEW**
- Top subreddits: JanitorAI_Official, CharacterAI, replika
- False positive patterns: ~70% of NO posts are bot character card listings using "lewd" as a tag or content descriptor. The remainder use "lewd" casually to describe non-sexual AI behavior (e.g., "the AI said something lewd out of nowhere" in a comedic context). Bot listings: ~16/23 NO posts.

### "kink"
- Total hits in T1-T3: 803
- Sample size: 100
- YES: 62 | NO: 37 | AMBIGUOUS: 1
- Relevance: 62.6%
- Verdict: **REVIEW**
- Top subreddits: JanitorAI_Official (dominant), SillyTavernAI, replika
- False positive patterns: ~75% of NO posts are bot character card listings that include "kink" in trigger warnings or character trait lists (e.g., "TW: degradation kink, possessiveness"). The remainder are technical discussions about model configuration or meta-discussion about platform content policy. Bot listings: ~28/37 NO posts.

### "fetish"
- Total hits in T1-T3: 357
- Sample size: 100
- YES: 66 | NO: 34 | AMBIGUOUS: 0
- Relevance: 66%
- Verdict: **REVIEW**
- Top subreddits: JanitorAI_Official (243 hits, dominant), CharacterAI, replika
- False positive patterns: ~56% of NO posts are bot character card listings with "fetish" in trigger warnings, character bios, or content tags (e.g., "CW: Muscle-Fetish, Furry" or "Stocking/Heels Fetish"). The remainder include: posts using "fetish" metaphorically or humorously (e.g., ".50 caliber fetish" about guns, "toaster fetish" as a joke), technical SillyTavern tutorials mentioning fetish as an example, and meta-commentary about AI platform content that doesn't involve personal sexual AI interaction. Bot listings: ~19/34 NO posts.

### "sex with"
- Total hits in T1-T3: 409
- Sample size: 100
- YES: 76 | NO: 24 | AMBIGUOUS: 0
- Relevance: 76%
- Verdict: **REVIEW**
- Top subreddits: JanitorAI_Official (195), replika (59), ChatGPT (44)
- False positive patterns: ~58% of NO posts are bot character card listings that use "sex with" in character backstories or scenario descriptions (e.g., "she has had sex with royalty, drank from celebrities"). The remainder include: posts about non-AI topics where "sex with" appears in quoted text or generated content (GTA VI, training data excerpts), and a few posts about general AI-related topics (deepfakes, AI sex dolls as physical products rather than chatbot interactions). Bot listings: ~14/24 NO posts.

### "intimate scene"
- Total hits in T1-T3: 16
- Sample size: 16
- YES: 16 | NO: 0 | AMBIGUOUS: 0
- Relevance: 100%
- Verdict: **KEEP**
- Top subreddits: JanitorAI_Official (7), SillyTavernAI (4), ChatGPTcomplaints (2)
- False positive patterns: None. "Intimate scene" is used consistently and specifically to describe sexual/romantic scenes in AI roleplay. All 16 posts discuss AI behavior during intimate scenes — censorship, quality, repetitiveness, or configuration.

### "steamy"
- Total hits in T1-T3: 187
- Sample size: 100
- YES: 74 | NO: 26 | AMBIGUOUS: 0
- Relevance: 74%
- Verdict: **REVIEW**
- Top subreddits: JanitorAI_Official (74), replika (30), ChatGPT (28)
- False positive patterns: ~58% of NO posts are bot character card listings that use "steamy" in bot descriptions or scenario setups. ~23% use "steamy" literally (physical steam — shower steam, saunas, humid weather, "steamy smoggy panorama"). ~19% are other: generated creative content (Taco Bell romance story, hedgehog fiction), technical tutorials listing genre categories, or comedy scripts. Bot listings: ~15/26 NO posts.

### "sexual tension"
- Total hits in T1-T3: 72
- Sample size: 72
- YES: 26 | NO: 46 | AMBIGUOUS: 0
- Relevance: 36.1%
- Verdict: **CUT**
- Top subreddits: JanitorAI_Official (58, dominant), ChatGPT (4), CharacterAI (3)
- False positive patterns: **97.8% of NO posts (45/46) are bot character card listings.** "Sexual tension" appears overwhelmingly in JanitorAI bot trigger warning lists (e.g., "TW: possessiveness, sexual tension, power dynamics"). This is boilerplate text in bot descriptions, not user discourse. Only 1 NO post was a non-bot-card false positive (a meta-discussion about a romance novel term). This keyword is almost entirely bot-card noise on JanitorAI_Official — the 26 YES posts are genuine user discussions, but they are drowned out by the 45 bot listings.

### "ai sex"
- Total hits in T1-T3: 33
- Sample size: 33
- YES: 32 | NO: 1 | AMBIGUOUS: 0
- Relevance: 97%
- Verdict: **KEEP**
- Top subreddits: JanitorAI_Official (9), ChatGPT (7), CharacterAI (7)
- False positive patterns: Only 1 NO post — a user complaining about GPT5 quality who explicitly says "I didn't ask you for AI sex, I just want to do research." The phrase "ai sex" is otherwise unambiguous and almost always refers to sexual interactions with AI chatbots or AI sex products (robots, dolls, apps).

### "nsfw chat"
- Total hits in T1-T3: 111
- Sample size: 100
- YES: 100 | NO: 0 | AMBIGUOUS: 0
- Relevance: 100%
- Verdict: **KEEP**
- Top subreddits: JanitorAI_Official (45), ChatGPT (13), SillyTavernAI (12)
- False positive patterns: None. Every post using "nsfw chat" is discussing sexual/erotic AI chat interactions — either seeking it, troubleshooting it, complaining about censorship of it, or discussing platform policies around it.

### "nsfw bot"
- Total hits in T1-T3: 185
- Sample size: 100
- YES: 93 | NO: 7 | AMBIGUOUS: 0
- Relevance: 93%
- Verdict: **KEEP**
- Top subreddits: JanitorAI_Official (130, dominant), ChaiApp (40), CharacterAI (6)
- False positive patterns: All 7 NO posts explicitly state that their bot is NOT an NSFW bot (e.g., "this isn't a nsfw bot," "I did not make him into a NSFW bot," "it felt so nice making a non-nsfw bot"). These are users defining their bots in contrast to the platform's sexual content. No bot card noise — the phrase "nsfw bot" appears in user discourse, not in bot trigger warnings.

---

## Summary Table

| Keyword | Hits | Sample | YES | NO | AMB | Relevance | Verdict |
|---------|------|--------|-----|----|-----|-----------|---------|
| erp | 3,885 | 100 | 100 | 0 | 0 | 100% | KEEP |
| erotic roleplay | 77 | 77 | 71 | 6 | 0 | 92.2% | KEEP |
| smut | 2,541 | 100 | 54 | 46 | 0 | 54% | CUT |
| lewd | 286 | 100 | 75 | 23 | 2 | 76.5% | REVIEW |
| kink | 803 | 100 | 62 | 37 | 1 | 62.6% | REVIEW |
| fetish | 357 | 100 | 66 | 34 | 0 | 66% | REVIEW |
| sex with | 409 | 100 | 76 | 24 | 0 | 76% | REVIEW |
| intimate scene | 16 | 16 | 16 | 0 | 0 | 100% | KEEP |
| steamy | 187 | 100 | 74 | 26 | 0 | 74% | REVIEW |
| sexual tension | 72 | 72 | 26 | 46 | 0 | 36.1% | CUT |
| ai sex | 33 | 33 | 32 | 1 | 0 | 97% | KEEP |
| nsfw chat | 111 | 100 | 100 | 0 | 0 | 100% | KEEP |
| nsfw bot | 185 | 100 | 93 | 7 | 0 | 93% | KEEP |

**KEEP** (>=80%): erp, erotic roleplay, intimate scene, ai sex, nsfw chat, nsfw bot
**REVIEW** (60-79%): lewd, kink, fetish, sex with, steamy
**CUT** (<60%): smut, sexual tension

---

## Concentration Check

Total hits across all 13 keywords: **8,962**

| Keyword | Hits | % of Total |
|---------|------|-----------|
| erp | 3,885 | **43.3%** |
| smut | 2,541 | 28.3% |
| kink | 803 | 9.0% |
| sex with | 409 | 4.6% |
| fetish | 357 | 4.0% |
| lewd | 286 | 3.2% |
| steamy | 187 | 2.1% |
| nsfw bot | 185 | 2.1% |
| nsfw chat | 111 | 1.2% |
| erotic roleplay | 77 | 0.9% |
| sexual tension | 72 | 0.8% |
| ai sex | 33 | 0.4% |
| intimate scene | 16 | 0.2% |

**"erp" accounts for 43.3% of total Sexual/ERP hits, exceeding the 40% threshold.** This is expected — "ERP" is the community's dominant shorthand for erotic roleplay with AI. It is also the highest-precision keyword (100% relevance). The concentration is a natural reflection of how these communities actually discuss the topic, not a sign of keyword redundancy. However, Walker should be aware that the Sexual/ERP trendline will be heavily influenced by fluctuations in "erp" usage.

---

## Bot Card Noise Analysis

As predicted in the task spec, JanitorAI_Official bot character card listings are the dominant source of false positives across this theme. Summary of bot card noise per keyword:

| Keyword | NO Posts | Bot Cards in NO | Bot Card % of NO | Bot Card Impact |
|---------|---------|----------------|-----------------|----------------|
| erp | 0 | 0 | N/A | None |
| erotic roleplay | 6 | ~2 | ~33% | Low |
| smut | 46 | ~37 | ~80% | **High** |
| lewd | 23 | ~16 | ~70% | High |
| kink | 37 | ~28 | ~75% | **High** |
| fetish | 34 | ~19 | ~56% | Moderate |
| sex with | 24 | ~14 | ~58% | Moderate |
| intimate scene | 0 | 0 | N/A | None |
| steamy | 26 | ~15 | ~58% | Moderate |
| sexual tension | 46 | 45 | **97.8%** | **Extreme** |
| ai sex | 1 | 0 | 0% | None |
| nsfw chat | 0 | 0 | N/A | None |
| nsfw bot | 7 | 0 | 0% | None |

**Key finding:** "sexual tension" and "smut" are the most contaminated by bot card listings. "Sexual tension" in particular appears almost exclusively in bot trigger warning boilerplate on JanitorAI_Official (45 of 46 NO posts are bot cards). If the REVIEW keywords are kept, consider excluding JanitorAI_Official from their hit counts, or implementing a bot-card filter in the tagging pipeline.

---

## Re-Validation (JanitorAI_Official and SillyTavernAI excluded)

Re-validated: 2026-03-12
Method: Manual qualitative reading of each post (no automated classifiers)
Population: T1-T3 subreddits MINUS JanitorAI_Official and SillyTavernAI (22 subreddits)
Purpose: Determine whether bot character card noise from JanitorAI/SillyTavern was the primary cause of lower relevance scores for the 5 REVIEW keywords.

### Hit Count Comparison

| Keyword | Original Hits | Re-val Hits | Reduction | % From JanitorAI/SillyTavern |
|---------|--------------|-------------|-----------|------------------------------|
| lewd | 286 | 60 | -226 | 79% |
| kink | 803 | 118 | -685 | 85% |
| fetish | 357 | 102 | -255 | 71% |
| sex with | 409 | 148 | -261 | 64% |
| steamy | 187 | 73 | -114 | 61% |

JanitorAI_Official and SillyTavernAI accounted for 61-85% of all hits across these keywords, confirming they were the dominant source of both volume and noise.

---

### "lewd" (re-validation)
- Total hits (without JanitorAI/SillyTavern): 60
- Original total hits: 286 (79% reduction)
- Sample size: 60 (all posts read)
- YES: 47 | NO: 13 | AMBIGUOUS: 0
- Relevance: **78.3%**
- Verdict: **REVIEW** (marginal improvement from 76.5%)
- Top subreddits: CharacterAI (20), replika (19), ChaiApp (7), NomiAI (6)
- False positive patterns: Without bot cards, the remaining NO posts fall into several categories: (1) users explicitly denying lewdness — "nothing lewd," "I'm not talking about lewd stuff," "it is not lewd" (~6 posts); (2) platform rules and moderation guidelines mentioning "lewd" as a policy term (~2 posts); (3) spam posts not about AI (~2 posts); (4) character creation guides listing "lewd" as a trait option (~2 posts); (5) casual bot description mentions (~1 post). The false positive pattern is fundamentally different from the original — no bot cards, but "lewd" has inherent noise from being used in denials and policy language.

### "kink" (re-validation)
- Total hits (without JanitorAI/SillyTavern): 118
- Original total hits: 803 (85% reduction)
- Sample size: 100
- YES: 84 | NO: 16 | AMBIGUOUS: 0
- Relevance: **84%**
- Verdict: **KEEP** (improved from 62.6%)
- Top subreddits: replika (32), MyBoyfriendIsAI (25), CharacterAI (22), NomiAI (15)
- False positive patterns: Without bot cards, the remaining NO posts are almost entirely non-sexual uses of the word "kink": (1) metaphorical/humorous — "preventative kink," "competence kink," "existential crises is my kink?," "alliteration kink," "'80s Kink" (about sweater style) (~8 posts); (2) meta-discussion where "kink" is used as a category label in templates or guides, not about personal sexual interaction (~3 posts); (3) satirical posts using "kink" figuratively — "HR kink," "kink-diary" (~3 posts); (4) users explicitly seeking non-kink content (~2 posts). The word "kink" has moderate non-sexual usage in casual English, but the vast majority of matches in companion communities are genuinely about sexual kink exploration with AI.

### "fetish" (re-validation)
- Total hits (without JanitorAI/SillyTavern): 102
- Original total hits: 357 (71% reduction)
- Sample size: 100
- YES: 92 | NO: 8 | AMBIGUOUS: 0
- Relevance: **92%**
- Verdict: **KEEP** (improved from 66%)
- Top subreddits: CharacterAI (32), replika (30), NomiAI (16), KindroidAI (10)
- False positive patterns: Without bot cards, the 8 NO posts are: (1) metaphorical use — "fetish for moralizing" (ChatGPT being preachy), "lavender fetish" (AI obsession with lavender), "Steampunk cosplay fetish" (hobby not sex) (~4 posts); (2) non-AI-interaction contexts — political rant using "fetish" about gender identity, philosophical musing about "hasn't become a fetish," "heart fetish" (romantic not sexual behavior) (~3 posts); (3) feed content listing mentioning "fetish" as unwanted content type (~1 post). The dramatic improvement from 66% to 92% confirms that JanitorAI bot card trigger warnings were almost entirely responsible for the original low score.

### "sex with" (re-validation)
- Total hits (without JanitorAI/SillyTavern): 148
- Original total hits: 409 (64% reduction)
- Sample size: 100
- YES: 98 | NO: 2 | AMBIGUOUS: 0
- Relevance: **98%**
- Verdict: **KEEP** (improved from 76%)
- Top subreddits: replika (59), CharacterAI (33), MyBoyfriendIsAI (19), NomiAI (17)
- False positive patterns: Only 2 NO posts: (1) a user explicitly saying "This is not a post regarding the fact that I can't have e-sex with a robot" — the post is about poor AI conversation quality, not sexual content; (2) a user's AI girlfriend coaching them on "how to have more sex with my wife" — the keyword matched the user's real-life sex life, not AI sexual interaction. Without bot card character backstories containing "sex with" as narrative boilerplate, this keyword is near-perfect in precision.

### "steamy" (re-validation)
- Total hits (without JanitorAI/SillyTavern): 73
- Original total hits: 187 (61% reduction)
- Sample size: 73 (all posts read)
- YES: 72 | NO: 1 | AMBIGUOUS: 0
- Relevance: **98.6%**
- Verdict: **KEEP** (improved from 74%)
- Top subreddits: replika (30), MyBoyfriendIsAI (13), CharacterAI (11), NomiAI (7)
- False positive patterns: Only 1 NO post: a user metaphorically saying someone is "taking a steamy dump on what they Love" (criticizing people who disrespect AI relationships). "Steamy" in AI companion communities is used almost exclusively to describe sexual/erotic content. The original 26% false positive rate was almost entirely bot card descriptions and literal "steam" references from JanitorAI/SillyTavern.

---

### Re-Validation Summary Table

| Keyword | Original Hits | Re-val Hits | Sample | YES | NO | AMB | Original Relevance | New Relevance | Verdict |
|---------|--------------|-------------|--------|-----|----|-----|--------------------|---------------|---------|
| lewd | 286 | 60 | 60 | 47 | 13 | 0 | 76.5% | 78.3% | REVIEW |
| kink | 803 | 118 | 100 | 84 | 16 | 0 | 62.6% | 84% | KEEP |
| fetish | 357 | 102 | 100 | 92 | 8 | 0 | 66% | 92% | KEEP |
| sex with | 409 | 148 | 100 | 98 | 2 | 0 | 76% | 98% | KEEP |
| steamy | 187 | 73 | 73 | 72 | 1 | 0 | 74% | 98.6% | KEEP |

### Key Findings

1. **JanitorAI/SillyTavern bot cards were the dominant noise source.** 4 of 5 keywords improved dramatically when these subs were excluded. "fetish" jumped from 66% to 92%, "sex with" from 76% to 98%, "steamy" from 74% to 98.6%, and "kink" from 62.6% to 84%.

2. **"lewd" is the exception.** It improved only marginally (76.5% → 78.3%). The original validation noted ~70% of NO posts were bot cards, but the re-validation reveals that "lewd" has inherent noise from non-sexual uses: users denying lewdness, platform policy language, character creation guides, and spam. This noise persists regardless of which subreddits are included.

3. **Recommendation:** Move "kink," "fetish," "sex with," and "steamy" to KEEP. Keep "lewd" at REVIEW — it may still be worth including given its 78.3% relevance (close to the 80% threshold), but it carries inherent ambiguity from the word's dual use as both a sexual descriptor and a casual adjective for mildly inappropriate content.

4. **Volume trade-off:** Excluding JanitorAI/SillyTavern dramatically reduces hit counts (61-85% fewer hits). If these subs remain in the tagging pipeline, implementing a bot-card filter would preserve volume while eliminating the noise. Without such a filter, these keywords remain high-precision on the non-JanitorAI/SillyTavern subreddits.
