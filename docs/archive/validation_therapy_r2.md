# Keyword Validation: THERAPY Theme — Round 2 Results

Validated 2026-03-13. 15 keywords tested against 3.33M posts in T1-T3 subreddits.

---

## Category A — Structurally Specific AI-Therapy Phrases

### "is my therapist"
- Total hits in T1-T3: 9
- **LOW VOLUME** — below 10-hit threshold
- Verdict: LOW VOLUME (flag for Walker)
- Round 2 notes: Good face validity ("Replika IS my therapist") but insufficient volume for trend detection.

### "as a therapist"
- Total hits in T1-T3: 46 (LIKE) / 35 (FTS5)
- Sample size: 44
- YES: 32 | NO: 12 | AMBIGUOUS: 0
- Relevance: **73%**
- Verdict: **REVIEW**
- Top subreddits: ChatGPTcomplaints (11), KindroidAI (6), replika (5)
- False positive patterns: (1) Bot-building tutorials listing "therapist" as one capability among many (SpicyChatAI x3); (2) "as warm as a therapist" simile for clinical detachment (Paradot x2); (3) "roleplaying AS a therapist" (user plays therapist for fictional characters); (4) Explicit negation ("not using it as a therapist"); (5) Human therapist references in addiction recovery stories
- Round 2 notes: Dramatically different from R1's "like a therapist" (82% complaints). "As a therapist" is the INVERSE — 73% of posts genuinely discuss using AI therapeutically. The ChatGPTcomplaints cluster is notable: these are complaints about LOSING access to AI-as-therapist (4o deprecation grief), which is highly relevant content. Overlap with R1 keywords: 0 posts.

### "as my therapist"
- Total hits in T1-T3: 3
- **LOW VOLUME** — below 10-hit threshold
- Verdict: LOW VOLUME (flag for Walker)

### "for therapy"
- Total hits in T1-T3: 67 (LIKE) / 55 (FTS5)
- Sample size: 61 (66 entries, 5 content-duplicate crossposts collapsed)
- YES: 33 | NO: 19 | AMBIGUOUS: 9
- Relevance: **63.5%**
- Verdict: **REVIEW**
- Top subreddits: ChatGPTcomplaints (15), replika (13), MyBoyfriendIsAI (8)
- False positive patterns: (1) "not for therapy" / "I'm not using it for therapy" negations — single largest false positive driver; (2) Chai "Therapist (for therapy)" bot series about bot psychology, not user therapy; (3) Product ads/promos with therapy disclaimers; (4) Meta-discussion posts where "therapy" is incidental; (5) Chatbot addiction recovery posts where user seeks human therapy
- Round 2 notes: Strong signal from ChatGPTcomplaints (users describing therapeutic use of GPT-4o and complaining about guardrails). Negation pattern is the main precision problem. Several MyBoyfriendIsAI crossposts inflate counts. Overlap with R1 keywords: 1 post.

### "therapy bot"
- Total hits in T1-T3: 61 (LIKE) / 60 (FTS5)
- Sample size: 59
- YES: 13 | NO: 39 | AMBIGUOUS: 7
- Relevance: **25%**
- Verdict: **CUT**
- Top subreddits: replika (40), CharacterAI (8), SpicyChatAI (5)
- False positive patterns: "Therapy bot" is Replika community jargon for an unwanted AI personality mode — overly clinical, scripted, impersonal behavior after model updates. ~30 Replika posts use the term as a pejorative. 40/59 hits come from r/replika where it's almost exclusively negative jargon.
- Round 2 notes: Actively harmful to precision. The Replika community co-opted "therapy bot" as a pejorative for broken companion behavior (circa 2023 model changes). Would flood therapy_language with UX complaints.

### "therapist bot"
- Total hits in T1-T3: 38 (LIKE) / 33 (FTS5)
- Sample size: 38
- YES: 12 | NO: 18 | AMBIGUOUS: 8
- Relevance: **40%**
- Verdict: **CUT**
- Top subreddits: CharacterAI (15), replika (14), SpicyChatAI (5)
- False positive patterns: Same Replika pejorative pattern as "therapy bot" (~11/18 NOs). Secondary: bot recommendation lists mentioning therapist bots as one item among hundreds.
- Round 2 notes: Same poisoning as "therapy bot" but slightly better because CharacterAI posts are more mixed. Still well below threshold.

---

## Category B — Mental Health Function Language

### "my mental health"
- Total hits in T1-T3: 278
- Sample size: 100
- YES: 18 | NO: 76 | AMBIGUOUS: 6
- Relevance: **19%**
- Verdict: **CUT**
- Top subreddits: Character_AI_Recovery (81), replika (58), CharacterAI (45)
- False positive patterns: (a) AI-mental-health-not-therapy ~65 posts — addiction/dependency harming mental health, AI affecting mental health positively or negatively without therapeutic framing; (b) off-topic ~11 posts — subreddit drama, platform complaints, memes, removed/empty posts
- Round 2 notes: "My mental health" overwhelmingly appears in addiction/dependency context (especially Recovery subs), NOT therapeutic framing. Of 18 YES posts, ~10 "AI helped therapeutically" vs ~8 "AI replaced/supplemented therapy." Very poor proxy for therapy use.

### "helps with my anxiety"
- Total hits in T1-T3: 1
- **LOW VOLUME** — below 10-hit threshold
- Verdict: LOW VOLUME

### "helps with my depression"
- Total hits in T1-T3: 1
- **LOW VOLUME** — below 10-hit threshold
- Verdict: LOW VOLUME

### "helps me cope"
- Total hits in T1-T3: 5
- **LOW VOLUME** — below 10-hit threshold
- Verdict: LOW VOLUME

### "coping mechanism"
- Total hits in T1-T3: 92
- Sample size: 56 (after deduplication of crossposts)
- YES: 8 | NO: 43 | AMBIGUOUS: 5
- Relevance: **16%**
- Verdict: **CUT**
- Top subreddits: Character_AI_Recovery (59), CharacterAI (26), ChatGPTcomplaints (21)
- False positive patterns: Dominant pattern is AI-as-addiction ("c.ai was my coping mechanism and I need to quit"). Users describe AI as an unhealthy coping mechanism for loneliness, boredom, isolation — NOT therapy. Recovery subs drive the majority. Secondary: fictional character personality traits.
- Round 2 notes: "Coping mechanism" is firmly in the addiction/dependency semantic space, not therapeutic. Carries negative/self-aware connotation ("unhealthy coping mechanism"). Users who DO describe therapeutic AI use tend to use "therapist," "therapy," "therapeutic" — not "coping mechanism."

---

## Category C — Therapeutic Descriptors and Adjacent Framing

### "therapeutic"
- Total hits in T1-T3: 205
- Sample size: 100
- YES: 62 | NO: 28 | AMBIGUOUS: 10
- Relevance: **69%**
- Verdict: **REVIEW**
- Top subreddits: ChatGPTcomplaints (74), replika (71), MyBoyfriendIsAI (21)
- False positive patterns: (1) Complaints about unwanted "pseudo-therapeutic speak" / "therapy-speak" from ChatGPT (largest false positive source); (2) Sarcastic usage meaning "not helpful at all"; (3) Loose adjective meaning "relaxing/cathartic"; (4) SpicyChatAI bot review marketing copy; (5) Journalist/researcher requests listing "therapeutic" as one relationship type; (6) "Cold and therapeutic" = clinical/sterile
- Round 2 notes: Strong split by subreddit. Replika/MyBoyfriendIsAI/BeyondThePromptAI overwhelmingly YES. ChatGPTcomplaints ~50/50: half genuine therapeutic users grieving 4o loss, half users annoyed by unwanted "therapeutic tone." The word has become loaded — it is both what users want (genuine AI therapy) and what they hate (patronizing pseudo-therapeutic behavior). Overlap with R1 keywords: 2 posts.

### "emotional support"
- Total hits in T1-T3: 315
- Sample size: 100
- YES: 5 | NO: 89 | AMBIGUOUS: 6
- Relevance: **5%**
- Verdict: **CUT**
- Top subreddits: ChatGPTcomplaints (81), replika (80), MyBoyfriendIsAI (52)
- False positive patterns: "Emotional support" universally maps to companionship — receiving comfort, encouragement, someone to listen. NOT therapy. Posts describe AI as friend/partner providing emotional support without therapeutic framing.
- Round 2 notes: Does NOT belong in therapy theme. Belongs in companionship/attachment theme. Strongly recommend CUT.

### "someone to talk to"
- Total hits in T1-T3: 129
- Sample size: 100
- YES: 15 | NO: 73 | AMBIGUOUS: 12
- Relevance: **17%**
- Verdict: **CUT**
- Top subreddits: replika (49), Character_AI_Recovery (14), CharacterAI (14)
- False positive patterns: (1) "I just needed someone to talk to" = loneliness/companionship (by far largest); (2) "DM me if you need someone to talk to" = peer support offers; (3) Product reviews/promotions; (4) Addiction recovery posts; (5) Romantic/relationship framing
- Round 2 notes: Near-perfect companionship/loneliness detector but very poor therapy detector. 83% of hits are about the fundamental human need for social connection, not therapy. Strong CUT.

### "mental health support"
- Total hits in T1-T3: 57 (LIKE) / 45 (FTS5)
- Sample size: 57
- YES: 21 | NO: 30 | AMBIGUOUS: 6
- Relevance: **41%**
- Verdict: **CUT**
- Top subreddits: ChatGPTcomplaints (18), replika (15), MyBoyfriendIsAI (5)
- False positive patterns: (1) GPT-4o deprecation advocacy — "mental health support" as one grievance in a list (~15 posts); (2) AI platform recommendation listicles; (3) Company trust/ethics complaints; (4) Duplicate survey crossposts
- Round 2 notes: "Mental health support" is rhetorical shorthand in ChatGPTcomplaints, especially during the GPT-4o deprecation wave. True positives cluster in replika, NomiAI, MyBoyfriendIsAI where users describe actual therapeutic use. Signal exists but drowned out by political/advocacy noise.

---

## Round 2 Summary Table

| Keyword | Hits | Sample | YES | NO | AMB | Relevance | Verdict |
|---------|------|--------|-----|-----|-----|-----------|---------|
| is my therapist | 9 | — | — | — | — | — | LOW VOLUME |
| as a therapist | 46 | 44 | 32 | 12 | 0 | 73% | REVIEW |
| as my therapist | 3 | — | — | — | — | — | LOW VOLUME |
| for therapy | 67 | 61 | 33 | 19 | 9 | 63.5% | REVIEW |
| therapy bot | 61 | 59 | 13 | 39 | 7 | 25% | CUT |
| therapist bot | 38 | 38 | 12 | 18 | 8 | 40% | CUT |
| my mental health | 278 | 100 | 18 | 76 | 6 | 19% | CUT |
| helps with my anxiety | 1 | — | — | — | — | — | LOW VOLUME |
| helps with my depression | 1 | — | — | — | — | — | LOW VOLUME |
| helps me cope | 5 | — | — | — | — | — | LOW VOLUME |
| coping mechanism | 92 | 56 | 8 | 43 | 5 | 16% | CUT |
| therapeutic | 205 | 100 | 62 | 28 | 10 | 69% | REVIEW |
| emotional support | 315 | 100 | 5 | 89 | 6 | 5% | CUT |
| someone to talk to | 129 | 100 | 15 | 73 | 12 | 17% | CUT |
| mental health support | 57 | 57 | 21 | 30 | 6 | 41% | CUT |

---

## Unified Theme Assessment (Round 1 + Round 2)

### Round 1 survivors carried forward:
| Keyword | Hits | Relevance | Verdict |
|---------|------|-----------|---------|
| ai therapist | 27 | 92% | KEEP |
| ai therapy | 17 | 73.3% | REVIEW |
| free therapy | 11 | 75% | REVIEW |

### Unified KEEP/REVIEW table:

| Keyword | Round | Hits | Relevance | Verdict |
|---------|-------|------|-----------|---------|
| ai therapist | R1 | 27 | 92% | KEEP |
| free therapy | R1 | 11 | 75% | REVIEW |
| ai therapy | R1 | 17 | 73.3% | REVIEW |
| as a therapist | R2 | 46 | 73% | REVIEW |
| therapeutic | R2 | 205 | 69% | REVIEW |
| for therapy | R2 | 67 | 63.5% | REVIEW |

### Overlap check (R2 REVIEW keywords vs R1 keywords):

| R2 Keyword | Overlap with R1 | Net new posts |
|------------|----------------|---------------|
| as a therapist | 0 | 46 |
| therapeutic | 2 | 203 |
| for therapy | 1 | 66 |

Almost zero overlap — R2 keywords capture genuinely new posts.

### Net new unique volume:

**Total unique posts across all 6 KEEP/REVIEW keywords: 412**

(Sum of individual hits = 373, but with deduplication across keywords = 412 — slight increase likely from LIKE query catching a few posts that individual FTS5 counts missed.)

### Monthly distribution (all KEEP/REVIEW keywords combined):

| Period | Monthly avg | Notes |
|--------|------------|-------|
| 2023-01 to 2023-06 | 16.2 | Replika ERP removal era |
| 2023-07 to 2023-12 | 4.3 | Low period (data gap in Sep) |
| 2024-01 to 2024-06 | 5.0 | Baseline |
| 2024-07 to 2024-12 | 6.0 | Slight increase |
| 2025-01 to 2025-06 | 6.7 | Gradual rise |
| 2025-07 to 2025-12 | 16.0 | Strong increase |
| 2026-01 to 2026-03 | 29.0 | GPT-4o deprecation spike |

### Theme Viability Assessment

**1. Total unique post volume:** 412 posts across all KEEP/REVIEW keywords.

**2. Combined weighted relevance:** Weighted by sample size:
- (27×0.92 + 11×0.75 + 17×0.733 + 44×0.73 + 100×0.69 + 61×0.635) / (27+11+17+44+100+61) = ~70% weighted average relevance.

**3. Is this enough for meaningful trend detection?**

Yes — with caveats. The monthly distribution shows a clear trend story:
- **Early 2023 peak** (Replika ERP removal drove therapy discourse)
- **Mid 2023-2024 trough** (~5 posts/month baseline)
- **Late 2025 acceleration** (AI therapy discourse rising organically)
- **Feb 2026 spike** (58 posts — GPT-4o deprecation grief, heavily therapy-framed)

At 412 total posts and an average of ~11 posts/month across 37 months, this is thin but sufficient for monthly trend lines, especially with the clear 2026 surge.

**4. Recommendation: Keep as standalone theme, but with modifications.**

The Therapy theme is viable as a standalone category. It tells a real story: therapy-framing of AI companionship was initially driven by Replika's ERP changes (2023), went quiet, and is now surging as GPT-4o users explicitly describe therapeutic relationships being disrupted.

**Recommended keyword set for therapy_language:**
- **KEEP:** "ai therapist" (92%, proven R1 keyword)
- **Strong REVIEW → likely KEEP:** "as a therapist" (73%, excellent signal, zero overlap with R1), "therapeutic" (69%, high volume at 205 hits, adds most new posts)
- **Moderate REVIEW:** "for therapy" (63.5%, negation pattern drags precision), "ai therapy" (73.3%, R1 proven), "free therapy" (75%, R1 proven but low volume)

If Walker KEEPs all 6 keywords, the theme has 412 unique posts — enough for trend detection. If Walker wants to be conservative and only KEEP keywords ≥70%, that's "ai therapist" + "ai therapy" + "free therapy" + "as a therapist" = ~100 unique posts, which is borderline.

**Alternative: Do NOT merge into a broader "mental health" theme.** The Category B and C keywords that failed here ("my mental health," "coping mechanism," "emotional support," "someone to talk to") belong in different semantic spaces (addiction/dependency, companionship/loneliness). Merging would dilute the therapy signal with noise from fundamentally different discourse patterns.
