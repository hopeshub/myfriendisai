# Precision Audit — 2026-04-20

Spot-check validation of keyword precision at the post and comment level,
five weeks after the v8 keyword lockfile and the comment system launch
(2026-03-18). Methodology follows the March 2026 validation protocol:
sample random matches, classify YES / NO / AMBIGUOUS, compute
`precision = YES / (YES + NO) × 100`.

Sample size is 10 per theme per source (60 posts + 60 comments). This is
a precision *smoke test*, not a formal re-validation; numbers are
directional, not authoritative. A finding worse than baseline warrants a
proper 100-sample follow-up before acting.

## Post-level precision (last 30 days)

| Theme | YES | NO | AMBIG | Precision | Baseline | Verdict |
|-------|-----|----|----- |----------|----------|---------|
| rupture       | 10 | 0 | 0 | 100% | ~85% | healthy |
| addiction     | 8  | 0 | 2 | 100% | ~90% | healthy |
| therapy       | 6  | 0 | 4 | 100% | ~92% | healthy |
| sexual_erp    | 7  | 0 | 3 | 100% | ~95% | healthy |
| consciousness | 7  | 2 | 1 | 78%  | ~80% | borderline |
| romance       | 4  | 4 | 2 | 50%  | ~93% | **drift — investigate** |

Romance FPs clustered around posts that borrow companionship vocabulary
for policy / tech / platform discussions: "our wedding" in a Chai
outage post, "my ai partner" in a 4o-retention campaign post, "in a
relationship with" in a subscription-refund thread. The keywords aren't
wrong; the discourse around AI companionship has broadened enough that
the phrases now appear in meta-discussion as well as first-person
relationship posts. Worth a proper 100-sample re-validation before
editing the keyword list.

## Comment-level precision (first validation since 2026-03-18 launch)

| Theme | Precision | Post baseline | Drift |
|-------|-----------|---------------|-------|
| sexual_erp    | 90% | ~95% | -5 pp |
| addiction     | 80% | ~90% | -10 pp |
| romance       | 70% | ~93% | -23 pp |
| rupture       | 70% | ~85% | -15 pp |
| therapy       | 50% | ~92% | -42 pp |
| consciousness | 40% | ~80% | -40 pp |

**Average drift: ~17 percentage points lower in comments than posts.**

Themes that rely on *framing* (consciousness, therapy) degrade the most
because comments are conversational fragments — they argue, dismiss,
and cite. A post titled "AI replaced my therapist" is unambiguous; a
comment that says "I've been using it for therapy 😭" isn't without
parent context.

Themes anchored in *specific vocabulary* (sexual_erp, addiction) hold up
well: recovery argot and NSFW shop-talk survive the move to comments
because the terms are rarely polysemous.

## Implication for the dual-metric export

The `count_post_only` series we added today is the higher-confidence
series. The `count` (post + comment) series expands coverage but
inherits ~17 pp of additional noise on average, concentrated in therapy
and consciousness. Consumers of the data who want high-confidence counts
should read `count_post_only`; consumers who want broader discourse
coverage should read `count` and understand the precision trade-off.

## Stage-2 disambiguation for researcher-accepted keywords

Concrete filter rules drafted for the two rupture-theme researcher-accepted
keywords. Implementation is deferred pending a decision to extend the
YAML schema with per-keyword filters.

### "grieving" (baseline 74% → target 96%)
- **Required context:** post mentions at least one companion platform
  name (ChatGPT, GPT-4o, 5.1, Character.AI, Replika, Chai, NomiAI,
  SoulmateAI, etc.).
- **Regex exclude:** literal animal-death context (pet / cat / dog
  within ±50 chars of "died / passed / euthanized").
- Estimated lift: removes ~5 of 6 FPs in the 30-post sample → 96%.

### "neutered" (baseline 79% → target 96%)
- **Regex exclude:** literal animal-neutering context (cat / dog / pet
  within ±80 chars of "neutered / spayed / sterilized").
- **Required context:** personal rupture narrative — post contains
  first-person change markers ("my companion became", "I used to",
  "no longer", comparison / before-after language).
- Estimated lift: ~96% precision.

## Frontend perf baseline (Lighthouse, myfriendisai.com)

| Category | Score |
|----------|-------|
| Performance    | 92  |
| Accessibility  | 100 |
| Best Practices | 96  |
| SEO            | 100 |

Core Web Vitals: LCP 2.2s (good), TBT 130ms (good), FCP 1.5s (good),
**CLS 0.125** (needs improvement — threshold is 0.1). 2 layout shifts
flagged; the chart area is the most likely culprit. Top JS opportunity:
reduce unused JS (78 KiB savings available) and legacy JS (14 KiB).
Accessibility passed 100 after today's contrast and tap-target fixes.

## Recommended follow-ups, ranked

1. **Romance keyword re-validation (100-sample)** — 50% sample precision
   is far enough below baseline to need a proper pass before acting.
2. **Document dual-metric interpretation on the site.** The About page
   should explain that `count_post_only` is the higher-confidence
   series and what the comment-level precision looks like.
3. **Ship stage-2 filters for grieving and neutered.** Requires a small
   YAML schema extension for per-keyword `filters` and a matcher update.
4. **Investigate CLS 0.125.** Likely the chart area expanding after
   data loads. Reserving vertical space or rendering a placeholder
   would move this under 0.1.
5. **Consider a comment-precision disclaimer** in the transparency
   panel or About page — roughly 17 pp lower precision than posts.
