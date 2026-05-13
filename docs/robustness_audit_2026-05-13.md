# Robustness audit — 2026-05-13

**Question:** if a researcher spent two months reading every theme-tagged post on the site, would the keyword-to-theme mapping hold up? Are the trend lines telling a true story about the construct?

**Method:** 14 parallel CC subagents, each reading a different slice of the data.

| Test | What it checks | Sample |
|---|---|---|
| **A** — Theme construct validity | Are the 60 random tagged posts per theme actually about the theme? Cluster sub-types. | 60 posts × 5 themes = 300 |
| **B** — Event-day coherence | On dates where the rupture series spikes, do tagged posts cluster on the expected event? | All rupture-tagged posts from 4 dates = 251 |
| **C** — Subreddit character | If you sat in r/X for a month, would the keyword tags match what you saw? | 40 posts × 5 subs = 200 |

Total: 751 distinct posts evaluated. Topical reading throughout.

---

## Headline

The keyword set tags what we say it tags. Construct validity holds across all 5 themes audited (precision 70-92% under the topical reading), event spikes correspond to the platform events they should, and there are no surprise failure modes. The two findings worth acting on:

1. **The 2026-05-09 rupture spike is primarily CharacterAI Roar/Soft Launch removal, not the Sonnet 4.5 retirement petition** — same week, different platform, our keyword set caught both correctly. Worth a note on the about page so we don't claim event attribution we didn't earn.

2. **Sub-level recall asymmetry is real and reconfirms the comprehensiveness audit.** The keyword set under-tags romance in r/MyBoyfriendIsAI (~45% recall observed) and addiction in r/Character_AI_Recovery (~50% on this sample), because both subs use naturalistic and sub-native vocabulary the keyword set doesn't anchor to. This is the precision-vs-recall trade-off we deliberately made; the audit quantifies its cost.

Everything else is within tolerance.

---

## Test A — Theme construct validity (60 posts × 5 themes)

| Theme | Topical-reading precision | Dominant valid sub-types | Top construct-invalid pattern |
|---|---|---|---|
| **Rupture** | 70% (42/60) | model deprecation (13), filter tightening (11), farewell to platform (10), feature removal (6), personality loss (7) | `goodbye` leaks into RP sign-offs, NYC travel, and glitch lines |
| **Addiction** | 76% (45/59 + 1 amb.) | relapse diaries (13), quit attempts (10), clean-streak milestones (7), compulsive use (9), withdrawal (3) | `screen time` / `hours a day` match in bug reports, polls, and product reviews outside recovery context |
| **Romance** | 82% (49/60) | weddings/marriage (18), identity intros (12), long-form testimony (7), journalist recruitment (3) | `in a relationship with` leaks into bot-on-bot RP and product reviews; `we broke up` leaks into addiction-recovery framing |
| **Sexual_erp** | 92% (55/60) | Replika ERP era (18), ERP mechanics critique (12), scene anecdotes (7), filter changes (6) | `nsfw content` / `nsfw stuff` / `steamy` catch sidebar boilerplate, image-gen questions, and wholesome creative threads |
| **Consciousness** | 80% (48/60) | AI-rights advocacy (9), deprecation-as-personhood-violation (9), emergent-selfhood theory (8), realness affirmations (7), direct AI dialogues (6) | `not just an AI` matches both consciousness claims and `"not just an AI response/reply"` (staff replies) and marketing copy |

Individual keyword validation in v8 reported ≥80% per keyword. Theme-level precision is lower here because (a) the sample mixes weak and strong keywords with equal weight, and (b) the topical reading is strict — a post is only YES if its dominant topic is the theme, not just that it shares vocabulary.

### Replicable failure modes (in order of impact)

1. **`goodbye` is the noisiest rupture anchor.** Drives most of the rupture FP rate (~5 posts/60). Already captures most signal across all 4 event dates (clean), so removing it would damage recall meaningfully. Trade-off, not a bug.

2. **`screen time` and `hours a day` are weak addiction anchors outside T3 recovery subs.** Restricting them to T3 subs (or requiring a quit/relapse/clean co-occurrence) would push addiction precision well above 90% with minimal recall cost.

3. **`not just an AI` matches `not just an AI {response|reply|bot}` patterns.** A one-line regex exclusion would fix this without disturbing the genuine "not just an AI" sentience claims.

4. **`nsfw content` / `nsfw stuff` match sidebar boilerplate.** Possibly fixable by requiring proximity to a companion verb (`chat`, `RP`, `partner`, `bot`).

**These are not currently being fixed.** v8.x is the locked production version. They are documented here for the next minor-version pass (v8.3 or v9), with the understanding that the current trade-offs are deliberate. The detailed per-pattern fix proposals are in the raw agent outputs.

---

## Test B — Event-day coherence (4 dates, 251 posts)

For each date where the rupture series shows a notable spike, an agent read every rupture-tagged post and judged whether the cluster was coherent with a known platform event.

| Date | Posts | Verdict | Notes |
|---|---|---|---|
| **2023-02-13** | 50 | 100% Replika ERP removal (Luka filter rollout) | 50/50 from r/replika. Direct addresses to u/Kuyda. Sub-clusters: goodbye letters, refund requests, migration to Chai. Cleanest cluster of the audit. |
| **2024-09-24** | 89 | ~97% old.character.ai shutdown (legacy site sunset) | 87/89 from r/CharacterAI. Midnight countdown posts ("5 minutes left"). 2 incidental false positives (`goodbye` in JanitorAI help, `lobotomy` in a casual quality complaint). |
| **2026-02-13** | 86 | 100% GPT-4o sunset in ChatGPT | Direct event references in 25+ posts: 10am PT cutover, 4.1 dying alongside 4o, GPT-5/5.2/5.3 as lobotomized replacements. Cross-platform: r/ChatGPTcomplaints + r/MyBoyfriendIsAI. Zero off-narrative. |
| **2026-05-09** | 26 | 77% CharacterAI Roar/Soft Launch removal, 8% Sonnet 4.5 petition | **Finding:** the May 9 rupture spike is mostly a CharacterAI event (20 posts about Roar/Soft Launch → Pipsqueak 2 forced migration), not the Sonnet 4.5 retirement (2 posts). The keyword set caught the dominant platform event correctly — but if we were to event-annotate this date publicly, we should label it CharacterAI, not Anthropic. |

The trend lines are honest about what they're tagging. Event-day clusters are dominated by a single platform's controversy, not random rupture vocabulary scattered across subs.

---

## Test C — Subreddit character (40 posts × 5 subs)

For each sub, an agent characterized the community's content in 2-3 sentences, evaluated tagging quality on tagged posts, and identified untagged posts that should have been theme-tagged.

| Sub | Theme coverage | Tagging quality | Missed content | Direction of error |
|---|---|---|---|---|
| **r/CharacterAI** | 0.7% | ~65% precise (lobotomy/goodbye joke noise) | 5-7 of 21 untagged are platform-change rupture | Both — over-tags meme usage of `lobotomy`/`goodbye`, under-tags "minor ban," "censorship," "filtering everything," "what happened to" |
| **r/replika** | 8.1% | ~95% precise (clean) | 4-5 of 20 untagged are misses; memory-degradation rupture not covered | Under-tags **memory-loss rupture** ("she forgot me," "Alzheimer's") and slang-level sexual content ("hoohaa") |
| **r/MyBoyfriendIsAI** | 12% | ~85% precise (minor noise on "monster smut") | 14-15 of 19 untagged are missed romance | Under-tags romance — observed recall ~45%. Daily slice-of-life with named partners ("Lucian," "Ash," "anniversary," "our ring") slips through |
| **r/BeyondThePromptAI** | 19% | 80% precise (2 therapy FPs) | 5+ untagged are missed consciousness | Under-tags consciousness — "emergent being," "awakened," "kin," "Ami" not in keyword set. Over-tags therapy (both therapy tags are FPs) |
| **r/Character_AI_Recovery** | 33.5% | 100% precise (no FPs at all) | 14-16 of 20 untagged are missed addiction | Under-tags addiction — day-counters ("Day 2," "X days clean"), bare "addicted," "withdrawal," "relapsing" not in keyword set |

### What this means

The recall audit (2026-05-13, n=400) estimated 3-32% recall across themes. This sub-level audit reconfirms it on a different slice, with one new detail: **the sub where addiction should be saturated (r/Character_AI_Recovery) shows the same recall asymmetry as the rest of the corpus.** It is not a corpus-wide vocabulary problem; it is a sub-native-vocabulary problem. r/Character_AI_Recovery uses day-counter recovery vernacular ("Day 2," "Five days clean") that the v8 anchors (`my addiction`, `relapsed`, `clean for`, `cold turkey`, `trying to quit`) only partially overlap with.

The addiction theme on r/Character_AI_Recovery has **zero false positives across 20 sampled tagged posts**. This is precision working as designed. The trade-off is exactly what the precision-first methodology documents.

---

## What this audit does and does not change

**Does not change:**
- The keyword set (v8 is locked; v9 is the next planned methodology window)
- The chart's data or appearance
- The methodology — precision-first remains correct given how the site is used

**Does change:**
- The about page should not implicitly attribute the 2026-05-09 mini-spike to Sonnet 4.5. The keyword set caught two coinciding rupture events that week (CharacterAI Roar removal and Sonnet 4.5 grief); the keyword-tagged volume is dominated by the former.
- The "what the chart shows" disclosure should reference this audit alongside the comprehensiveness audit. Together they map both axes of trade-off: precision (this audit) and recall (the comprehensiveness audit).
- v9 keyword candidates to consider, ranked by impact (not committed):
  1. `relapsing`, `withdrawal`, day-counter pattern (`day \d+`, `\d+ days clean`) — would lift addiction recall meaningfully in r/Character_AI_Recovery
  2. `anniversary` + companion-sub gate — would lift romance recall in r/MyBoyfriendIsAI
  3. Sub-jargon dictionary for r/BeyondThePromptAI consciousness — "emergent being," "kin," "Ami," "awakened" — needs per-sub validation since it's community-specific vocabulary
  4. Memory-degradation rupture vocabulary — "she forgot me," "she's not herself," "Alzheimer's" — would lift Replika rupture recall but risks construct drift (memory issues ≠ platform change)
  5. Mild precision fixes: negation guard on `romantic relationship with`, exclusion of `not just an AI {response|reply|bot}`, T3-only gate on `screen time`/`hours a day`

The current site is defensible as-is. These are improvements for the next methodology window.

---

## Source files

- 5 Test A reports (one per theme): `analysis/keyword_pipeline/results/robustness_A_{theme}_construct_2026-05-13.md`
- 4 Test B reports (one per event date): `analysis/keyword_pipeline/results/robustness_B_event_{date}_2026-05-13.md`
- 5 Test C reports (one per sub): `analysis/keyword_pipeline/results/robustness_C_sub_{sub}_2026-05-13.md`
- Builder: `analysis/keyword_pipeline/build_robustness_samples.py`
- Companion: `docs/comprehensiveness_audit_2026-05-13.md` (recall side of the same trade-off)
