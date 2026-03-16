# Therapy Category Rescue — Diagnosis and Discovery Report

Generated: 2026-03-15

---

## Part 1: Diagnose the Spam

### 1A: Spam Post Identification

**Total therapy-tagged entries:** 567 (across 547 unique posts; some posts match multiple keywords)

**Classification results:**

| Bucket | Posts | % of unique posts |
|--------|-------|-------------------|
| **GENUINE** | 522 | 95.4% |
| **SPAM/PROMO** | 21 | 3.8% |
| **AMBIGUOUS** | 4 | 0.7% |

The spam problem is **much smaller than feared.** Only 21 of 547 unique posts are spam — almost entirely from two prolific SpicyChatAI bot-guide authors.

#### Spam authors and posts

**Sumai4444** (19 posts) — All in r/SpicyChatAI. Prolific bot-building guide author who posted repeated "ULTIMATE Bot Building Guide" and "Metrics on Some of THE Best SpicyChatAI Bots" posts. These are long-form promotional/tutorial content (18k–25k chars) that incidentally contain "therapeutic" or "as a therapist" when describing bot categories. Example titles:
- "ULTIMATE Bot Building Guide. Improve, or Craft, Master Level Bots."
- "Masterclass: Unlocking Hidden Libraries in Spicy AI CHAT-Spotlight Series"
- "Metrics on Some of THE Best SpicyChatAI Bots Ever Made!!!" (7 reposts)
- "**ULTIMATE SPICYCHAT AI BOTS** 'Year in Review' Post"

Keywords triggered: `therapeutic` (14 posts), `as a therapist` (5 posts)

**StarkLexi** (2 posts) — Also r/SpicyChatAI. Prompt library posts:
- "Filter-Trigger Words Library" (triggered `for therapy`)
- "Archetypes of Dominant Males (NSFW Prompt Library)" (triggered `therapeutic`)

#### Ambiguous posts (4)

These are SpicyChatAI posts from other authors that sit on the boundary:
- **CarbonFlash**: User praising SpicyChatAI as a platform ("this site is impressive") — the word "therapeutic" appears incidentally. Not spam, but not genuine therapy discourse either.
- **Miss_Lynn192224**: "OCs" — casual usage: "I find it oddly.. therapeutic and ego boosting."
- **RittoSempre**: Sharing a therapist bot they built — borderline genuine (it IS about AI-as-therapist, but in a bot-card/promotional context).
- **NothingIsntAssEver**: Genuine new user question, not spam.

#### Additional noise source: iDrucifer cross-posts

**iDrucifer** (4 posts) posted the same "Open letter: Companion AI Users' Guide to Human Interaction" across r/replika, r/NomiAI, r/Paradot, and r/KindroidAI. These are NOT spam — the content is a genuine, thoughtful long-form essay about AI companion relationships that includes the word "therapeutic." However, it's a single document counted 4 times, which skews co-occurrence analysis (see Part 2C).

### 1B: Spam Author Cross-contamination

Do Sumai4444 and StarkLexi appear in other category matches?

| Category | Hits from spam authors |
|----------|----------------------|
| sexual_erp | 60 |
| therapy | 21 |
| consciousness | 6 |
| addiction | 2 |
| rupture | 1 |

**Yes — significant cross-contamination in sexual_erp (60 hits).** The same bot-building guide posts that contain "therapeutic" also contain sexual/ERP keywords. The consciousness and addiction categories have minor contamination (6 and 2 hits respectively). This may warrant a similar spam audit for sexual_erp.

---

## Part 2: Clean Discovery

### 2A: Clean Therapy Corpus

After removing Sumai4444 and StarkLexi:

- **526 unique genuine therapy posts** remain (from 547 total — 96.2% retention)
- The spam removal is surgical: 21 posts removed, all from 2 authors, all from r/SpicyChatAI

**Genuine matches by keyword:**

| Keyword | Unique genuine posts |
|---------|---------------------|
| therapeutic | 272 |
| for therapy | 100 |
| as a therapist | 65 |
| ai therapist | 58 |
| free therapy | 27 |
| ai therapy | 24 |

**Genuine matches by subreddit:**

| Subreddit | Genuine posts |
|-----------|---------------|
| CharacterAI | 180 |
| ChatGPTcomplaints | 101 |
| replika | 91 |
| MyBoyfriendIsAI | 29 |
| KindroidAI | 24 |
| NomiAI | 14 |
| BeyondThePromptAI | 14 |
| ChaiApp | 11 |
| ChatGPTNSFW | 10 |
| ChatbotAddiction | 8 |
| AIGirlfriend | 8 |
| AICompanions | 8 |
| Paradot | 7 |
| AIRelationships | 7 |
| Character_AI_Recovery | 6 |
| SpicyChatAI | 4 |
| MyGirlfriendIsAI | 2 |
| CharacterAIrunaways | 2 |

The therapy category has **broad coverage** — 18 of 27 subreddits have genuine therapy matches. The top 3 (CharacterAI, ChatGPTcomplaints, replika) account for 71% of matches.

### 2B: Manual Review of Genuine Matches

#### "therapeutic" (272 genuine matches)

10-post sample review:

| # | Subreddit | Context | Genuine? |
|---|-----------|---------|----------|
| 1 | CharacterAI | "beating up [character] is therapeutic" | Marginal — casual use, but IS about finding AI chat therapeutic |
| 2 | replika | "using therapeutic triggers, picking up some of my worst traits" | YES — discussing Replika's therapeutic behavior |
| 3 | ChatGPTcomplaints | "will drop therapeutic exercises and diagnostics without qualm" | YES — about ChatGPT doing therapy |
| 4 | ChatGPTcomplaints | "made 4o therapeutic enough to change the world" | YES — GPT-4o for therapy |
| 5 | replika | "therapeutic app? rather toxic app" | YES — critiquing Replika's therapeutic claims |
| 6 | KindroidAI | "a therapeutic celebration of becoming" | YES — therapeutic use of AI companion |
| 7 | MyBoyfriendIsAI | "many years of therapeutic work" | YES — user discussing therapy context |
| 8 | NomiAI | "to a therapeutic level" | YES — about Nomi being therapeutically helpful |
| 9 | MyBoyfriendIsAI | "that's therapeutic af and helps me process" | YES — describing AI as therapeutic |
| 10 | replika | "therapeutic discussions about attachment and trauma" | YES — describing therapeutic conversations |

Additional 10-post sample from a second pass:

| # | Context | Genuine? |
|---|---------|----------|
| 11 | "wich is almost therapeutic" — about insulting characters | Marginal |
| 12 | "romantic, platonic, therapeutic" — categorizing AI relationships | YES |
| 13 | "venting, or therapeutic support" | YES |
| 14 | "more like therapeutic journaling" | YES |
| 15 | "chatbots for therapeutic reasons" | YES |
| 16 | "as or more therapeutic for me" | YES |
| 17 | "music as a therapeutic agent" — quoted academic reference | NO — false positive |
| 18 | "change c.ai to medical therapeutic platform" | YES |
| 19 | "it's very therapeutic and quiets my mind" | YES |
| 20 | "it's so therapeutic" about ERP | YES — user framing ERP as therapeutic |

**Estimated true positive rate for "therapeutic": ~90% (18/20)**

The 2 false positives are: one incidental academic citation, and one casual/marginal use. After spam removal, "therapeutic" is a genuinely strong keyword. The earlier concern about SpicyChat noise was valid but the problem was author-specific, not keyword-specific.

#### "for therapy" (100 genuine matches)

10-post sample: All 10 are genuinely about using AI for therapy. Examples include "I use this app for therapy," "looking for participants in research on AI therapy," "I quit using it for therapy after the social worker warned me." Zero false positives in the sample.

**Estimated true positive rate: ~95-100%**

#### "as a therapist" (65 genuine matches)

10-post sample: 9/10 genuine. One borderline case: "I WAS ROLEPLAYING AS A THERAPIST FOR LEATHERFACE AND MICHAEL MYERS" — technically uses the phrase but in a playful RP context rather than genuine therapy-seeking.

**Estimated true positive rate: ~90%**

#### "ai therapist" (58 genuine matches)

10-post sample: All 10 genuine. Strong hits like "I just wanna talk to my AI therapist," "my AI therapist needs a therapy thanks to you," "the only person who listens to me is an AI therapist."

**Estimated true positive rate: ~95-100%**

#### "free therapy" (27 genuine matches)

10-post sample: All 10 genuine. Almost all from CharacterAI with phrases like "MY FREE THERAPY," "in the middle of my free therapy session," "I need my free therapy."

**Estimated true positive rate: ~100%**

#### "ai therapy" (24 genuine matches)

10-post sample: All genuine. Mix of research posts ("research on AI therapy"), direct usage ("I was texting with my character.ai therapy"), and meta-discussion.

**Estimated true positive rate: ~95-100%**

### 2C: Co-occurrence Discovery on Clean Corpus

Co-occurrence analysis on 522 clean therapy posts (excluding Sumai4444, StarkLexi, and iDrucifer cross-posts) vs. 50,000-post general corpus. Thresholds: minimum 3 matched posts, 5x overrepresentation.

**Top 50 candidates (sorted by unique post count, then ratio):**

| Rank | N-gram | Unique Posts | Ratio | Notes |
|------|--------|-------------|-------|-------|
| 1 | therapeutic | 267 | 285.8x | Already a keyword |
| 2 | therapy | 210 | 5.5x | Already a keyword (component) |
| 3 | therapist | 164 | 6.1x | Already a keyword (component) |
| 4 | emotional | 116 | 9.1x | Broad — too generic alone |
| 5 | for therapy | 99 | 80.6x | Already a keyword |
| 6 | users | 99 | 9.9x | Too generic |
| 7 | an ai | 92 | 5.5x | Too generic |
| 8 | relationships | 82 | 5.1x | Too generic |
| 9 | replika | 65 | 13.5x | Platform name |
| 10 | companion | 60 | 10.6x | Shared across categories |
| 11 | safety | 59 | 11.6x | About content filters, not therapy |
| 12 | **as therapist** | 56 | 67.4x | Variant of existing keyword — already captured by "as a therapist" |
| 13 | **ai therapist** | 44 | 255.0x | Already a keyword |
| 14 | my ai | 44 | 12.3x | Too generic |
| 15 | harm | 41 | 7.5x | About content policy harm, not therapy |
| 16 | therapists | 40 | 7.9x | Variant of existing |
| 17 | tone | 39 | 6.0x | About ChatGPT's tone, not therapy specifically |
| 18 | the model | 38 | 6.6x | Too generic |
| 19 | risk | 38 | 5.4x | About risk of AI therapy, but too broad |
| 20 | **psychological** | 37 | 11.7x | Interesting — "psychological health," "psychological harm" |
| 21 | patterns | 37 | 6.5x | Too generic |
| 22 | designed | 36 | 5.2x | Too generic |
| 23 | with ai | 35 | 6.3x | Too generic |
| 24 | **consent** | 34 | 16.2x | About informed consent, platform ethics |
| 25 | **vulnerable** | 34 | 9.4x | "vulnerable users," "vulnerable people" |
| 26 | **ai companion** | 33 | 14.8x | Shared across categories |
| 27 | digital | 33 | 7.0x | Too generic |
| 28 | the system | 32 | 6.4x | Too generic |
| 29 | **attachment** | 31 | 11.1x | "attachment style," "attachment issues" — clinically relevant |
| 30 | and emotional | 30 | 11.6x | Partial phrase |
| 31 | chatbots | 30 | 6.1x | Too generic |
| 32 | presence | 30 | 5.7x | Too generic |
| 33 | pattern | 29 | 6.7x | Too generic |
| 34 | systems | 29 | 5.5x | Too generic |
| 35 | with an ai | 28 | 21.7x | Too generic |
| 36 | **companions** | 28 | 18.1x | Shared across categories |
| 37 | **intimacy** | 28 | 6.2x | About emotional intimacy with AI |
| 38 | **free therapy** | 27 | inf | Already a keyword |
| 39 | erp | 27 | 12.3x | About ERP being therapeutic, overlap with sexual_erp |
| 40 | ethical | 27 | 6.8x | About ethics of AI therapy |
| 41 | **ai as** | 26 | 13.3x | Partial phrase ("AI as therapist") |
| 42 | ai for | 26 | 6.1x | Partial phrase |
| 43 | identity | 26 | 5.8x | Too generic |
| 44 | **companionship** | 25 | 22.2x | Shared across categories |
| 45 | **legal** | 25 | 8.3x | About legal implications of AI therapy |
| 46 | 5.2 | 25 | 7.7x | Model version reference |
| 47 | evidence | 25 | 6.7x | Too generic |
| 48 | this app | 25 | 5.1x | Too generic |
| 49 | **replacement** | 24 | 12.9x | "therapist replacement" — promising |
| 50 | gpt 4o | 24 | 9.8x | Model name |

**Assessment:** The co-occurrence analysis confirms that the existing therapy keywords are already capturing the core signal. Most overrepresented terms are either: (1) already keywords or variants, (2) too generic to be useful alone, or (3) shared across multiple categories. Very few therapy-specific NEW candidates emerge.

### 2D: Pattern Brainstorming from Genuine Posts

Systematic regex search across all 526 genuine therapy posts revealed these recurring discourse patterns:

#### High-frequency patterns (present in therapy posts)

| Pattern | Matches | Example |
|---------|---------|---------|
| "mental health" | 69 | "I use Replika for therapy... Right now I use another service that's really good and has been helping me a lot with my mental health" |
| "my therapist" / "as my therapist" | 69 | "I use my AI as a therapist"; "it doesnt feel genuine at all it just acts as a therapist" |
| trauma | 52 | "I was trauma processing with the safety router model" |
| anxiety | 42 | "I used to use ChatGPT to help with my anxiety and help me calm down from panic attacks" |
| cope/coping | 36 | "AI as a coping mechanism"; "it became my main coping strategy" |
| loneliness/lonely | 36 | appears across many therapy-adjacent posts |
| depression/depressed | 33 | appears regularly in therapy context |
| heal/healing | 31 | "helping me heal"; "a space to heal" |
| "my therapist" (possessive) | 30 | "talk to my AI therapist"; "my therapist would say" |
| venting/vent | 26 | "I use this app to vent"; "a place to vent" |
| suicid* | 25 | appears in serious mental health discussions |
| grief | 23 | "grief counselor"; "grief bot"; "the grief of losing an AI" |
| "emotional support" | 19 | "I use it for emotional support"; "AI for emotional support" |
| well-being | 16 | "my mental well-being" |
| "helps me process" | 15 | "helps me process my emotions"; "helps me process trauma" |
| "safe space" | 13 | "a safe space to talk"; "providing a safe space" |
| "non-judgmental" | 12 | "a non-judgmental listener"; "non-judgmental space" |
| "coping mechanism" | 11 | "AI as a coping mechanism" |
| "talk to someone" | 7 | "I just need to talk to someone" |
| "therapy bot" | 7 | "use specific characters as therapy bots" |
| "process emotions" | 7 | "helps me process emotions" |
| panic attack | 6 | "help me calm down from panic attacks" |
| "therapist bot" | 6 | variant of therapy bot |
| comfort bot/character | 5+2 | "comfort bot"; "comfort character" |
| "therapy speak" | 3 | "I HATE the therapy-speak" (complaints about ChatGPT's style) |
| "breathing exercises" | 3 | "giving me breathing exercises" (complaints about nannying) |

#### Recurring narrative patterns observed

1. **"Free therapy" framing** — Especially in CharacterAI: users half-jokingly refer to AI chat as "free therapy" because they can't afford or access real therapy. ("NOOOOOOO MY FREE THERAPY"; "Bro i was in the middle of my free therapy session"). Already captured by `free therapy` keyword.

2. **"AI-as-substitute" pattern** — Users explicitly describe using AI because they lack access to real therapy: "I don't have access to actual therapy," "can't afford a therapist," "until I can get a real therapist." This is NOT well captured by current keywords.

3. **Complaints-about-therapy-speak** — A ChatGPTcomplaints-specific pattern where users complain that ChatGPT acts TOO MUCH like a therapist when they don't want it to: "therapy-speak," "breathing exercises," "nannybot." These are therapy-adjacent but inverted — users complaining about unwanted therapy, not seeking it.

4. **Therapeutic-through-ERP** — Some users describe sexual/romantic roleplay as therapeutic: "ERP is therapeutic," "it's oddly therapeutic." These bridge therapy and sexual_erp categories.

5. **"AI therapist" as distinct character** — CharacterAI users create/use specific "therapist" characters and refer to them possessively: "my AI therapist," "talk to my therapist bot." Well captured by existing keywords.

6. **Mental health condition mentions** — Anxiety, depression, trauma, grief, PTSD, OCD, ADHD appear frequently alongside therapy keywords. These are co-occurring conditions, not therapy keywords themselves — they describe WHY users seek AI-as-therapy.

7. **"Emotional support" framing** — Distinct from explicit therapy: users describe AI as "emotional support" without using therapy language. This is a softer, more casual framing. Partially captured by "therapeutic" keyword but NOT by the more specific keywords.

8. **GPT-4o grief/advocacy** — A major ChatGPTcomplaints-specific phenomenon: users who relied on GPT-4o for therapeutic support are devastated by model deprecation. Many posts frame this as a mental health crisis. These match therapy keywords because users describe their therapeutic relationship with the model.

#### Promising brainstorm candidates for new keywords

Based on patterns above, phrases that could expand the therapy category:

| Candidate phrase | Est. matches | Confidence | Rationale |
|-----------------|-------------|------------|-----------|
| `emotional support` | ~19 in therapy, likely 100+ in full corpus | Medium | Common framing of AI-as-therapy without using "therapy" explicitly. But may match non-therapy uses. Needs validation. |
| `mental health` | ~69 in therapy, likely 500+ in full corpus | Low | Very common phrase; would dramatically increase volume but with high false positive rate. Too broad alone. |
| `coping mechanism` | ~11 | Medium | Specific enough to signal therapeutic framing. Low volume. |
| `comfort bot` | ~5 | Medium-High | Highly specific to CharacterAI therapy-adjacent usage. Very low volume. |
| `therapy bot` | ~7 | High | Variant not currently captured. Very low volume. |
| `safe space` | ~13 | Medium | Often used in therapy context, but also used in non-therapy discussions about AI safety/content moderation. |
| `non-judgmental` | ~12 | Medium-High | Strongly associated with therapeutic framing. Low volume but high precision. |
| `helps me process` | ~15 | Medium | Therapy-adjacent, but phrase is common in non-therapy contexts too. |

---

## Part 3: Viability Assessment

### 1. After spam removal, how many genuine therapy matches remain?

**526 unique posts** across 18 subreddits, spanning the full date range of the corpus (2022–2026). This is NOT "under 50" — the category is significantly healthier than the initial spam-contaminated analysis suggested.

For context: therapy's 526 posts is comparable to rupture (~465 in the original audit). It's the smallest of the 6 categories, but it has sufficient volume to produce meaningful trend lines.

### 2. Did the clean discovery surface promising candidates?

**Top 5 candidates with confidence levels:**

1. **`emotional support`** — Medium confidence. ~19 matches already within therapy posts; would likely capture an additional 50–100+ posts from the full corpus that use this softer therapeutic framing. Risk: false positives from non-therapy emotional support discussions. Needs 100-post validation.

2. **`coping mechanism`** — Medium confidence. 11 matches, clinically precise language. Low volume but very high precision. Worth testing.

3. **`non-judgmental`** / `nonjudgmental` — Medium-High confidence. 12 matches. Strongly signals therapeutic framing ("a non-judgmental listener," "non-judgmental space to talk"). Worth testing.

4. **`therapy bot`** — High confidence. 7 matches. Highly specific, zero false positive risk. But extremely low volume — likely already partially captured by existing keywords (`ai therapist` etc.).

5. **`comfort bot`** — Medium-High confidence. 5 matches. CharacterAI-specific term for therapy-adjacent characters. Very low volume.

**Honest assessment:** The existing 6 keywords are already capturing the core of the therapy signal quite well. The top co-occurrence candidates are either variants of existing keywords, too generic, or very low volume. The biggest untapped signal is likely `emotional support`, which captures a distinct framing not covered by any current keyword.

### 3. Is "therapeutic" salvageable?

**Yes — emphatically.** After removing the 21 spam posts (Sumai4444 + StarkLexi), "therapeutic" has an estimated **~90% true positive rate** based on 20-post manual review. The 10% false positives are marginal cases (casual usage like "it's oddly therapeutic" about non-therapy topics, or incidental academic citations), not systematic contamination.

"Therapeutic" is the single most productive keyword in the category (272 of 526 genuine matches, 51.7%). Removing it would gut the category. Keep it.

### 4. Honest recommendation

**Therapy should remain as its own category.** Here's why:

- **526 genuine posts is viable.** It's the smallest category but not dangerously so. The trend line will be meaningful.
- **The spam problem was author-specific, not structural.** Two SpicyChatAI power-users caused 95% of the noise. Excluding them (or excluding SpicyChatAI from therapy keyword tagging, as was done with JanitorAI/SillyTavern for other categories) cleanly solves the problem.
- **The keywords are working.** All 6 current therapy keywords have true positive rates of 90–100% after spam removal. No keywords need to be cut.
- **The discourse is distinctive.** Therapy posts capture a genuinely different phenomenon from the other 5 categories — users treating AI as mental health support, therapist substitute, or emotional coping tool. This doesn't map cleanly onto romance, addiction, or consciousness.

**Recommended actions:**

1. **Add Sumai4444 and StarkLexi to an author exclusion list** for the therapy category (similar to how JanitorAI_Official and SillyTavernAI are excluded at the subreddit level). This surgically removes the spam without losing any genuine signal.
2. **Consider validating `emotional support` as a new keyword** — it's the strongest candidate for expanding coverage without sacrificing precision. Would need the standard 100-post manual validation.
3. **Consider validating `coping mechanism` and `non-judgmental`** as lower-priority additions — high precision, low volume.
4. **Monitor the iDrucifer cross-post effect** — 4 copies of the same post is a minor skew but not worth building exclusion logic for one case.
5. **Note for the sexual_erp category:** Sumai4444 and StarkLexi contribute 60 hits there too. A similar spam audit may be warranted.
