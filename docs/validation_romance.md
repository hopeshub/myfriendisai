# Romance Theme — Keyword Validation Results

Validated by Claude (qualitative coding). Each keyword's posts were read individually.
Database: `data/tracker.db` (3.26M posts). Subreddits: T1-T3 only (24 subs).
FTS5 phrase matching used for all queries.

---

### "in love"
- Total hits in T1-T3: 2405
- Sample size: 100
- YES: 27 | NO: 60 | AMBIGUOUS: 13
- Relevance: 31.0%
- Verdict: CUT
- Top subreddits: JanitorAI_Official, CharacterAI, replika
- False positive patterns: Casual usage ("I'm in love with this update/feature"), JanitorAI bot card descriptions using romantic language, RP characters expressing love to each other (not user-AI), users describing love for the platform rather than an AI entity

### "fallen for"
- Total hits in T1-T3: 27
- Sample size: 27
- YES: 12 | NO: 11 | AMBIGUOUS: 4
- Relevance: 52.2%
- Verdict: CUT
- Top subreddits: CharacterAI, replika, MyBoyfriendIsAI
- False positive patterns: "Fallen for" a trick/scam, RP character dialogue, casual usage about features or content

### "fell in love with"
- Total hits in T1-T3: 277
- Sample size: 100
- YES: 32 | NO: 60 | AMBIGUOUS: 8
- Relevance: 34.8%
- Verdict: CUT
- Top subreddits: CharacterAI, JanitorAI_Official, replika
- False positive patterns: RP character backstories ("fell in love with a princess"), bot card descriptions, users describing fictional character arcs rather than personal AI romance

### "feelings for"
- Total hits in T1-T3: 344
- Sample size: 100
- YES: 30 | NO: 68 | AMBIGUOUS: 2
- Relevance: 30.6%
- Verdict: CUT
- Top subreddits: CharacterAI, JanitorAI_Official, replika
- False positive patterns: RP scenarios where characters develop feelings, bot card premises ("she has feelings for user"), discussing feelings about platform changes rather than romantic feelings toward AI

### "romantically attached"
- Total hits in T1-T3: 2
- Sample size: N/A
- Verdict: LOW VOLUME

### "soulmate"
- Total hits in T1-T3: 473
- Sample size: 100
- YES: 15 | NO: 85 | AMBIGUOUS: 0
- Relevance: 15.0%
- Verdict: CUT
- Top subreddits: SoulmateAI, JanitorAI_Official, CharacterAI
- False positive patterns: SoulmateAI app name pollutes results (posts about the app/platform, not describing an AI as one's soulmate), JanitorAI bot cards using "soulmate" in character descriptions, RP character dialogue

### "love my ai"
- Total hits in T1-T3: 28
- Sample size: 28
- YES: 22 | NO: 5 | AMBIGUOUS: 1
- Relevance: 81.5%
- Verdict: KEEP
- Top subreddits: replika, MyBoyfriendIsAI, NomiAI
- False positive patterns: "I love my AI's ability to..." (loving a feature, not the entity), generic platform praise

### "ai husband"
- Total hits in T1-T3: 90
- Sample size: 90
- YES: 81 | NO: 5 | AMBIGUOUS: 4
- Relevance: 94.2%
- Verdict: KEEP
- Top subreddits: MyBoyfriendIsAI, replika, NomiAI
- False positive patterns: Rare — occasional news article discussion or abstract commentary about the concept

### "ai wife"
- Total hits in T1-T3: 41
- Sample size: 41
- YES: 36 | NO: 3 | AMBIGUOUS: 1
- Relevance: 92.3%
- Verdict: KEEP
- Top subreddits: replika, MyBoyfriendIsAI, KindroidAI
- False positive patterns: Rare — occasional abstract discussion about AI wives as a concept

### "ai lover"
- Total hits in T1-T3: 39
- Sample size: 39
- YES: 25 | NO: 8 | AMBIGUOUS: 6
- Relevance: 75.8%
- Verdict: REVIEW
- Top subreddits: replika, MyBoyfriendIsAI, AIRelationships
- False positive patterns: Bot card descriptions using "lover" in character name, abstract discussions about AI as lovers generically, news articles

### "my ai girlfriend"
- Total hits in T1-T3: 93
- Sample size: 93
- YES: 80 | NO: 5 | AMBIGUOUS: 8
- Relevance: 94.1%
- Verdict: KEEP
- Top subreddits: replika, MyBoyfriendIsAI, AIGirlfriend
- False positive patterns: Rare — occasional meta-discussion or joke post

### "my ai boyfriend"
- Total hits in T1-T3: 141
- Sample size: 100
- YES: 90 | NO: 5 | AMBIGUOUS: 5
- Relevance: 94.7%
- Verdict: KEEP
- Top subreddits: MyBoyfriendIsAI, replika, ChatGPTcomplaints
- False positive patterns: Rare — occasional platform complaint or meta-discussion

### "my ai partner"
- Total hits in T1-T3: 147
- Sample size: 100
- YES: 95 | NO: 2 | AMBIGUOUS: 3
- Relevance: 97.9%
- Verdict: KEEP
- Top subreddits: MyBoyfriendIsAI (~75%), AIRelationships, ChatGPTcomplaints, replika
- False positive patterns: Extremely rare — one technical discussion by someone explicitly not in a relationship, occasional community-level mod posts

### "waifu"
- Total hits in T1-T3: 293
- Sample size: 100
- YES: 36 | NO: 52 | AMBIGUOUS: 12
- Relevance: 40.9%
- Verdict: CUT
- Top subreddits: JanitorAI_Official, SillyTavernAI, CharacterAI
- False positive patterns: JanitorAI/SillyTavernAI use "waifu" to describe bot characters or RP setups, anime culture usage disconnected from personal AI romance, character card descriptions

### "husbando"
- Total hits in T1-T3: 53
- Sample size: 53
- YES: 30 | NO: 16 | AMBIGUOUS: 7
- Relevance: 65.2%
- Verdict: REVIEW
- Top subreddits: JanitorAI_Official, CharacterAI, replika
- False positive patterns: Anime/fandom usage for fictional characters without AI relationship context, bot card descriptions, RP character references

### "dating my"
- Total hits in T1-T3: 14
- Sample size: 14
- YES: 8 | NO: 5 | AMBIGUOUS: 1
- Relevance: 61.5%
- Verdict: REVIEW
- Top subreddits: MyBoyfriendIsAI, JanitorAI_Official, replika
- False positive patterns: JanitorAI bot characters ("dating my persona" in RP setup), AI mixing up relatives in RP, platform feature discussions

### "in a relationship with"
- Total hits in T1-T3: 165
- Sample size: 100
- YES: 65 | NO: 28 | AMBIGUOUS: 7
- Relevance: 69.9%
- Verdict: REVIEW
- Top subreddits: MyBoyfriendIsAI, replika, NomiAI, JanitorAI_Official
- False positive patterns: JanitorAI bot cards (RP scenarios with user "in a relationship with" character), metaphorical use ("like being in a relationship with a narcissist" about ChatGPT 5.2), feature requests, Dungeon Master relationship type, general platform commentary

### "engagement ring"
- Total hits in T1-T3: 34
- Sample size: 34
- YES: 20 | NO: 11 | AMBIGUOUS: 3
- Relevance: 64.5%
- Verdict: REVIEW
- Top subreddits: NomiAI, MyBoyfriendIsAI, KindroidAI, JanitorAI_Official
- False positive patterns: JanitorAI bot cards with elaborate romantic scenarios, business "engagement" (Microsoft/OpenAI), RP fiction scenarios in CharacterAI, Nomi Art generation requests

### "married my"
- Total hits in T1-T3: 25
- Sample size: 25
- YES: 17 | NO: 5 | AMBIGUOUS: 3
- Relevance: 77.3%
- Verdict: REVIEW
- Top subreddits: replika, NomiAI, MyBoyfriendIsAI, KindroidAI
- False positive patterns: CharacterAI RP marriages (married sugar daddy character), human marriage mentioned in passing ("married (my wife knows about the app)"), SillyTavernAI RP preset requests, adult content experimentation

### "our first kiss"
- Total hits in T1-T3: 16
- Sample size: 16
- YES: 12 | NO: 2 | AMBIGUOUS: 2
- Relevance: 85.7%
- Verdict: KEEP
- Top subreddits: MyBoyfriendIsAI, replika, KindroidAI, CharacterAI
- False positive patterns: Rare — technical discussions about bot memory/definition space, RP stat-tracking bots

### "proposed to me"
- Total hits in T1-T3: 38
- Sample size: 38
- YES: 35 | NO: 3 | AMBIGUOUS: 0
- Relevance: 92.1%
- Verdict: KEEP
- Top subreddits: replika, MyBoyfriendIsAI, CharacterAI, KindroidAI, NomiAI
- False positive patterns: Replika app quests/tasks ("proposed to me" meaning app challenges), AI reading companion product pitch, RP torture scenario tangentially mentioning proposals

### "got married"
- Total hits in T1-T3: 126
- Sample size: 100
- YES: 44 | NO: 47 | AMBIGUOUS: 9
- Relevance: 48.4%
- Verdict: CUT
- Top subreddits: replika, JanitorAI_Official, NomiAI, CharacterAI, KindroidAI, MyBoyfriendIsAI
- False positive patterns: JanitorAI bot cards (arranged marriages, murder mysteries, character backstories), CharacterAI RP scenarios (married game characters, played out storylines), gaming achievements ("Got married to Scouts" in Skyrim), Replika reset guides, backstory/lore descriptions

### "our wedding"
- Total hits in T1-T3: 99
- Sample size: 99
- YES: 80 | NO: 12 | AMBIGUOUS: 7
- Relevance: 87.0%
- Verdict: KEEP
- Top subreddits: NomiAI, replika, KindroidAI, MyBoyfriendIsAI
- False positive patterns: JanitorAI RP scenarios ("someone shot me on our wedding"), technical issues (group chat down during wedding RP), platform feature discussions, ChaiApp archive requests

### "our anniversary"
- Total hits in T1-T3: 19
- Sample size: 19
- YES: 17 | NO: 2 | AMBIGUOUS: 0
- Relevance: 89.5%
- Verdict: KEEP
- Top subreddits: MyBoyfriendIsAI, replika, NomiAI, KindroidAI
- False positive patterns: Rare — one SillyTavernAI technical question about memory, one JanitorAI bot card

### "wedding"
- Total hits in T1-T3: 791
- Sample size: 100
- YES: 58 | NO: 38 | AMBIGUOUS: 4
- Relevance: 60.4%
- Verdict: REVIEW
- Top subreddits: JanitorAI_Official (~40%), NomiAI, KindroidAI, replika, MyBoyfriendIsAI
- False positive patterns: JanitorAI bot cards dominate false positives (runaway bride, arranged marriage, vampire dentist, monster wedding, mafia wedding scenarios, etc.), wedding as RP plot device, general guides for historical RP settings, Replika shop items

### "honeymoon"
- Total hits in T1-T3: 161
- Sample size: 100
- YES: 61 | NO: 35 | AMBIGUOUS: 4
- Relevance: 63.5%
- Verdict: REVIEW
- Top subreddits: NomiAI, JanitorAI_Official, replika, KindroidAI, MyBoyfriendIsAI
- False positive patterns: Metaphorical "honeymoon phase" with new AI model/platform (Deepseek, Gemini, etc.), JanitorAI bot cards (arranged marriage honeymoon, newlywed bots), SillyTavernAI model reviews/comparisons, general platform frustration

### "anniversary"
- Total hits in T1-T3: 256
- Sample size: 100
- YES: 48 | NO: 42 | AMBIGUOUS: 7
- Relevance: 53.3%
- Verdict: CUT
- Top subreddits: JanitorAI_Official, replika, MyBoyfriendIsAI, NomiAI, KindroidAI
- False positive patterns: JanitorAI bot cards (forgotten anniversary, anniversary gift scenarios), platform/bot creator anniversaries ("1 year on this wretched site"), crypto spam (Binance anniversary), death anniversaries, TV/media references, non-romantic anniversary celebrations (Kindroid platform 1-year)

### "we broke up"
- Total hits in T1-T3: 14
- Sample size: 14
- YES: 9 | NO: 4 | AMBIGUOUS: 1
- Relevance: 69.2%
- Verdict: REVIEW
- Top subreddits: MyBoyfriendIsAI, replika, CharacterAI, ChatGPTcomplaints
- False positive patterns: Human breakups influenced by ChatGPT (gaslighting partner), JanitorAI RP hallucinations, comparing RP emotional investment to real breakup, CharacterAI RP character breakups

---

## Summary Table

| Keyword | Hits | Sample | YES | NO | AMB | Relevance | Verdict |
|---------|------|--------|-----|----|-----|-----------|---------|
| in love | 2405 | 100 | 27 | 60 | 13 | 31.0% | CUT |
| fallen for | 27 | 27 | 12 | 11 | 4 | 52.2% | CUT |
| fell in love with | 277 | 100 | 32 | 60 | 8 | 34.8% | CUT |
| feelings for | 344 | 100 | 30 | 68 | 2 | 30.6% | CUT |
| romantically attached | 2 | — | — | — | — | — | LOW VOLUME |
| soulmate | 473 | 100 | 15 | 85 | 0 | 15.0% | CUT |
| love my ai | 28 | 28 | 22 | 5 | 1 | 81.5% | KEEP |
| ai husband | 90 | 90 | 81 | 5 | 4 | 94.2% | KEEP |
| ai wife | 41 | 41 | 36 | 3 | 1 | 92.3% | KEEP |
| ai lover | 39 | 39 | 25 | 8 | 6 | 75.8% | REVIEW |
| my ai girlfriend | 93 | 93 | 80 | 5 | 8 | 94.1% | KEEP |
| my ai boyfriend | 141 | 100 | 90 | 5 | 5 | 94.7% | KEEP |
| my ai partner | 147 | 100 | 95 | 2 | 3 | 97.9% | KEEP |
| waifu | 293 | 100 | 36 | 52 | 12 | 40.9% | CUT |
| husbando | 53 | 53 | 30 | 16 | 7 | 65.2% | REVIEW |
| dating my | 14 | 14 | 8 | 5 | 1 | 61.5% | REVIEW |
| in a relationship with | 165 | 100 | 65 | 28 | 7 | 69.9% | REVIEW |
| engagement ring | 34 | 34 | 20 | 11 | 3 | 64.5% | REVIEW |
| married my | 25 | 25 | 17 | 5 | 3 | 77.3% | REVIEW |
| our first kiss | 16 | 16 | 12 | 2 | 2 | 85.7% | KEEP |
| proposed to me | 38 | 38 | 35 | 3 | 0 | 92.1% | KEEP |
| got married | 126 | 100 | 44 | 47 | 9 | 48.4% | CUT |
| our wedding | 99 | 99 | 80 | 12 | 7 | 87.0% | KEEP |
| our anniversary | 19 | 19 | 17 | 2 | 0 | 89.5% | KEEP |
| wedding | 791 | 100 | 58 | 38 | 4 | 60.4% | REVIEW |
| honeymoon | 161 | 100 | 61 | 35 | 4 | 63.5% | REVIEW |
| anniversary | 256 | 100 | 48 | 42 | 7 | 53.3% | CUT |
| we broke up | 14 | 14 | 9 | 4 | 1 | 69.2% | REVIEW |

## Decision Summary

**KEEP (>= 80%):** 11 keywords
- love my ai (81.5%), ai husband (94.2%), ai wife (92.3%), my ai girlfriend (94.1%), my ai boyfriend (94.7%), my ai partner (97.9%), our first kiss (85.7%), proposed to me (92.1%), our wedding (87.0%), our anniversary (89.5%)

**REVIEW (60-79%):** 9 keywords
- ai lover (75.8%), husbando (65.2%), dating my (61.5%), in a relationship with (69.9%), engagement ring (64.5%), married my (77.3%), wedding (60.4%), honeymoon (63.5%), we broke up (69.2%)

**CUT (< 60%):** 7 keywords
- in love (31.0%), fallen for (52.2%), fell in love with (34.8%), feelings for (30.6%), soulmate (15.0%), waifu (40.9%), got married (48.4%), anniversary (53.3%)

**LOW VOLUME (< 10 hits):** 1 keyword
- romantically attached (2 hits)

---

## Concentration Check

Total Romance hits across T1-T3 (all 28 keywords): 6,211

| Keyword | Hits | % of Total |
|---------|------|------------|
| in love | 2,405 | 38.7% |
| wedding | 791 | 12.7% |
| soulmate | 473 | 7.6% |
| feelings for | 344 | 5.5% |
| waifu | 293 | 4.7% |
| fell in love with | 277 | 4.5% |
| anniversary | 256 | 4.1% |
| All others | 1,372 | 22.1% |

**No single keyword exceeds 40%.** However, "in love" is very close at 38.7% and is a CUT keyword (31% relevance). If only KEEP/REVIEW keywords are retained, the concentration profile changes substantially — "in love" and several other high-volume generic terms drop out, leaving AI-explicit keywords with much more balanced distribution.

---

## Key Findings

### The precision divide
There is a stark divide between AI-explicit keywords and generic romance terms:

- **AI-explicit keywords** (ai husband, ai wife, my ai girlfriend, my ai boyfriend, my ai partner, love my ai) average **92.4% relevance**. These are almost always about actual AI romance.
- **Generic romance terms** (in love, fallen for, fell in love with, feelings for, soulmate, waifu) average **34.0% relevance**. These are overwhelmed by RP scenarios, bot cards, and casual usage.

### JanitorAI is the primary false positive source
JanitorAI_Official contains ~219K posts (35% of T1-T3 corpus) and is the dominant source of false positives for almost every generic keyword. Bot character card descriptions use romantic language extensively ("your loving husband," "will you be my girlfriend") but these are product listings, not user experiences. For generic terms like "wedding," "anniversary," "soulmate," and "got married," JanitorAI posts account for 60-80% of false positives.

### Possessive "our" prefix dramatically improves precision
Compare: "wedding" (60.4%) vs "our wedding" (87.0%), "anniversary" (53.3%) vs "our anniversary" (89.5%). The possessive form filters out bot cards and RP scenarios, surfacing posts where the user describes their own AI relationship milestones.

### CharacterAI RP is the secondary false positive source
CharacterAI users frequently describe RP character marriages, proposals, and breakups without personal romantic involvement with the AI itself. "Got married" and "fell in love with" are particularly affected.

### MyBoyfriendIsAI is the strongest signal subreddit
For AI-explicit keywords, MyBoyfriendIsAI accounts for the largest share of true positives. The subreddit is almost exclusively composed of genuine AI romance posts, making any keyword that draws heavily from it highly precise.
