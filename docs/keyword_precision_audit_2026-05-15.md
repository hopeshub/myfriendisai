# Keyword precision audit — 2026-05-15

A one-time audit of the production keyword set, using the ~14,800 Claude
Sonnet 4.6 verdicts already collected before the full-corpus backfill was
abandoned. Purpose: check whether any production keyword is measuring noise
rather than its theme — i.e. whether anything needs cutting.

This audit replaces the abandoned plan to backfill LLM verification to 100%
coverage and flip the chart to `count_llm_verified`. See the strategic
reasoning in `docs/llm_integration_strategy_2026-05-15.md`.

## Method and its limit

For each keyword × theme × surface (post/comment) with ≥10 Sonnet verdicts,
precision is taken as `TP / (TP + FP)` over the existing verdicts.

**Hard caveat — these are not calibrated precision figures.** The verdicts
come from the lenient "default-TP under topical reading" prompt (the v2
prompt adopted after v1 over-rejected at 61.5% agreement). Overall the
verdicts run 96% TP / 4% FP — far above the project's manual-validation
numbers. The lenient prompt is rubber-stamping to a degree. So:

- **Absolute precision from these verdicts is an upper bound, not the truth.**
- **Relative ranking is still usable** — a keyword that scores low *against
  a 96% baseline* is genuinely the most suspect, even if "96%" itself is inflated.

This is the same logic the drift check runs on: relative agreement, not
absolute calibration.

## Per-theme verdict precision (Sonnet, lenient prompt — upper bound)

| Theme | Post TP/n | Comment TP/n |
|---|---|---|
| addiction | 97.0% (3027/3120) | 94.7% (195/206) |
| consciousness | 96.8% (481/497) | 93.9% (46/49) |
| romance | 93.6% (2380/2542) | 87.9% (102/116) |
| rupture | 95.1% (678/713) | 100% (98/98) |
| sexual_erp | 97.3% (5635/5793) | 93.6% (88/94) |
| therapy | 93.4% (1338/1432) | 97.0% (130/134) |

## Lowest-scoring keyword cells (n ≥ 10)

| Keyword | Theme | Surface | TP/n | % |
|---|---|---|---|---|
| honeymoon | romance | comment | 7/13 | 54% |
| we broke up | romance | post | 16/24 | 67% |
| not just an ai | consciousness | post | 13/18 | 72% |
| hours a day | addiction | comment | 33/41 | 80% |
| personality changed | rupture | post | 20/25 | 80% |
| in a relationship with | romance | comment | 13/16 | 81% |
| romantic relationship with | romance | post | 95/113 | 84% |

Every other keyword cell (92 more, n ≥ 10) scored ≥ 85%. 41 keyword cells
have < 10 verdicts and are not auditable from the current verdict set;
their admission-time manual validation stands.

## Findings

1. **No production keyword is measuring noise.** Even read as relative
   ranking against an inflated baseline, the worst cells are not garbage
   keywords — they are borderline keywords, and all three sub-85% post/comment
   cells are *already documented*: `we broke up` and `hours a day` are
   researcher-accepted (logged in `config/keywords_v8.yaml`); `honeymoon` is an
   already-flagged noisy comment keyword; `not just an ai` is a low-volume
   consciousness keyword. There is nothing here that admission validation
   and the existing noisy-keyword flag did not already catch.

2. **The LLM verdicts cannot certify a precision number.** They say ~95%;
   the 2026-05-13 adversarial audit said 51–72% comment precision under a
   strict human-style topical reading. Both cannot be right. The lenient
   prompt is the likely cause. What the verdicts *can* honestly support is
   the negative result in finding 1: no keyword is outright broken.

3. **The keyword set does not need surgery.** No cuts. No promotions. v8
   stays as is.

## Decision

- **No keyword changes.** The audit's job was to find keywords measuring
  noise; it found none. v8 keyword set unchanged.
- **LLM verification is not a precision oracle for this project.** It is
  retained only as (a) this one-time garbage-detector audit and (b) the
  ongoing sample-based drift check. It is not a production filter.
- **`count` (raw regex) remains the sole production chart series.** The
  `count_llm_verified` series is not promoted and should not be surfaced as
  a primary precision claim.
- **Open follow-up:** `theme_health.json` still exports `llm_stats.precision`
  (~95%, the inflated number). The public Theme Health snapshot should not
  present that as a precision figure. Resolve before launch — either drop
  `llm_stats` from the surface or label it explicitly as lenient-prompt
  verdict share, not precision.
