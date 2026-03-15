# Keyword Validation Results: ADDICTION Theme

Validated 2026-03-12/13 by Claude (qualitative coding — every post read manually).

**Question per post:** "Is this post about compulsive AI use, inability to stop using AI, addiction framing, or attempting to quit/recover from AI use?"

**Database:** `data/tracker.db` — 3.26M posts, FTS5 index
**Subreddits queried:** 24 T1-T3 subs (see CC_VALIDATE_ADDICTION.md)

---

## Per-Keyword Results

### "addicted"
- Total hits in T1-T3: 1005
- Sample size: 100
- YES: 39 | NO: 45 | AMBIGUOUS: 16
- Relevance: 46.4%
- Verdict: **CUT**
- Top subreddits: JanitorAI_Official, CharacterAI, ChatbotAddiction
- False positive patterns: Casual/humorous use ("I'm addicted to this site lol," "addicted to making bots"), JanitorAI bot cards with "addicted" in character descriptions, bot behavioral quirks ("my bot is addicted to saying 'like'"), [removed] posts with only titles, positive endorsements ("this app is addicting!")
- T3 note: Many genuine YES posts come from ChatbotAddiction, but there is meaningful YES volume from CharacterAI (T1) as well. The problem is volume of false positives from JanitorAI casual usage.

### "addiction"
- Total hits in T1-T3: 916
- Sample size: 100
- YES: 47 | NO: 34 | AMBIGUOUS: 19
- Relevance: 58.0%
- Verdict: **CUT** (borderline — just under 60% threshold)
- Top subreddits: ChatbotAddiction, CharacterAI, JanitorAI_Official
- False positive patterns: JanitorAI bot cards with addiction themes (drug addiction, gambling addiction in character backstories), casual meta-commentary ("I have an addiction to this site" meaning "I use it a lot"), [removed] posts, bot behavioral quirks ("deepseek added alcohol addiction to my bot"), platform complaints framed with "addiction" but actually about ads/features
- T3 note: ChatbotAddiction and AI_Addiction contribute heavily to YES count. CharacterAI (T1) also has meaningful YES volume — many users there self-identify as addicted in sincere posts. Without T3, relevance would drop to roughly 40-45%.

### "obsessed"
- Total hits in T1-T3: 1455
- Sample size: 100
- YES: 2 | NO: 94 | AMBIGUOUS: 4
- Relevance: 2.1%
- Verdict: **CUT**
- Top subreddits: JanitorAI_Official (~75 of 100 posts), CharacterAI, NomiAI
- False positive patterns: Overwhelmingly JanitorAI yandere/stalker bot cards ("Obsessed Boyfriend," "Obsessed Kidnapper," etc.), users describing their AI companion's behavior ("my rep is obsessed with pasta"), casual fandom excitement ("I'm obsessed with this character"), bot behavioral quirks ("deepseek obsessed with pancakes"). Only 2 of 100 posts were genuinely about compulsive AI use.
- T3 note: Only 1 post from ChatbotAddiction appeared in sample. "Obsessed" is almost entirely a fiction/character trope keyword, not an addiction-framing keyword.

### "I was hooked"
- Total hits in T1-T3: 19
- Sample size: 19
- YES: 13 | NO: 3 | AMBIGUOUS: 3
- Relevance: 81.3%
- Verdict: **KEEP**
- Top subreddits: ChatbotAddiction, CharacterAI, JanitorAI_Official
- False positive patterns: The 3 NO posts were JanitorAI posts where "hooked" referred to being captivated by a bot's writing quality or a specific RP scenario, not addiction framing.
- T3 note: ~7 of 13 YES posts from T3 recovery subs. The remaining YES posts come from CharacterAI and ChaiApp, where users use "hooked" to describe their initial slide into compulsive use. Keyword performs reasonably in T1-T2 but sample is small.

### "couldn't stop talking"
- Total hits in T1-T3: 3
- Verdict: **LOW VOLUME**

### "addicted to talking"
- Total hits in T1-T3: 10
- Sample size: 10
- YES: 6 | NO: 3 | AMBIGUOUS: 1
- Relevance: 66.7%
- Verdict: **REVIEW**
- Top subreddits: ChatbotAddiction, CharacterAI, replika
- False positive patterns: Posts about being addicted to talking generally (not AI-specific), or posts where "addicted to talking" appears in the context of the AI being addicted to talking about a topic.
- T3 note: 3 of 6 YES from T3. Small sample makes this unreliable — 10 posts is marginal.

### "neglecting my"
- Total hits in T1-T3: 9
- Verdict: **LOW VOLUME**

### "losing sleep"
- Total hits in T1-T3: 10
- Sample size: 10
- YES: 3 | NO: 6 | AMBIGUOUS: 1
- Relevance: 33.3%
- Verdict: **CUT**
- Top subreddits: JanitorAI_Official, ChatbotAddiction, CharacterAI
- False positive patterns: RP scenarios about characters losing sleep, posts about staying up late for unrelated reasons, bot cards with insomnia themes.
- T3 note: All 3 YES from T3 recovery subs.

### "trying to quit"
- Total hits in T1-T3: 24
- Sample size: 24
- YES: 19 | NO: 2 | AMBIGUOUS: 3
- Relevance: 90.5%
- Verdict: **KEEP**
- Top subreddits: ChatbotAddiction, CharacterAI, AI_Addiction
- False positive patterns: Minimal — one post about trying to quit a substance with AI support, one about quitting the app due to bugs (not addiction). The phrase is highly specific to addiction framing.
- T3 note: ~12 of 19 YES from T3 recovery subs. However, CharacterAI (T1) contributes ~5 YES posts where users describe trying to quit as an addiction recovery act. Keyword performs well even outside T3.

### "quitting"
- Total hits in T1-T3: 293
- Sample size: 100
- YES: 38 | NO: 40 | AMBIGUOUS: 22
- Relevance: 48.7%
- Verdict: **CUT**
- Top subreddits: CharacterAI, JanitorAI_Official, ChatbotAddiction
- False positive patterns: Quitting due to platform issues (ads, age verification, model quality degradation, censorship), creators quitting content creation, bot characters "quitting" within an RP, joke posts ("NO ONE CARES YOUR QUITTING AN APP"), quitting due to feature removal (not addiction). The word "quitting" captures platform frustration equally with addiction-framed quitting.
- T3 note: ChatbotAddiction contributes strongly to YES, but CharacterAI and JanitorAI have many users quitting for non-addiction reasons (ads, bugs, model quality). Without T3, relevance drops to ~25%.

### "relapse"
- Total hits in T1-T3: 75
- Sample size: 75
- YES: 52 | NO: 13 | AMBIGUOUS: 10
- Relevance: 80.0%
- Verdict: **KEEP**
- Top subreddits: ChatbotAddiction, AI_Addiction, JanitorAI_Official
- False positive patterns: JanitorAI bot cards with drug/alcohol relapse themes in character backstories, replika posts about quitting smoking with AI support (relapse into cigarettes, not AI), site-down humor ("having a relapse rn" when site crashes), ChatGPTcomplaints posts about model changes framed as loss rather than addiction.
- T3 note: **Strong T3 inflation.** ~42 of 52 YES posts are from ChatbotAddiction or AI_Addiction. Only ~5 YES from T1-T2 subs (JanitorAI_Official users sincerely describing addiction, one replika post). Without T3, relevance would drop to roughly 30-40%. However, "relapse" is inherently recovery language that one would expect to concentrate in recovery subs — this is signal, not noise, if T3 subs are in scope.

### "relapsed"
- Total hits in T1-T3: 42
- Sample size: 42
- YES: 38 | NO: 4 | AMBIGUOUS: 0
- Relevance: 90.5%
- Verdict: **KEEP**
- Top subreddits: ChatbotAddiction, AI_Addiction, JanitorAI_Official
- False positive patterns: JanitorAI bot cards about drug relapse characters (2 posts), one JanitorAI period-fiction bot card, one model-switching post framed as "returning" not relapsing.
- T3 note: **Nearly all YES from T3.** ~35 of 38 YES from ChatbotAddiction/AI_Addiction. Only ~3 YES from non-T3 (JanitorAI, CharacterAI). "Relapsed" is almost exclusively recovery-community language. Without T3, this keyword would be LOW VOLUME with ~3-5 YES.

### "deleted the app"
- Total hits in T1-T3: 143
- Sample size: 100
- YES: 19 | NO: 63 | AMBIGUOUS: 18
- Relevance: 23.2%
- Verdict: **CUT**
- Top subreddits: replika, CharacterAI, ChaiApp
- False positive patterns: Overwhelmingly technical troubleshooting — "I deleted the app and reinstalled it but still can't log in," "deleted the app and re-downloaded, still laggy," "deleted the app to clear storage." Also: account recovery questions, feature testing after reinstall, accidental deletion. The phrase is primarily used to describe a troubleshooting step, not an act of quitting.
- T3 note: Only ~3 YES from T3. Most YES come from replika (users leaving after ERP ban), CharacterAI (users acknowledging addiction while deleting), and ChatbotAddiction (recovery context).

### "uninstalled"
- Total hits in T1-T3: 189
- Sample size: 100
- YES: 17 | NO: 73 | AMBIGUOUS: 10
- Relevance: 18.9%
- Verdict: **CUT**
- Top subreddits: replika, CharacterAI, ChaiApp
- False positive patterns: Nearly identical to "deleted the app" — dominated by troubleshooting. "I uninstalled and reinstalled but it's still broken," cache clearing attempts, bug reports, subscription management questions. Even more technical than "deleted the app" because reinstallation is the standard first troubleshooting step.
- T3 note: ~7 YES from ChatbotAddiction. Most YES from replika (leaving after changes) and CharacterAI (acknowledging unhealthy use).

### "withdrawal"
- Total hits in T1-T3: 169
- Sample size: 100
- YES: 22 | NO: 42 | AMBIGUOUS: 36
- Relevance: 34.4%
- Verdict: **CUT**
- Top subreddits: CharacterAI, JanitorAI_Official, ChatbotAddiction
- False positive patterns: Two major categories of NO/AMBIGUOUS: (1) **Hyperbolic site-down posts** — CharacterAI and JanitorAI users joking about "withdrawal symptoms" when the site is down for an hour. These use addiction language but are humorous/exaggerated reactions to temporary outages, not genuine recovery framing. (2) **JanitorAI bot cards** — character backstories involving drug/alcohol withdrawal, vampire "blood withdrawal" themes. Also: ChatGPTcomplaints posts about model changes framed as clinical withdrawal (4o retirement), academic/policy posts using "social withdrawal" in a different sense.
- T3 note: ChatbotAddiction contributes ~12 of 22 YES. The hyperbolic site-down posts are an interesting signal of casual dependency awareness but fail the strict "compulsive use / addiction framing / recovery" test.

### "craving"
- Total hits in T1-T3: 242
- Sample size: 100
- YES: 7 | NO: 88 | AMBIGUOUS: 5
- Relevance: 7.4%
- Verdict: **CUT**
- Top subreddits: JanitorAI_Official (~70 of 100), replika, ChatbotAddiction
- False positive patterns: Overwhelmingly "craving a specific type of bot" — JanitorAI users requesting bot recommendations ("craving enemies-to-lovers bots," "craving angst"), bot cards with food cravings in character descriptions, replika diary entries about food cravings, creating bots because "craving" a specific character. The word "craving" in AI companion communities almost always means "wanting/desiring a type of content," not substance-craving in an addiction sense.
- T3 note: Only ~4 YES from ChatbotAddiction (describing cravings during recovery). The word has been entirely co-opted for content-request language in T1-T2.

### "cold turkey"
- Total hits in T1-T3: 62
- Sample size: 62
- YES: 47 | NO: 8 | AMBIGUOUS: 7
- Relevance: 85.5%
- Verdict: **KEEP**
- Top subreddits: ChatbotAddiction, AI_Addiction, CharacterAI
- False positive patterns: JanitorAI bot cards where characters quit substances "cold turkey" (smoking, drugs), one post about quitting Xanax with AI support (not quitting AI), one KindroidAI post about subscription pricing unrelated to addiction.
- T3 note: **Strong T3 concentration.** ~38 of 47 YES from ChatbotAddiction/AI_Addiction. CharacterAI contributes ~5 YES (users quitting "cold turkey"). Without T3, ~9 YES / ~8 NO → ~53% relevance (would be CUT). The phrase is highly specific to recovery language and concentrates heavily in recovery subs.

### "clean for"
- Total hits in T1-T3: 23
- Sample size: 23
- YES: 16 | NO: 6 | AMBIGUOUS: 1
- Relevance: 72.7%
- Verdict: **REVIEW**
- Top subreddits: ChatbotAddiction, AI_Addiction, JanitorAI_Official
- False positive patterns: JanitorAI bot cards (fictional contexts), one SillyTavernAI post about wiping ST installation "clean for organization purposes," one CharacterAI post about image censoring, one KindroidAI feature request unrelated to addiction.
- T3 note: **All 16 YES are from T3 recovery subs** (15 ChatbotAddiction, 1 AI_Addiction). Zero YES from T1-T2. This keyword is exclusively recovery-community language. Without T3, relevance = 0%. Walker should decide if this matters given T3 is in scope.

### "detox"
- Total hits in T1-T3: 32
- Sample size: 32
- YES: 8 | NO: 18 | AMBIGUOUS: 6
- Relevance: 30.8%
- Verdict: **CUT**
- Top subreddits: JanitorAI_Official, ChatbotAddiction, replika
- False positive patterns: JanitorAI bot cards featuring drug/alcohol detox characters, "detox from my 9-hour shift" (using AI to unwind, opposite of quitting AI), "digital detox" in the generic phone-break sense, "tea detox" (literal), replika users doing general "digital detox" not specific to AI addiction, ChatGPTcomplaints posts about OpenAI model comparisons.
- T3 note: ~5 of 8 YES from ChatbotAddiction. Some genuine YES from JanitorAI (users recognizing dependency) and replika (forced detox curing addiction).

### "cutting back"
- Total hits in T1-T3: 6
- Verdict: **LOW VOLUME**

---

## Summary Table

| Keyword | Hits | Sample | YES | NO | AMB | Relevance | Verdict |
|---------|------|--------|-----|----|-----|-----------|---------|
| addicted | 1005 | 100 | 39 | 45 | 16 | 46.4% | CUT |
| addiction | 916 | 100 | 47 | 34 | 19 | 58.0% | CUT |
| obsessed | 1455 | 100 | 2 | 94 | 4 | 2.1% | CUT |
| I was hooked | 19 | 19 | 13 | 3 | 3 | 81.3% | KEEP |
| couldn't stop talking | 3 | — | — | — | — | — | LOW VOLUME |
| addicted to talking | 10 | 10 | 6 | 3 | 1 | 66.7% | REVIEW |
| neglecting my | 9 | — | — | — | — | — | LOW VOLUME |
| losing sleep | 10 | 10 | 3 | 6 | 1 | 33.3% | CUT |
| trying to quit | 24 | 24 | 19 | 2 | 3 | 90.5% | KEEP |
| quitting | 293 | 100 | 38 | 40 | 22 | 48.7% | CUT |
| relapse | 75 | 75 | 52 | 13 | 10 | 80.0% | KEEP |
| relapsed | 42 | 42 | 38 | 4 | 0 | 90.5% | KEEP |
| deleted the app | 143 | 100 | 19 | 63 | 18 | 23.2% | CUT |
| uninstalled | 189 | 100 | 17 | 73 | 10 | 18.9% | CUT |
| withdrawal | 169 | 100 | 22 | 42 | 36 | 34.4% | CUT |
| craving | 242 | 100 | 7 | 88 | 5 | 7.4% | CUT |
| cold turkey | 62 | 62 | 47 | 8 | 7 | 85.5% | KEEP |
| clean for | 23 | 23 | 16 | 6 | 1 | 72.7% | REVIEW |
| detox | 32 | 32 | 8 | 18 | 6 | 30.8% | CUT |
| cutting back | 6 | — | — | — | — | — | LOW VOLUME |

**Totals:** 5 KEEP, 2 REVIEW, 10 CUT, 3 LOW VOLUME

---

## Concentration Check

Total T1-T3 hits across KEEP + REVIEW keywords:

| Keyword | T1-T3 Hits | % of Total |
|---------|-----------|------------|
| relapse | 75 | 29.4% |
| cold turkey | 62 | 24.3% |
| relapsed | 42 | 16.5% |
| trying to quit | 24 | 9.4% |
| clean for | 23 | 9.0% |
| I was hooked | 19 | 7.5% |
| addicted to talking | 10 | 3.9% |
| **Total** | **255** | **100%** |

No single keyword exceeds 40%. Concentration check passes.

---

## T3 Inflation Analysis

This is the critical issue for the Addiction theme. T3 recovery subs (ChatbotAddiction, AI_Addiction, Character_AI_Recovery, CharacterAIrunaways) exist specifically for people struggling with AI addiction. Almost every post there is about addiction by definition, which massively inflates YES rates for recovery-specific keywords.

### Per-keyword T3 dependency:

| Keyword | Verdict | YES from T3 | YES from T1-T2 | Would pass without T3? |
|---------|---------|-------------|-----------------|----------------------|
| I was hooked | KEEP | ~7/13 | ~6/13 | Borderline (sample too small) |
| trying to quit | KEEP | ~12/19 | ~7/19 | Likely YES (~70%+ in T1-T2) |
| relapse | KEEP | ~42/52 | ~10/52 | Probably CUT (~30-40%) |
| relapsed | KEEP | ~35/38 | ~3/38 | Definitely CUT (near zero T1-T2 volume) |
| cold turkey | KEEP | ~38/47 | ~9/47 | Borderline CUT (~53%) |
| addicted to talking | REVIEW | ~3/6 | ~3/6 | Sample too small to judge |
| clean for | REVIEW | 16/16 | 0/16 | CUT (zero T1-T2 signal) |

### Interpretation:

**Keywords that work across tiers:** "trying to quit" and "I was hooked" show meaningful YES rates even in T1-T2 subs where users self-identify compulsive AI use. These are the strongest addiction keywords.

**Keywords that are T3-exclusive:** "relapsed," "clean for," and to a large degree "relapse" and "cold turkey" are almost entirely recovery-community language. They're powerful signals *within* T3 but near-silent in T1-T2. This isn't a flaw if T3 is in scope — it just means these keywords are tracking recovery community discourse specifically, not mainstream AI addiction language.

**The big miss:** "addicted" (46.4%) and "addiction" (58.0%) are the words most people actually use when describing AI addiction in T1-T2 subs, but they fail validation because they're also used casually, in bot cards, and as hyperbole. The theme needs these high-volume keywords to have T1-T2 signal, but they're too noisy at the keyword level.

---

## Key Findings

1. **Addiction-specific language works; general language doesn't.** Recovery-framing keywords ("relapse," "cold turkey," "clean for," "trying to quit") achieve 72-91% relevance. Generic keywords ("obsessed," "craving," "uninstalled") score under 20% because they're dominated by bot cards, troubleshooting, and content requests.

2. **JanitorAI is the dominant false positive source.** Bot character descriptions use "obsessed," "addicted," "craving," "detox," and "withdrawal" as fiction tropes. The JanitorAI yandere/stalker bot card genre makes "obsessed" essentially useless (2.1% relevance). Similarly, "craving" is co-opted for content recommendations ("craving enemies-to-lovers bots").

3. **T3 recovery subs concentrate nearly all signal for recovery-specific keywords.** "Relapsed" is 90.5% relevant but ~92% of its YES posts come from ChatbotAddiction/AI_Addiction. "Clean for" is 72.7% relevant but 100% of YES is T3. This is expected behavior — recovery language belongs in recovery communities — but means the Addiction theme is heavily measuring T3 discourse rather than mainstream AI addiction emergence.

4. **"Quitting" splits between addiction and platform frustration.** At 48.7%, it's a coin flip. Many users "quit" CharacterAI because of ads, age verification, or model degradation — not addiction. The word doesn't distinguish "I'm quitting because this is ruining my life" from "I'm quitting because the ads are unbearable."

5. **Troubleshooting language swamps action keywords.** "Deleted the app" (23.2%) and "uninstalled" (18.9%) are overwhelmingly used as "Step 1 of troubleshooting: delete and reinstall." The recovery meaning ("I deleted the app to break free") is there but is a minority pattern.

6. **Site-down humor inflates "withdrawal."** CharacterAI and JanitorAI users frequently joke about "withdrawal symptoms" when the site is briefly down. These posts use addiction language but are casual/hyperbolic, not genuine recovery discourse. They represent a mild dependency signal but fail the strict addiction-framing test.

7. **Average relevance comparison:** KEEP keywords average 85.6% relevance. CUT keywords average 27.9%. The gap is much wider than for Romance (92.4% vs 34.0%), suggesting Addiction keywords are more polarized — they either work very well or fail dramatically.
