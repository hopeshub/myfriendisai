# Monthly drift check — 2026-10 cycle findings

Classified and recorded 2026-10-24. The launchd build staged the samples on
2026-10-13. They sat unclassified for 11 days, which tripped the GitHub
drift-backlog alert. The cycle covers 184 sample files and about 5,000
classifications by 13 blind parallel raters. Results are in
`analysis/keyword_pipeline/results/drift_2026-10_*_results.txt`, and the
recorded history is in `analysis/keyword_pipeline/drift_history.json`.

## What changed in the instrument first

The September cycle was held back because its raters applied edge-case rules
differently from August's (`docs/drift_2026-09_findings.md`). Before
classifying October:

1. **Written conventions.** `analysis/keyword_pipeline/drift_rater_conventions.md`
   settles the four open questions from September: companion-voiced text,
   user-initiated leaving, non-companion model complaints, and ironic cures.
   It also covers non-discourse text (recruitment, spam, app plugs, mod
   boilerplate), empty bodies, and doubt. The calls follow the locked topical
   reading and `theme_definitions.yaml`. Where the definitions already decided
   a case, the conventions follow them, not either cycle's habit. For example,
   user-initiated leaving is FP for rupture per the 2026-05-12 exclusion.
2. **Self-contained headers.** `scripts/drift_check.py build` now prints the
   theme's definition, its exclusions and the conventions into every sample
   file. Before, it printed a generic "FP rules (strict)" list that contradicted
   the topical reading's "when in doubt, YES". The unclassified October files
   were re-built with the new header. The originals were discarded; they were
   regenerable and had never been rated.

## Calibration: the conventions reproduce August

A separate blind rater re-scored the August and September versions of eight
keywords where September had swung, applying only the written conventions.
The table shows post-level precision except for `lobotomy`, which is the
comment file:

| Keyword | Aug as recorded | Aug, conventions | Sep as classified | Sep, conventions |
|---|---|---|---|---|
| `farewell` | 92% | 84% | 52% | 64% |
| `we broke up` | 89% | 77% | 53% | 78% |
| `husbando` | 86% | 88% | 52% | 88% |
| `tulpa` | 79% | 86% | 43% | 86% |
| `lobotomy` (comment) | 94% | 80% | 70% | 86% |
| `goodbye` | 76% | 72% | 56% | 66% |
| `in a relationship with` | 68% | 68% | 50% | 70% |

Under the conventions both months land on August's level, and September's
collapse disappears. That confirms September was rater drift.

The two places the conventions run below August are both deliberate:
- **Spam copypasta.** The "$1,800 a month side hustle" text appears 10 times in
  August's `lobotomy` comment sample, and August counted it TP.
- **User-initiated farewells.** `theme_definitions.yaml` has excluded these
  since 2026-05-12.

**Therapy is the exception.** A second blind re-rating of six August therapy
files landed about halfway between August and October:

| Keyword (post) | August | October | Calibration |
|---|---|---|---|
| `emotional support` | 52% | 80% | 70% |
| `therapeutic` | 52% | 76% | 64% |

So October's therapy figures run roughly five to ten points generous. The
calibration rater traced most of the spread to two edge cases:
- the matched keyword falling outside the 500-character excerpt;
- complaints about a model's "therapy voice".

Both are fixed for November (see below). The chip outcomes do not depend on
which rater is right. Under calibration, `emotional support` and `therapeutic`
clear 60% and `ai therapy` (58%) does not.

The September cycle stays unrecorded. October measures nearly the same
population, because samples draw at random from each keyword's whole history,
so a re-scored September would add a second near-duplicate point and no new
information.

## Results

Pooled precision by theme:

| Theme | Post Oct | Post Aug | Comment Oct | Comment Aug |
|---|---|---|---|---|
| addiction | 88.0% (n=758) | 84.6% | 86.5% (n=525) | 81.2% |
| romance | 88.7% (n=942) | 88.7% | 83.7% (n=612) | 80.4% |
| consciousness | 87.9% (n=373) | 85.9% | 82.2% (n=269) | 70.3% |
| sexual_erp | 88.3% (n=513) | 83.2% | 79.2% (n=366) | 79.4% |
| rupture | 81.5% (n=921) | 84.7% | 80.9% (n=858) | 80.2% |
| therapy | 80.9% (n=362)* | 66.4% | 66.5% (n=230) | 71.2% |

\* Roughly five to ten points generous; see the therapy calibration above.

**Below the 60% cut at post level.** These get the `drifting` chip on the next
export:

| Keyword | Theme | Oct (n) | Aug |
|---|---|---|---|
| `memory reset` | rupture | 50% (8) | 55% |
| `ai therapy` | therapy | 51% (35) | 48% |
| `not just an ai` | consciousness | 53% (19) | 61% |
| `memory wiped` | rupture | 55% (11) | 83% |
| `lobotomies` | rupture | 59% (22) | 68% |

All five are low-volume. Each sample is nearly the keyword's entire match
history, so cycles re-rate the same posts, and a couple of calls move the
figure by ten points. Treat `memory wiped` (n=11) and `lobotomies` (n=22) as
borderline, not as demonstrated meaning shifts.

**Cleared since August.** `screen time` (68%), `I was hooked` (60%),
`emotional support` (80%) and `therapeutic` (76%). `I was hooked` is still
weak: its false positives are enthusiasm ("after 3 days I was hooked").

**Weak at comment level only** (v9 pile; the published line is post-only):
- `as a therapist` 48%
- `honeymoon` 52%, mostly "honeymoon phase" for a new model
- `therapeutic` 54%, the 5.x safety-voice complaints
- `romantic relationship with` 56%, from disclaimers and thesis recruitment
- `saying goodbye` 62%

## New content in the corpus

**Character.AI's reported Chapter 11 filing.** r/CharacterAI has discussed it
heavily since 2026-10-13 ("Character AI has filed for bankruptcy"). The
project has not independently confirmed the filing. This is the month's real
event in the discourse. It produces fresh rupture true positives: `taken away`, `mourn`,
`mourning`, `saying goodbye`, plus early goodbyes. It also coincides with
r/CharacterAI volume spikes on Oct 13–14. Other live rupture sources:
- the GPT-5.5 sunset and the Sonnet 4.5 / Opus 4.5 retirements;
- the Paradot and Mate.ai shutdowns;
- the "Pipsqueak 2" model change.

**An app-promotion wave in r/CharacterAIrunaways.** It is driven by the C.AI
news. Developers plug their own apps, and some accounts pose as users; riako.ai
posted 5 near-identical comments. It pulls the `nsfw chat`, `nsfw content` and
`nsfw stuff` comment files down to 63–72%.

**Templates and boilerplate:**
- r/MyBoyfriendIsAI's "Weekly Image Thread" contains "a steamy scene". It is 4
  of `steamy` post's 8 FPs and is a v9 template-guard candidate, like the
  r/NomiAI case.
- r/MyGirlfriendIsAI's weekly researcher-request thread.
- The Signal Front recruitment post appears 7 times in `personhood` post.

**Wrong-sense spam.** `erps` matched an "Enterprise Resource Planning"
listicle.

## Changes for the November cycle

Two changes were made on 2026-10-24, after this cycle was classified:

1. **Keyword-anchored excerpts.** When a long body's first keyword match falls
   past the 500-character head, the sample shows the opening, `[...]`, and the
   passage around the match. Nearly every rater named the hidden keyword as
   their most common forced guess.
2. **Conventions 8–12.** These cover outsiders, product senses (including the
   therapy-voice split), declining, repeated text, and usage figures. Each
   writes down the call most October raters reported making, so November
   stays consistent with October.
