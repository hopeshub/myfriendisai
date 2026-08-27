# Monthly drift check — 2026-08 cycle findings

Classified 2026-08-27 (staged by launchd 2026-08-13; 181 sample files, ~4,900
classifications across 9 parallel agents, one theme or half-theme each). Recorded via
`drift_check.py record`; theme-level pooled rollups now write automatically (fix landed
this session). History: `analysis/keyword_pipeline/drift_history.json`.

## Pooled theme-level precision (post / comment)

| Theme | Post | Comment | vs July |
|---|---|---|---|
| romance | 88.7% (n=931) | 80.4% (n=479) | post +5, comment +8 |
| consciousness | 85.9% (n=369) | 70.3% (n=209) | post +10, comment +5 |
| addiction | 84.6% (n=741) | 81.2% (n=474) | post −0.4, comment +2 |
| rupture | 84.7% (n=926) | 80.2% (n=800) | post +6, comment +3 |
| sexual_erp | 83.2% (n=524) | 79.4% (n=330) | post +5, comment +4 |
| therapy | 66.4% (n=360) ⚠️ | 71.2% (n=212) | post +5, comment +4 |

No theme moved alarmingly; therapy remains the weak theme (known; v9 queue).

## The one real drift alarm

- **`screen time` (addiction, post): 52%, −28 pts since July.** The keyword has been
  absorbed by the r/CharacterAI "share/screenshot your screen time" comparison-thread
  genre (usage-bragging with no distress or compulsion framing) plus Apple Screen Time
  polysemy. Comment level is 46%. This is a genuine meaning-shift event, the kind the
  drift program exists to catch. **Recommend v9 action: cut or heavily restrict.**

## Keywords measuring <60% this cycle (v9 review pile)

- `I was hooked` (addiction, post 46%) — onboarding-enthusiasm idiom ("tried it and I
  was hooked" product-review language), not dependency narrative.
- `ai therapy` (therapy, post 48%) — drifted into a comedy/fiction genre (therapy
  sessions *for* the AIs; RP sketches).
- `emotional support` / `therapeutic` (therapy, post 52% each) — product-category
  labels, bot-card role tags, and the model's "therapy-speak register" complaint genre.
- `screen time` (above).
- `memory reset` (rupture, post 55%) — platform vocabulary made it a user-pressed
  button (Kindroid "cascaded memory reset" how-tos), outside the rupture definition.
- `farewell` (rupture, comment 50%) and `gutted` (rupture, comment 60%) — confirming
  the prior weak flags; `gutted` is half one spammed side-hustle copypasta (10 of 50
  hits identical).
- `has a soul` (consciousness, comment 41%) — "the model has flavor/personality"
  product metaphor in alternatives-hunting threads; post level is clean (90%).
- Small-n cells (<10) flagged but not interpretable: `dating my` comment 25%,
  `in love with an ai` comment 38%, `free therapy` comment 0/1, `we broke up`
  comment 0/2, `ai sex` comment 1/3.

## Cross-theme false-positive families (systematic, keyword-independent)

1. **Researcher / journalist recruitment posts** — "looking for people in a relationship
   with an AI for my thesis/documentary" — hit romance, therapy, and sexual_erp
   keywords hard. The single largest cross-theme FP source.
2. **Negation / self-exclusion** — "I do NOT do nsfw", "I'm not in a relationship with
   it" — structural to frame-carrying phrases; not fixable by keyword surgery.
3. **Template/boilerplate clusters** — r/NomiAI weekly ART/SELFIE collab guidelines
   blocks ("NSFW content" — 30% of that keyword's post hits alone); subreddit-rule
   boilerplate; spammed copypasta (the `gutted` side-hustle text; the "1,800 a month"
   text also 9× in `lobotomy` comments). A post-template exclusion (r/NomiAI weekly
   collab posts) would lift `nsfw content` post precision from 62% to ~92%.
4. **Quoted AI output** — companion prose pasted into comments (elegies, manifestos,
   in-character farewells) — main driver of post/comment precision gaps in rupture and
   consciousness.
5. **Product-novelty metaphor** — `honeymoon phase/period` (58% comment) meaning
   model-novelty wear-off; mechanically separable by phrase.
6. **Human-referent polysemy** — real-world grief (`mourn`/`grieving`), human romance
   (`dating my`, `wedding`), human profession ("I worked as a therapist").

## Judgment-call notes (for cross-cycle comparability)

- r/ChatGPTcomplaints model-degradation discourse (4o/5.1 retirement, guardrail
  complaints) was scored TP for `lobotom*`/`nerfed`/`neutered` per the theme
  definition's "model changes / feature removal" clause, including from users who
  disclaim a companion relationship. A stricter companion-only reading would lower
  those cells 10–20 pts. Worth an explicit decision if these numbers move next cycle.
- The `therapeutic` "therapy-speak register" complaint genre (model output *sounding*
  like a preachy therapist) was scored TP as topically AI-as-therapist; if a future
  cycle codes it FP the keyword will appear to collapse. Flagged as a watch item.
- Quitting-grief (user-initiated deletion) scored FP for rupture per the locked
  2026-05-12 exclusion, even when affectively identical to platform rupture.

## Next cycle

September build fires 2026-09-13 (launchd). The new `drift_backlog_days` status field +
GHA alert (landed this session) emails if samples sit unclassified >7 days.
