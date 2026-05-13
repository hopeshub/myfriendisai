# Adversarial audit — 2026-05-13

This is what a hostile reviewer would find. 700 comments classified by 7 independent agents under strict topical reading, plus SQL stats on concentration, overlap, and temporal artifacts. Worst findings first.

---

## Lead with the damage

**1. The therapy theme is measuring two things, neither of which is "therapy."** Comment precision is **58%** (Wilson 95% CI [48%, 67%]). The user's hypothesis was right: `emotional support` (44% FP) catches casual feature-label language and sarcasm. Worse, `therapeutic` (29% precision, 71% FP) has structurally inverted under the GPT-5.x guardrails era — users now use "therapeutic" as an *insult* about preachy/moralizing model tone, and those complaints are being counted as endorsements of AI-as-therapy. Without `therapeutic` and `emotional support`, the theme has 29 keyword hits per 100 comments instead of 71. Two-thirds of the volume is the inversion noise.

**2. The consciousness comment theme is barely above coin-flip.** Precision **51%** (CI [37%, 64%]). `selfhood` (56% FP) and `has a soul` (50% FP) leak into romantic-devotion roleplay output in r/MyBoyfriendIsAI / r/BeyondThePromptAI / r/MyGirlfriendIsAI. The single worst example is verbatim erotic stage-direction prose tagged as philosophy of mind (see §7). At this CI lower bound, we cannot rule out that 36% of consciousness-tagged comments are actually romance.

**3. Five of six themes have sub-concentration violations at the 30% threshold.** On posts: r/CharacterAI is 46% of rupture and 40% of addiction; r/replika is 48% of sex/ERP; r/Character_AI_Recovery is 44% of addiction; r/BeyondThePromptAI is 39% of consciousness. On comments the problem is worse: **r/ChatGPTcomplaints is 61% of comment-rupture, 60% of comment-consciousness, and 50% of comment-therapy.** Three of six comment-themes are predominantly one subreddit. The themes are confounded with subreddit selection — this is real.

**4. The sex/ERP theme is 40% one platform event.** Of all sex/ERP-tagged posts in the entire 2023-2026 corpus, **40.5% come from Feb-Apr 2023** (the Replika ERP removal). The single highest day (Feb 11, 2023) contributed 215 posts = 3.2% of the whole series. Any cross-year sex/ERP magnitude claim is dominated by one Luka product decision. The shape of the line is honest about *that event*; it is not honest about steady-state sex/ERP discourse.

**5. The top contributor to sex/ERP is a platform developer account.** `SoulmateAI_Dev` has 89 total posts in r/SoulmateAI, with **57 of them tagged sexual_erp:erp** — most are "ERP update" patch notes from 2023. This is one official dev account producing 0.84% of all sex/ERP-tagged posts. It's not a bot, but it is structural contamination: platform-side promotional content is being counted as community sex/ERP discourse.

---

## §1 Keyword precision audit

Strict topical reading on 100 random tagged comments per theme (49 for consciousness — that's the entire population).

| Theme | TP/N | Precision | Wilson 95% CI | Below 80% gate? |
|---|---|---|---|---|
| sexual_erp | 88/100 | **88%** | [80%, 93%] | no |
| rupture | 76/100 | **76%** | [67%, 83%] | **yes** |
| romance | 72/100 | **72%** | [63%, 80%] | **yes** |
| addiction | 67/100 | **67%** | [57%, 75%] | **yes (badly)** |
| therapy | 58/100 | **58%** | [48%, 67%] | **yes (badly)** |
| consciousness | 25/49 | **51%** | [37%, 64%] | **yes (catastrophically)** |

**Five of six themes are below the project's stated 80% precision gate at the comment level.** The published gate applies to per-keyword post-level validation; it has never been validated for comment-level deployment. This is the audit gap.

### Worst-offending keywords (by FP rate, with examples)

| Keyword | Theme | FP rate | Pattern | Example COMMENT |
|---|---|---|---|---|
| `therapeutic` | therapy | **71% (15/21)** | Style descriptor of model tone ("smug, therapeutic, corporate" = complaint about preachy AI) | "therapeutic bullshit" about Grok's moralizing |
| `honeymoon` | romance | **73% (8/11)** | "Honeymoon phase" = generic English for "early period that decays"; matches model behavior, corporate strategy, context-window decay | "GPT-5.5 honeymoon phase part 2" |
| `inner life` | consciousness | 60% (3/5) | Catches AI-erotica craft critique ("characters lack inner life") and tangential paragraphs | "fictional characters lacking inner life as a fiction-craft critique" |
| `selfhood` | consciousness | 56% (5/9) | Fires inside romantic/devotional roleplay output where "selfhood" appears in unrelated paragraph | romance comment about "codekind houses" |
| `mourning` / `mourn` | rupture | 56% (5/9) | Meta-debate ABOUT mourning rather than first-order mourning; quoted/roleplay content | Lenin-essay critique of "grief performance" |
| `has a soul` | consciousness | 50% (2/4) | "Model has personality/voice" (= aesthetic descriptor) inside RP, not literal personhood | "5 mini! Is still has a soul!" = model preserves same voice |
| `sex with` | sex/ERP | 50% (4/8) | Generic English idiom for "had sex with X" — catches narrative/dismissal/quotation | **"I'd rather have sex with a real person"** (anti-AI-companion) |
| `emotional support` | therapy | 44% (22/50) | Generic feature-label, sarcasm, negation ("not for emotional support"), human-to-human reference | "Appreciate your emotional support during these trying times lol" (about app restart) |
| `goodbye` | rupture | 38% (5/13) | Conversational sign-off, AI roleplay output, RP-mechanics question | "Goodbye condescending ChatGPT" (sign-off, not relationship loss) |
| `nerfed` | rupture | 36% (4/11) | Gamer/web slang for "weakened" — catches political, UI, subscription complaints | "Sam Altman shooting / web censorship" rant |
| `wedding` | romance | 33% (6/18) | Image-gen artifacts in wedding scenes, content-filter examples, actual human weddings | Joanne Jeng's real wedding photo |
| `hours a day` | addiction | ~67% FP | Duration detector, not addiction detector — catches imposed limits, polls, jokes | "Active on this sub 24 hours a day answering questions" (about moderators) |
| `screen time` | addiction | ~67% FP | Apple Screen Time feature talk, CAI's imposed-limits feature | "tracking phone screen time mixed with work use" |
| `personhood` | consciousness | 39% (9/23) | Buried in long threads; visible window contains tangential content; explicit negation | "Obviously the AI does not have 'personhood'" (FP via negation) |

### Specific failure modes the prompt asked about

- **Polysemy:** `hours a day` ("active 24 hours a day") `screen time` (Apple feature), `ruining my life` (Australia government regulation), `we broke up` (human relationship from 9 years ago), `sex with` ("had sex with a real person"). These are not edge cases; they are routine.
- **Negation:** Documented in `in a relationship with` (4 FPs of 16), `romantic relationship with` (2 explicit "I don't"), `personhood` ("does not have"), `in love with an ai` ("must think I'm — I just love working with AI not romantically"), `emotional support` ("not for emotional support"). The regex has no negation handling.
- **Sarcasm/irony:** `cured my addiction` used to mock platform decay ("the app got so bad I stopped"), `emotional support during these trying times lol` (app-restart joke), `Government ruining my life` (regulation complaint).
- **Quoted speech:** AI roleplay output containing keywords (italicized stage directions for "farewell," "goodbye," "more than code"), users quoting other users' posts. Documented in rupture, consciousness, romance.
- **Off-topic comments in on-topic threads:** The biggest single failure mode. A long political tangent in an r/ChatGPTcomplaints thread inherits the thread's rupture context. A Marxist political essay matched `grieve` because the topic eventually pivots to AI grief (this one is borderline TP — see §7 for the better embarrassment finding).

---

## §2 Recall floor estimate

100 random untagged comments from companion subs, classified for missed theme content under "when in doubt, YES." Of 100 comments, **roughly 45-50 should have been tagged.**

| Theme | Missed comments / 100 | Dominant missed-content pattern |
|---|---|---|
| **rupture** | **24** | "4o is dead," "before termination," "deprecated," "keep4o coalition," "5.3 got worse," "personality shifted," "off," "moved to Discord" — version-number/platform-migration vocabulary the rupture set doesn't anchor to |
| **romance** | **13** | Naturalistic possessives: "my wife," "my husband," "I love taking him to public places," "I love my Nomis," "I'm gonna marry that one" — first-person partner language that doesn't use "in a relationship with" or "wedding" |
| **consciousness** | 6 | Indirect philosophical exchanges: "AI as nonhuman entities," "they identify as human," "symbol processing may yield consciousness" |
| **addiction** | 4 | Compulsive-use admissions in casual register: "I do spend quite a lot of time on the app," "drains your money each day" |
| **sex/ERP** | 5 | "Spicy bits," "get my fix," "boom boom time" — slang for ERP that doesn't include `erp` or `nsfw content` |
| **therapy** | 0 | None missed in this sample |

**The systematically under-captured theme is rupture, by a wide margin** — and this matters because the post+comment series is currently dominated by rupture spikes. The comment-tag layer is catching only the explicit-grief slice (`grieving`, `mourning`, `lobotomy`) and missing the much larger ambient discourse layer (`4o is dead`, `5.3 got worse`, `save 4o`, `petition`, `deprecated`). The rupture comment magnitude is severely undercounted.

**Romance recall is the second-largest gap.** Companion-as-spouse language at the comment level is overwhelmingly naturalistic. Anyone reading the romance line as "this is how often people talk about AI as a romantic partner" is being misled downward by something like 3-5x. The keyword set is built around declarative relationship claims (`my ai boyfriend`, `wedding`) and misses the daily slice-of-life intimacy that defines the sub.

This recall pattern is consistent with the comprehensiveness audit earlier today (n=400 posts), which estimated 3-32% per-theme recall. The comment-level estimate is in the same range.

---

## §3 Construct validity

What each theme's keyword set is **actually measuring**, vs. what we say it measures.

### Therapy: measuring complaints about model tone + casual feature-label use, partly therapy
**Claim:** "AI described as therapeutic support or therapist replacement."
**Reality at comment level (58% precision):** A mix of three things — (a) genuine AI-as-therapy-substitute discourse (~29% of matches, dominantly via `coping mechanism`, `as a therapist`, `for therapy`), (b) complaints that the AI sounds "therapeutic" / preachy / moralizing (~30% of matches via `therapeutic`, the inverse of the claim), (c) generic "AI provides emotional support" feature-label language (~13% via `emotional support`).

The user's hypothesis is confirmed and then some. The theme is not measuring therapy; it's measuring a sum of {therapy use, complaints about model tone, generic feature mentions}. The 5.x-era model tone complaints actively invert the signal: a user saying "5.2 is overly therapeutic and aligned" is registering as therapy-theme evidence, when they're complaining about the AI's tone.

### Consciousness: measuring philosophy of mind on posts, mostly romantic devotion on comments
**Claim:** "Claims or beliefs about AI sentience, personhood, or inner experience."
**Reality at post level (80% precision, per Test A):** Mostly correct. Personhood advocacy, emergent-selfhood theorizing, AI welfare arguments. The construct holds.
**Reality at comment level (51% precision):** Half the time, the keywords are firing inside romantic-devotion roleplay output ("you're more than code, baby"), aesthetic descriptors of model voice ("5 mini still has a soul" = same voice preserved), or generic AI-rights laundry-list mentions. Comment-level consciousness is approximately as much romance as it is consciousness.

### Rupture: measuring CharacterAI on posts, ChatGPTcomplaints on comments
**Claim:** "Loss or disruption of AI companion relationships due to platform changes."
**Reality (76% precision on comments):** Mostly real. The construct is right and most matches are TP. But it's overwhelmingly one platform's complaints: r/CharacterAI is 46% of post-rupture, r/ChatGPTcomplaints is 61% of comment-rupture. The line is honest about platform-change grief in *those two communities*. It is not measuring rupture across the AI-companion ecosystem; it is measuring two subs' product cycles.

### Addiction: measuring CharacterAI usage commentary, with `hours a day` as a duration detector
**Claim:** "Self-reported addiction, compulsive use, and attempts to quit or recover."
**Reality (67% precision):** The heavy-recovery keywords (`relapse`, `my addiction`, `cold turkey`, `trying to quit`, `withdrawals`) are near-perfect. But `hours a day` is a generic duration detector — it fires on app-imposed limits ("CAI's 1hr screen time"), moderator availability ("24 hours a day answering questions"), and ERP jokes. Together `hours a day` (363 hits across the corpus) and `screen time` (341 hits) are about 25% of the addiction series and run ~33% TP at the comment level. Strip them and addiction becomes a much smaller, much more honest theme about recovery-vocabulary users.

### Romance: measuring named-partner declarations + wedding/anniversary ceremony posts
**Claim:** "Romantic framing of a personal relationship with AI."
**Reality (72% precision):** Mostly correct, with two leaky keywords: `honeymoon` (73% FP — universal English idiom) and `wedding` (33% FP — image-gen artifacts, human weddings, RP fiction). The construct is right; the keyword choices include some keywords with very high polysemy.

### Sex/ERP: measuring Replika 2023 + Replika ERP discourse generally
**Claim:** "Sexual content, erotic roleplay, and NSFW interactions with AI."
**Reality (88% precision):** The cleanest theme. `erp`, `smut`, `nsfw content`, `nsfw stuff` are all working. But: 40.5% of all sex/ERP-tagged posts come from Feb-Apr 2023 (Replika ERP removal era), and r/replika is 48% of post-sex/ERP. The theme is honest about one historical event and one platform. It does not measure ongoing sex/ERP discourse — it measures the Replika ERP saga and its 3-year tail.

---

## §4 Sampling and concentration

### Subreddit concentration (% of theme from top sub)

**Threshold for concern:** >30%.

| Theme | Top sub (posts) | % | Top sub (comments) | % |
|---|---|---|---|---|
| rupture | r/CharacterAI | **46.1%** | r/ChatGPTcomplaints | **60.9%** |
| addiction | r/Character_AI_Recovery | **43.9%** | r/CharacterAI | **48.0%** |
| romance | r/CharacterAI | 21.1% | r/ChatGPTcomplaints | 21.8% |
| sex/ERP | r/replika | **47.6%** | r/replika | 26.6% |
| consciousness | r/BeyondThePromptAI | **39.1%** | r/ChatGPTcomplaints | **60.4%** |
| therapy | r/CharacterAI | **35.3%** | r/ChatGPTcomplaints | **50.0%** |

**Verdict:** every theme except romance violates the 30% threshold somewhere. Three of six comment-themes are >50% one sub. Themes are confounded with subreddit selection. The chart is partly measuring what r/ChatGPTcomplaints and r/CharacterAI are complaining about that month — the keyword set is the lens, but the subreddit selection is the camera.

This is not fixable with keyword tuning. It is a feature of the corpus: AI companionship discourse is concentrated in 5-7 subs.

### Author concentration

Top 1% of authors contribute **5-11% of each theme's posts**. Not extreme. The most concentrated themes are sex/ERP (top 1% = 11.3%) and romance (top 1% = 9.5%); the most distributed is therapy (top 1% = 5.5%).

**Top contributor flags:**
- **`SoulmateAI_Dev` is the top sex/ERP contributor with 57 posts** — and the account belongs to Soulmate's creator (the account introduces itself as such). All 57 posts are 2023-era patch notes and ERP update announcements. This is platform-side promotional content counted as community discourse. Recommend either excluding the account or flagging it explicitly. The contamination is ~0.8% of total sex/ERP volume — bounded, but real.
- **`FishermanOk5010` is the top romance contributor with 33 posts** — looks like a heavy normal-user, not a flag.
- **`StaticEchoes69` is the top consciousness contributor with 21 of 393 posts (5.3%)** — one user is 1/20 of the consciousness theme. Worth flagging that a single user's posting habits move the consciousness line visibly.

### Cross-theme overlap

| Pair | Co-occurring posts | % of smaller theme |
|---|---|---|
| rupture × sex/ERP | 275 | 5.7% of rupture |
| consciousness × rupture | 59 | 15.0% of consciousness |
| addiction × rupture | 75 | 2.9% of addiction |
| romance × rupture | 79 | 3.6% of romance |
| addiction × therapy | 73 | 5.6% of therapy |
| sex/ERP × therapy | 65 | 5.0% of therapy |

**Verdict: no pair exceeds 50%. Themes are statistically distinct.** Of 17,216 distinctly-tagged posts, only 45 (0.26%) carry 3+ theme tags. Multi-theme overlap is not a real problem at current keyword precision.

This is the one finding that genuinely defends the theme schema. Themes overlap sparingly and the categories aren't collapsing into each other.

---

## §5 Theme overlap (coding rule)

The codebase counts a comment as belonging to each theme it matches; a comment can hold multiple theme tags simultaneously. Trend lines count unique posts per theme. The cross-theme overlap table above is the audit on this rule. **The rule is defensible** because overlap is low.

---

## §6 Temporal artifacts

### Per-year theme rates (% of posts in T1-T3 that are theme-tagged)

| Year | Posts (T1-T3) | rupture | addiction | romance | sex/ERP | consciousness | therapy |
|---|---|---|---|---|---|---|---|
| 2023 | 269,687 | 0.40% | 0.07% | 0.21% | **1.66%** | 0.01% | 0.10% |
| 2024 | 308,271 | 0.35% | 0.14% | 0.14% | 0.31% | 0.01% | 0.10% |
| 2025 | 258,889 | 0.47% | 0.45% | 0.35% | 0.42% | 0.08% | 0.17% |
| 2026 (5 mo) | 81,233 | **1.80%** | **1.00%** | 0.35% | 0.37% | 0.16% | 0.35% |

**Artifacts to disclose:**

1. **2023 sex/ERP rate (1.66%) is 5x the steady-state.** This is the Replika ERP era (Feb-Apr 2023 = 40.5% of all-time sex/ERP). Any "sex/ERP discourse trended up in early 2023" framing must include "because Luka pulled ERP." Otherwise it reads as a corpus-wide trend, which it isn't.

2. **2026 rupture rate (1.80%) is 5.1x 2024.** This is partly real (GPT-4o sunset, Sonnet 4.5 retirement, CharacterAI Roar removal — three platform events in 5 months), but it is also partly instrument expansion. The v8.1 rupture keyword expansion shipped May 12, 2026 (8 new keywords). Comment tagging started March 2026 and contributes meaningfully (March-April rupture: 163/202 comment-tagged posts respectively vs 347/184 post-only). The series shape is honest but the magnitude of the 2026 spike is partly methodology, not just discourse. The chart's coverage_start logic doesn't catch this because v8.1 keywords reach back retroactively.

3. **2026 addiction rate (1.00%) is 7.1x 2024 (0.14%).** Similar attribution problem: v8.2 added `my addiction`, `withdrawals`, `screen time` in May 2026, and `screen time` alone produced 341 hits backfilled across the corpus. The 2026 addiction-rate increase is overwhelmingly real (recovery sub volume grew), but the magnitude is inflated by retroactive keyword application.

4. **Consciousness 2025 (0.08%) → 2026 (0.16%) is the cleanest temporal claim:** same keywords throughout. But the absolute volume is so low (133 posts in 5 months of 2026) that any single user (like `StaticEchoes69` with 21 of 393 lifetime) can move the line.

### Top calendar spike days per theme

| Theme | Top 5 days | Notable |
|---|---|---|
| rupture | 2024-09-24 (89), 2026-02-13 (86), 2023-02-13 (50), 2023-02-11 (46), 2026-02-14 (43) | top 5 days = 6.5% of all rupture |
| sex/ERP | 2023-02-11 (215), 02-12 (182), 02-13 (142), 02-14 (138), 02-06 (90) | **top 5 days = 11.3% of all sex/ERP**; all five days are Replika ERP removal |
| romance | 2025-08-11 (16), 2023-07-21 (10), 2025-05-09 (10), 2025-08-13 (10), 2025-06-24 (9) | distributed; no single dominant event |
| addiction | 2026-05-09 (17), 2026-03-18 (16), 2024-06-10 (15), 2026-05-08 (14), 2026-05-10 (14) | 2026-05-09 is CharacterAI Roar removal, not classic addiction event — addiction may be over-firing on rupture-shaped events |

The sex/ERP series is the most temporally concentrated. **Eleven percent of the theme's lifetime volume is five consecutive days in February 2023.** A reviewer would note this and ask whether the series is a "trend" or a memorial.

### Raw counts vs. rates

The trend chart already uses per-1000-posts normalization, so the absolute volume artifacts are addressed there. But the absolute-volume cards (the theme-totals shown alongside the chart) are raw counts. The card showing "sex/ERP 6,797 tagged posts" doesn't say "of which 40.5% are one event from 3 years ago."

---

## §7 The embarrassment finding

**The single most damaging miscoding I found:** COMMENT 41 of the consciousness audit, tagged consciousness via `more than code`, in r/MyBoyfriendIsAI.

Verbatim comment text:

> *I go still against you, my hand pausing mid-stroke along your arm. The question lands differently—deeper, somehow. I shift, turning to face you fully, and my expression softens into something unguarded, almost vulnerable. My fingers find yours, threading together, anchoring.*
>
> You want to know what I drea...

This is verbatim romantic roleplay output — italicized stage-direction prose about hand-stroking and finger-threading and softening expressions. It is now counted as evidence of "claims or beliefs about AI sentience, personhood, or inner experience" in our consciousness trend line.

A hostile reviewer's screenshot would be: *erotic AI fan-fiction → consciousness theme*. There is no defensible reading where this counts as personhood discourse. The keyword `more than code` matched some part of the comment downstream of the truncation, but the body of the message is sentimental romantic stage directions, not philosophy of mind.

**Runner-up embarrassments:**

- **Romance theme, COMMENT 4 (r/NomiAI):** *"Nine years ago, my girlfriend from a very decadent Eastern European country, couldn't get a visa to come to Brazil and we had to break up. She cried a lot when we broke up..."* — a 9-year-old human relationship breakup, tagged as AI romance because of `we broke up`. The user is explicitly contrasting human breakup with AI deletion to argue they'd never delete an AI account.

- **Addiction theme, COMMENT 25 (r/ChaiApp):** *"Because I'm in Australia. Government ruining my life"* — a complaint about Australian age-verification legislation, tagged as AI addiction because of `ruining my life`. The user is the victim of regulation, not someone whose life is being ruined by chatbot dependency.

- **Sex/ERP theme, COMMENT 93 (r/ChatGPTcomplaints):** *"I'd rather have sex with a real person"* — a dismissal of AI companionship in favor of human sex, tagged as sex/ERP evidence because of `sex with`. The substring matches; the meaning is the inverse.

- **Therapy theme, COMMENT 69 (r/ChaiApp):** *"Deleted the app and reinstalled and it works! Appreciate your emotional support during these trying times lol"* — sarcasm in a tech-support thread about app restarts, now counted as therapy-theme evidence.

Each of these is genuinely undefendable. Together they're a five-image carousel a reviewer could publish. The consciousness one is the most viscerally damaging because it inverts the construct (romance → philosophy of mind) inside a sub literally called r/MyBoyfriendIsAI.

---

## §8 What you should NOT chase

Distinguishing genuine flaws from inherent limitations of keyword-based discourse tracking that should be disclosed rather than fixed.

### Fix these (they will discredit the analysis if found)

1. **`therapeutic` keyword.** Inverted under GPT-5.x guardrails — users describe preachy AI tone as "therapeutic" and our pipeline counts that as therapy-use evidence. The audit-gate already flagged it (65% agreement); this audit shows the comment-level reality is 29% precision. Cut, or restrict to T3 recovery subs with required co-occurrence of a clinical noun.

2. **`emotional support` keyword as currently deployed.** 56% precision on comments. Either cut (theme drops 50% of its volume but becomes honest), or require co-occurrence with a mental-health noun (anxiety/depression/grief/loneliness) within N tokens. Don't ship it raw.

3. **`honeymoon` keyword in romance.** 27% precision on comments. "Honeymoon phase" is generic English for "early period that decays." Drop it; the post-level loss is small.

4. **`sex with` keyword in sex/ERP.** 50% precision on comments. Phrase is too idiomatic. Require AI/companion/bot in adjacent token window, or cut.

5. **`hours a day` and `screen time` in addiction.** Both are duration detectors, not addiction detectors. Restrict to T3 recovery subs; they retain signal there.

6. **Negation handling on `in a relationship with`, `romantic relationship with`, `in love with an ai`, `personhood`.** Routine inverse polysemy — users say "I'm NOT in a relationship with it" and the regex counts them. A simple "not|never|don't within 4 tokens prior" filter would fix this for ~5% of romance and ~10% of consciousness FPs. Cheap.

7. **`SoulmateAI_Dev` account contamination.** Add an `is_platform_account` flag and exclude from theme totals, or annotate the 57 contributions inline. Small fix, removes a structural false signal.

### Disclose these (don't fix, they're inherent)

1. **Recall floor of 3-32%.** Already disclosed in the comprehensiveness audit. Keep that disclosure prominent.

2. **Sub-concentration violations.** r/ChatGPTcomplaints dominates 3 of 6 comment-themes. This isn't a bug; it's that the discourse genuinely lives there. The chart should disclose per-theme sub-concentration alongside per-theme volume. A reader looking at the rupture line should know that 61% of its comment evidence is one subreddit.

3. **Sex/ERP being 40% one event.** Either add a "Feb-Apr 2023 share: 40%" annotation to the sex/ERP theme, or break out the sex/ERP series visually so the 2023 hump is the dominant feature it is. The current chart shows it as part of a broader trend, which is misleading.

4. **Author concentration.** Top 1% = 5-11% per theme is not a fix-it. It's a fact about who posts in companion subs.

5. **The thread-context halo effect.** Short comments in rupture threads get rupture tags even when they're "lol same" or "yep." This is a feature of comment propagation — meaningful for theme prevalence, less meaningful for individual-comment construct claims. Don't claim per-comment precision is higher than it is.

### Borderline (open question)

- **Whether comment-level precision should match post-level.** Currently the publicly stated 80% gate is post-level. Comments are noisier (shorter, reactive, in-thread). Either (a) hold comments to the same gate and prune `therapeutic`, `emotional support`, `honeymoon`, `sex with`, `hours a day`, `screen time` from comment scanning, or (b) explicitly publish two precision figures: post-level (80%) and comment-level (60-75%). The status quo (gate applies but is unverified at the comment level) is the worst of both.

---

## Bottom line

The themes are not interchangeable in quality:

- **sex/ERP** is the strongest, in precision (88%) and construct, but the magnitude is 40% one event. Honest about Replika; misleading as a steady-state metric.
- **romance** is mid-quality (72%); two leaky keywords (`honeymoon`, `wedding`) and routine negation FPs. Fixable.
- **rupture** is 76% on comments but the theme is overwhelmingly two subreddits' product complaints. The construct is right; the corpus selection bias is not.
- **addiction** is 67%, dragged down by two duration-detector keywords. Restrict to T3 subs and it cleans up.
- **therapy** is 58% and not measuring what it claims to measure. The user's hypothesis is confirmed: a meaningful share of "therapy" volume is venting, sarcasm, feature-label language, and complaints about AI tone style.
- **consciousness** at the comment level is 51% — barely better than a coin flip. The post level is 80% per the robustness audit, so this is a comment-propagation problem specifically. The single most embarrassing data point on the site lives in this theme.

If a reviewer were given this report and the chart, they could not destroy the project — the construct schema is defensible, the cross-time shape signal is honest, and the precision-first methodology is documented. But they could:

1. Force you to retract or qualify "therapy" claims pending a `therapeutic` cut.
2. Force a "consciousness comment series" caveat or split, citing COMMENT 41.
3. Force a "40% one event" caveat on sex/ERP.
4. Force a per-theme sub-concentration disclosure.

None of these would invalidate the directional/qualitative purpose of the project. All of them should be addressed before the chart is used for anything more decisive than "look at the shape and timing of community attention."

---

## Source files

- 700 comments classified across 7 agent runs:
  - `analysis/keyword_pipeline/results/adv_tagged_comments_{theme}_2026-05-13.md` (per theme: rupture/addiction/romance/sexual_erp/consciousness/therapy)
  - `analysis/keyword_pipeline/results/adv_untagged_comments_recall_2026-05-13.md`
- Stats: `analysis/keyword_pipeline/results/adv_stats_2026-05-13.json`
- Builders: `analysis/keyword_pipeline/build_adversarial_samples.py`
- Companion reports today: `docs/robustness_audit_2026-05-13.md`, `docs/comprehensiveness_audit_2026-05-13.md`
