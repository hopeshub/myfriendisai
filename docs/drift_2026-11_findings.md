# Monthly drift check — 2026-11 cycle findings

Classified 2026-11-20, in the November refresh session. Recorded into `analysis/keyword_pipeline/drift_history.json` on the `methods/record-drift-2026-11` branch, with the schema note recommended below. Merging that branch publishes the result: the next collection's `export_keyword_details.py` run updates the `drifting` chips. The launchd build staged the samples on 2026-11-13. The cycle covers 184 sample files and 6,811 classifications by 26 blind parallel raters, each given only the sample files and a brief telling them to apply the header exactly. Results are in `analysis/keyword_pipeline/results/drift_2026-11_*_results.txt`. Every file was checked so that its line count equals its entry count.

## The headline: every theme is lower, and that is the rubric, not the corpus

Every theme's pooled precision came in below October's, at both levels, by 2 to 13 points. A uniform drop across all six themes is the September signature, so before recording anything I tested whether it was real.

It can't be the corpus. Samples draw at random from each keyword's whole history (`cmd_build`: `ORDER BY RANDOM()` over all matching posts), and 63% of November's entries date from 2026, so the population moved by one month of new posts out of several years. Three things did change between the cycles:

- the raters (a fresh pool);
- the rubric (conventions 8–12 and the sharpened doubt rule in convention 7, added 2026-10-24);
- the display (keyword-anchored excerpts, also 2026-10-24).

**Calibration.** I re-rated 28 of October's own sample files (1,350 entries: two random files per theme and level with n ≥ 40, plus the four biggest movers) twice, blind, with raters who never saw October's labels:

- **R1**: October's files exactly as October's raters saw them (conventions 1–7, old excerpts).
- **R2**: the same October entries under November's header (conventions 1–12).

| Same 28 October files | Pooled precision |
|---|---|
| October, as recorded | 80.7% |
| R1: new raters, October's rubric | 78.4% |
| R2: new raters, November's rubric | 72.7% |
| November cycle, same 28 keywords, November's samples | 71.6% |

Item-level agreement was 93.0% between October and R1, and 92.8% between R1 and R2. That is the noise floor for two blind raters on this task.

So, of the roughly nine points between October and November on these keywords:

- about **two points** are raters: under an identical rubric, the new pool is slightly stricter;
- about **six points** are conventions 8–12;
- **one point or less** is left for sampling and the new excerpts.

R2, which is October's entries under November's rubric, lands on November's figure. The corpus didn't move; the instrument did.

Where the rubric step concentrates (R1 → R2, pooled over the calibration files):

| Theme × level | R1 | R2 | Conventions doing the work |
|---|---|---|---|
| therapy comment | 87% | 68% | 8 (outsiders), 9 (therapy-voice product sense), 10 (declining) |
| sexual_erp comment | 69% | 57% | 8, 10 ("I don't do NSFW") |
| therapy post | 73% | 65% | 9, 10 |
| consciousness comment | 77% | 68% | 9 ("this model has a soul") |
| addiction post | 88% | 82% | 12 (neutral screen-time figures) |
| romance, rupture, addiction comment | — | within ±4 pts | small |

The 2026-10-24 notes describe conventions 8–12 as writing down "the call most October raters reported making, so November stays consistent with October". The calibration says they did more than that. Written down, the calls are applied every time, not mostly, and they all point toward FP. That is a defensible reading of the topical definition: an outsider with no stake, a product described as having "a soul", and a flat "not for me" are not theme discourse. But it is a step change, and it has to be recorded as one.

The October raters were also generous on a few keywords under their own rubric. R1, on October's own entries, gives `we broke up` (post) 56% against October's 84%: most of the misses are breakups with human partners in addiction stories. It gives `taken away` (post) 72% against 86%, and `nsfw stuff` (post) 76% against 88%. That fits the earlier note that October's therapy figures ran generous.

## Recording

The branch **records November as it stands and marks the break.**
- `record` was run on the 184 files, then `report`. Its theme figures match the results table below.
- One line was added to `schema_notes` in `drift_history.json`: "2026-11 is the first cycle under rater conventions 1–12 and keyword-anchored excerpts (2026-10-24). A blind calibration on October's samples puts the rubric step at about −6 points pooled, concentrated in therapy and sex/ERP comments (`docs/drift_2026-11_findings.md`). Read 2026-11 onward against 2026-11, not against earlier cycles."
- Compare December onward against November.

The alternative is to treat conventions 8–12 as too strict and loosen them. I'd advise against that. They're the right reading, and loosening them to restore October's numbers would be fitting the rubric to a result.

**What recording changes on the site.** The `drifting` chip shows when a keyword's latest post-level re-check is below 60%. Today five keywords carry it. After recording, ten will. None of the current five clears, and five join:

| Keyword | Theme | Nov (n) | Oct | Why |
|---|---|---|---|---|
| `as a therapist` | therapy | 54% (50) | 82% | Rubric. R1 82 → R2 62 on October's own entries: the 5.x "acts like a therapist" voice (conv. 9), roleplay roles and human therapists |
| `we broke up` | romance | 56% (32) | 84% | October was generous: R1 gives 56% on October's own entries. Mostly human-partner breakups |
| `I was hooked` | addiction | 52% (50) | 60% | Enthusiasm sense ("I tried it and I was hooked"); was borderline in October |
| `goodbye` | rupture | 52% (50) | 66% | Convention 2: leaving for your own reasons; also fiction and real-world grief |
| `tulpa` | consciousness | 59% (29) | 79% | Human in-head sense, mostly in r/Character_AI_Recovery; one author writes a third of the posts |
| `ai therapy` *(already chipped)* | therapy | 46% (35) | 51% | Research citations, recruitment, news headlines |
| `not just an ai` *(already)* | consciousness | 47% (19) | 53% | Product marketing and spam |
| `memory reset` *(already)* | rupture | 50% (8) | 50% | Kindroid's user-triggered "cascaded memory reset" |
| `memory wiped` *(already)* | rupture | 55% (11) | 55% | — |
| `lobotomies` *(already)* | rupture | 59% (22) | 59% | Real lobotomies, roleplay jokes |

Ten chips across 92 keywords is honest under the current rubric. Two cautions:
- `memory reset` (n=8) and `memory wiped` (n=11) are chipped on a handful of posts. The open question of a minimum n (CLAUDE.md item 17c) applies here.
- A chip is a disclosure, not a cut. Standing policy keeps a drifted keyword counting until the v9 bump.

## Results

Pooled precision by theme. The Aug and Oct columns used the older rubric, so read the step above before comparing across it.

| Theme | Post Nov | Post Oct | Post Aug | Comment Nov | Comment Oct | Comment Aug |
|---|---|---|---|---|---|---|
| addiction | 84.7% (n=760) | 88.0% | 84.6% | 81.3% (n=534) | 86.5% | 81.2% |
| romance | 86.5% (n=943) | 88.7% | 88.7% | 77.0% (n=636) | 83.7% | 80.4% |
| consciousness | 75.9% (n=374) | 87.9% | 85.9% | 71.5% (n=274) | 82.2% | 70.3% |
| sexual_erp | 79.1% (n=513) | 88.3% | 83.2% | 69.8% (n=378) | 79.2% | 79.4% |
| rupture | 74.3% (n=922) | 81.5% | 84.7% | 75.4% (n=873) | 80.9% | 80.2% |
| therapy | 67.9% (n=361) | 80.9% | 66.4% | 57.6% (n=243) | 66.5% | 71.2% |

These are rater precision on random matches, not the May census precision quoted in METHODOLOGY §4.4. That census used a different method and stays as it is.

**Weak at comment level** (v9 pile; the published line is post-only), n ≥ 15:
- `husbando` 21% (one copy-pasted industry essay is 5 of 19)
- `has a soul` 30% (product sense)
- `as a therapist` 32%
- `tulpa` 42%
- `lewd` 47% (negation, porn spam)
- `finally deleted` 48% (quitting over the product)
- `hours a day` 48% (neutral usage figures, conv. 12)
- `honeymoon` 48% ("honeymoon phase")
- `sex with` 48% (human referents)
- `romantic relationship with` 50% (disclaimers, recruitment)
- `therapeutic` 50% (safety-voice complaints)
- `for therapy` 55%, `nsfw content` 56%, `farewell` 56%, `saying goodbye` 59%

## New content in the corpus

**Character.AI's bankruptcy** is producing rupture true positives: `saying goodbye`, `taken away` and `farewell`, clustered from mid-October. The other sources are the 4o, Sonnet 4.5 and Opus 4 retirements.

**App promotion has spread beyond r/CharacterAIrunaways.** Developers replying to "any alternatives?" threads with their own apps are now in most NSFW comment files: CharaVerse, Lucidbook, PlumHour, HereHaven, Immersey, LoreMate, Oudream and others. Two accounts look like astroturf rather than open developer posts:
- **DarLink AI**: plugs with the same selling points ("so addictive", "fully uncensored", "insane rp + memory") turned up in at least six different keyword files, in r/aipartners, r/SoulmateAI and r/AICompanions among others.
- **riako.ai**: same-day near-identical comments in different threads (also seen in October).

These are mostly comments, so they don't touch the published post-only line. They belong with the seeding-ring check (handoff D13).

**Templates and boilerplate in posts, which do touch the published line:**
- r/MyBoyfriendIsAI's "Weekly Image Thread" still contains "a steamy scene": 5 of `steamy` post's 50. It is flagged for the second month running. This is the r/NomiAI case again, only smaller. Find the posting account and add it to `EXCLUDED_AUTHORS`, or guard the template at v9. A before/after per theme is needed, because this changes the denominator.
- The Signal Front AI-personhood recruitment post appears 5 times in November's `personhood` post sample (6–7 in October's), each copy with a different Discord link. Raters split on it (see below).
- r/MyGirlfriendIsAI's weekly researcher-request thread.

**Spam.** The "$1,800 a month side hustle" copypasta appears 12 times across the `gutted` and `lobotomy` comment files. It is all in r/ChatGPTcomplaints on 22–23 June 2026, and all FP. There is also porn spam in r/NomiAI and r/Paradot (`lewd`), and an escort-style ad in r/SoulmateAI.

**Machine text.** A `farewell` comment in r/replika is leaked LLM-agent output ("SKIP: this is a goodbye/leaving post, and the prompt's own rule says…"). Raters also flagged LLM-voiced comments in r/CharacterAI threads, and companion-app developers posting philosophy-of-memory essays (Throughline, Vesper). This connects to the handoff's note that AI-written text is entering the rooms.

## Edges the raters split on (candidate convention 13)

These came up repeatedly and weren't decided the same way across raters. Each is worth a ruling before December:
1. **Advocacy recruitment with a stake** (the Signal Front post). It is on-theme argument, but it is also templated recruitment. The November rater called it FP; both calibration raters called it TP. It moves `personhood` post by about 10 points.
2. **Community-written satire** ("AI Marriage Guidelines"). One rater called four copies TP, another called one copy FP.
3. **Long sceptic arguments posted inside companion subs.** These sit between convention 8 (outsider, FP) and convention 10 (engages at length, TP). Most raters called them TP when the argument engaged the question and FP for one-line dismissals.
4. **Members promoting their own tool or app** (a free script, a self-hosted setup, a podcast) versus a "try X" plug. Raters called these TP when the post carried the member's own stake.
5. **Under rupture: a bot deleted by its creator**, not by the platform. One rater called it FP under convention 2.

## Calibration files

The R1 and R2 labels, the October labels for the same 28 files and the per-file table are in `docs/refresh_2026-11/_work/drift_calibration/` on the collection host. That folder is local and not in the repo.
