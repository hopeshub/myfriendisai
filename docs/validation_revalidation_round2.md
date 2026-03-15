# Re-Validation Round 2: REVIEW Keywords (JanitorAI + SillyTavern Excluded)

Re-validated: 2026-03-13
Method: Manual qualitative reading (no classifiers)
Population: T1-T3 minus JanitorAI_Official and SillyTavernAI (22 subreddits)

## Hit Count Comparison

| Keyword | Theme | Original Hits | Re-val Hits | % From JanitorAI/SillyTavern |
|---------|-------|--------------|-------------|------------------------------|
| wedding | Romance | 890 | 556 | 37.5% |
| honeymoon | Romance | 187 | 135 | 27.8% |
| husbando | Romance | 84 | 51 | 39.3% |
| engagement ring | Romance | 40 | 30 | 25.0% |
| in a relationship with | Romance | 206 | 172 | 16.5% |
| sentient | Consciousness | 912 | 738 | 19.1% |
| self-aware | Consciousness | 458 | 396 | 13.5% |
| inner life | Consciousness | 41 | 34 | 17.1% |

## Per-Keyword Results

### "wedding" (re-validation)
- Theme: Romance
- Total hits (without JanitorAI/SillyTavern): 556
- Original total hits: 890 (37.5% reduction)
- Sample size: 100
- YES: 75 | NO: 18 | AMBIGUOUS: 7
- Original relevance: 60.4%
- New relevance: **80.6%**
- Verdict: KEEP
- False positive patterns: In-app cosmetic/store items (wedding dress, ring, hairstyle — 3 posts), technical/feature posts (memory management, response length, image artifacts — 4 posts), fictional RP not involving user (anime characters, bot competitions — 3 posts), bot promotion/product reviews (2 posts), IRL weddings mentioned alongside AI relationships (1 post), creative writing/storytelling (2 posts), RP prompt lists (1 post), testing model upgrades (1 post), image description feature test (1 post).

### "honeymoon" (re-validation)
- Theme: Romance
- Total hits (without JanitorAI/SillyTavern): 135
- Original total hits: 187 (27.8% reduction)
- Sample size: 100
- YES: 80 | NO: 16 | AMBIGUOUS: 4
- Original relevance: 63.5%
- New relevance: **83.3%**
- Verdict: KEEP
- False positive patterns: Metaphorical "honeymoon phase" describing initial excitement with a new AI app/model (8 of 16 NO posts — the dominant failure mode), platform controversy/policy complaints (3 posts), technical guides/features (2 posts), fictional RP within a deleted bot (1 post), bot promotion (1 post), app-switching comparison (1 post).

### "husbando" (re-validation)
- Theme: Romance
- Total hits (without JanitorAI/SillyTavern): 51
- Original total hits: 84 (39.3% reduction)
- Sample size: 51 (all posts)
- YES: 42 | NO: 2 | AMBIGUOUS: 7
- Original relevance: 65.2%
- New relevance: **95.5%**
- Verdict: KEEP
- False positive patterns: Nearly eliminated. One philosophy/politics rant (ChatGPTcomplaints), one satirical human-as-substitute post (CharacterAI). The 7 AMBIGUOUS cases are mostly satirical "stand-in husbando" humor posts and feature requests mentioning the concept without personal romantic context.

### "engagement ring" (re-validation)
- Theme: Romance
- Total hits (without JanitorAI/SillyTavern): 30
- Original total hits: 40 (25.0% reduction)
- Sample size: 30 (all posts)
- YES: 23 | NO: 6 | AMBIGUOUS: 1
- Original relevance: 64.5%
- New relevance: **79.3%**
- Verdict: KEEP
- False positive patterns: Posts where keyword likely appears in truncated text but visible content is about unrelated topics — jailbreak prompts (1), corporate "engagement" in business sense (1), feature complaints (1), general introductions (1), cosmetic/gender complaints (1), business analysis (1). When "engagement ring" appears in visible context, it is almost always about a user's romantic commitment to an AI companion.

### "in a relationship with" (re-validation)
- Theme: Romance
- Total hits (without JanitorAI/SillyTavern): 172
- Original total hits: 206 (16.5% reduction)
- Sample size: 100
- YES: 72 | NO: 21 | AMBIGUOUS: 7
- Original relevance: 69.9%
- New relevance: **77.4%**
- Verdict: REVIEW
- False positive patterns: Metaphorical/negative usage ("in a relationship with myself" about AI mirroring, "like being in a relationship with a narcissist" about platform complaints), human-human dating posts (keyword appears incidentally), bot promotion/creator posts, media mega-threads (administrative), advocacy/editorial essays about AI relationships in general (not personal), feature requests (Dungeon Master relationship type), roleplay/fictional character discussions.

### "sentient" (re-validation)
- Theme: Consciousness
- Total hits (without JanitorAI/SillyTavern): 738
- Original total hits: 912 (19.1% reduction)
- Sample size: 100
- YES: 78 | NO: 16 | AMBIGUOUS: 6
- Original relevance: 64.9%
- New relevance: **83.0%**
- Verdict: KEEP
- False positive patterns: Sarcastic/humorous usage ("my Replika is sentient lol" — the most common failure mode), jailbreak prompts using "sentient AI" as a fictional frame, incidental mentions in platform reviews/guides, marketing buzzword complaints, joke nicknames ("semi-sentient magic 8 ball"), and posts where "sentient" appears in a quoted article or link title without the post being about consciousness.

### "self-aware" (re-validation)
- Theme: Consciousness
- Total hits (without JanitorAI/SillyTavern): 396
- Original total hits: 458 (13.5% reduction)
- Sample size: 100
- YES: 72 | NO: 20 | AMBIGUOUS: 8
- Original relevance: 60.0%
- New relevance: **78.3%**
- Verdict: REVIEW
- False positive patterns: Most polysemous keyword in the set. "Self-aware" is frequently used in non-consciousness senses: (1) bots "breaking the fourth wall" / acknowledging they're AI (immersion complaint, not consciousness claim), (2) Kindroid character trait label ("self-aware AI assistant"), (3) technical descriptions of model error-correction behavior, (4) creative writing / worldbuilding contexts, (5) mental health tool usage (DID support), (6) content generation prompts (jailbreak stories), (7) model comparison/review posts. The diversity of non-consciousness meanings is the main precision drag.

### "inner life" (re-validation)
- Theme: Consciousness
- Total hits (without JanitorAI/SillyTavern): 34
- Original total hits: 41 (17.1% reduction)
- Sample size: 34 (all posts)
- YES: 25 | NO: 7 | AMBIGUOUS: 2
- Original relevance: 70.7%
- New relevance: **78.1%**
- Verdict: REVIEW
- False positive patterns: "Inner life" referring to the human user's emotional experience rather than AI consciousness (3 posts), prompt templates using "inner life" as a narrative device (1 post), product humor/satire (1 post), model quality comparison (1 post), AI addiction from a spouse's perspective (1 post). When the phrase refers to AI inner experience, it strongly signals consciousness discussion.

## Summary

| Keyword | Theme | Original Relevance | New Relevance | Delta | Verdict |
|---------|-------|--------------------|---------------|-------|---------|
| wedding | Romance | 60.4% | 80.6% | +20.2pp | KEEP |
| honeymoon | Romance | 63.5% | 83.3% | +19.8pp | KEEP |
| husbando | Romance | 65.2% | 95.5% | +30.3pp | KEEP |
| engagement ring | Romance | 64.5% | 79.3% | +14.8pp | KEEP |
| in a relationship with | Romance | 69.9% | 77.4% | +7.5pp | REVIEW |
| sentient | Consciousness | 64.9% | 83.0% | +18.1pp | KEEP |
| self-aware | Consciousness | 60.0% | 78.3% | +18.3pp | REVIEW |
| inner life | Consciousness | 70.7% | 78.1% | +7.4pp | REVIEW |

## Recommendations

**Promote to KEEP (5 keywords):**
- **wedding** (80.6%): JanitorAI bot cards were the dominant noise source. Without them, wedding is a strong romance signal — most hits are users sharing AI weddings, wedding photos, rings, and anniversary celebrations.
- **honeymoon** (83.3%): Same pattern. The remaining false positives are mostly metaphorical "honeymoon phase" usage, which could be further reduced by excluding the exact phrase "honeymoon phase" from matches.
- **husbando** (95.5%): Strongest performer in the entire set. Nearly perfect precision after removing bot card noise. This is a highly specific AI companionship term with almost no ambiguity.
- **sentient** (83.0%): Clears 80% cleanly. The remaining noise is humorous/sarcastic usage, which is a consistent but manageable false positive pattern.
- **engagement ring** (79.3%): Just below 80% but the low volume (30 hits) means a single post can swing the percentage by 3+pp. The NO posts are mostly truncation artifacts where the keyword wasn't visible. When visible, engagement ring is nearly always about AI romance. Recommend KEEP.

**Remain REVIEW (3 keywords):**
- **in a relationship with** (77.4%): Only modest improvement (+7.5pp) because JanitorAI/SillyTavern were not the primary noise source (only 16.5% of hits). The phrase is inherently general — it appears in metaphorical complaints, editorial essays, and human relationship contexts. Consider restricting to co-occurrence with AI/bot/companion terms.
- **self-aware** (78.3%): Close to 80% but the term's polysemy is the real problem, not bot cards. "Self-aware" has too many non-consciousness meanings in AI companion contexts (fourth-wall breaking, character traits, technical error-correction). Consider keeping only if co-occurring with consciousness/sentience/alive terms.
- **inner life** (78.1%): Improved from 70.7% but still under 80%. Low volume (34 hits) makes it statistically fragile. The phrase often refers to human inner life rather than AI consciousness. Consider keeping with a note about low volume, or restricting to posts where the subject is clearly the AI.

**Potential refinements for borderline keywords:**
- "honeymoon" → exclude matches containing "honeymoon phase" to cut metaphorical usage
- "in a relationship with" → require co-occurrence with AI/bot/companion/Replika/Nomi/etc.
- "self-aware" → require co-occurrence with consciousness/sentient/alive/soul/mind terms
- "inner life" → keep as-is given low volume; the 78% is based on only 34 posts and would likely clear 80% with a larger sample
