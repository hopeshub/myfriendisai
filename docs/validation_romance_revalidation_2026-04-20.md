# Romance Theme — Re-validation 2026-04-20

Full 19-keyword re-validation of the romance theme following a precision
smoke test (`docs/precision_audit_2026-04-20.md`) that scored romance at
**50%** on a last-30-day post sample, far below the ~93% baseline. Run
via four parallel agents (Groups A–D). Per-group results are preserved
in `validation_romance_revalidation_2026-04-20_group{A,B,C,D}.md`.

## Methodology

- Scope: T1-T3 active subreddits only (22 subs). Case-insensitive match.
- Window: `created_utc >= 2026-01-01` (~3.5 months, same discourse era
  as the smoke test).
- Target: random sample of 100 matching posts per keyword; actual sample
  = full in-window population where matches < 100.
- Classification: YES / NO / AMBIGUOUS. Precision = YES / (YES + NO).
- Thresholds: ≥80% KEEP · 60-79% REVIEW · <60% CUT.

## Results

| Keyword | Baseline | Precision | N | Verdict | Notes |
|---|---|---|---|---|---|
| **Group A — AI-explicit identity** | | | | | |
| my ai partner | 97.9% | 100.0% | 17 | KEEP | |
| my ai girlfriend | 94.1% | 85.7% | 7 | KEEP | thin sample |
| ai husband | 94.2% | 75.0% | 13 | REVIEW | |
| my ai boyfriend | 94.7% | 62.5% | 8 | REVIEW | |
| ai wife | 92.3% | 0.0% | 1 | N/A | sample unusable |
| **Group B — AI relationship terms** | | | | | |
| love my ai | 81.5% | 100.0% | 4 | KEEP | thin sample |
| married my | 86.0% | 100.0% | 1 | N/A | sample unusable |
| ai lover | 94.0% | 50.0% | 9 | CUT? | rhetorical-use drift |
| dating my | 80.0% | 0.0% | 9 | **artifact** | regex bug — see below |
| husbando | 95.5% | 0.0% | 2 | N/A | sample unusable |
| **Group C — Milestones** | | | | | |
| proposed to me | 92.1% | 100.0% | 4 | KEEP | thin sample |
| our anniversary | 89.5% | 100.0% | 1 | N/A | sample unusable |
| our wedding | 87.0% | 88.9% | 9 | KEEP | thin sample |
| our first kiss | 85.7% | 100.0% | 2 | N/A | sample unusable |
| engagement ring | 79.3% | 100.0% | 1 | N/A | sample unusable |
| **Group D — General + endings** | | | | | |
| honeymoon | 83.3% | 60.0% | 10 | REVIEW | "honeymoon phase" = 2/4 NOs |
| wedding | 80.6% | 62.2% | 38 | **REVIEW — drift confirmed** | only large-sample drift finding |
| we broke up | 75.0% | 0.0% | 2 | N/A | sample unusable |
| in a relationship with | 77.4% (REVIEW) | 64.7% | 17 | REVIEW — **do not promote** | |

## Key findings

### 1. In-window sample sizes are too small to act on most keywords

13 of 19 keywords returned fewer than 15 in-window hits; 6 of those
returned fewer than 5. Small-sample precision swings dominate any real
drift signal. This is itself a useful finding: **romance-keyword
volume has collapsed in 2026-Q1** relative to historical baselines.
Whether that's a real decline in AI-romance discourse, a collection
artifact, or a denominator-shift effect (more meta-commentary crowding
out first-person posts) is worth investigating separately.

Before editing `config/keywords_v8.yaml`, a wider window (2025-06-01+
or 2025-01-01+) is needed to reach n≥50 per keyword for the borderline
ones.

### 2. Confirmed drift: `wedding` (n=38)

`wedding` is the only keyword with enough volume to verdict reliably.
Precision dropped from 80.6% → 62.2%. The FP mix is dominated by
ChatGPTcomplaints posts where "wedding" appears inside satirical/
meta-commentary content (fabricated OpenAI PR scripts quoting
hypothetical users, BBC article citations, reporter-style timelines of
the 4o-retention controversy). This FP category didn't exist at
baseline validation time.

### 3. Probable drift: `in a relationship with` (n=17)

From 77.4% (REVIEW at baseline) to 64.7%. Still REVIEW; should not be
promoted to KEEP. Same meta-commentary FP pattern as `wedding`.

### 4. Probable drift: `honeymoon` (n=10)

From 83.3% to 60.0% on the edge of CUT. "honeymoon phase" (metaphorical,
referring to platform/product novelty) is 2 of 4 NOs. A regex exclusion
for that substring was already flagged as a known issue in the v8 yaml
comment.

### 5. Separate pre-existing bug: multi-word keywords lack word boundaries

`src/keyword_matching.py:26-29` compiles multi-word terms with
**substring matching** (no `\b` boundaries), while single-word terms
get boundaries. This means `dating my` matches `upDATING MY`,
`valiDATING MY`, `invaliDATING MY`. Group B's 0% precision for
`dating my` is entirely this bug, not drift — 8 of 9 hits were
"updating my" / "validating my" inside unrelated ChatGPTcomplaints
posts.

The bug affects all multi-word keywords across all themes, though
most phrases have a leading space in practice that limits collisions.
`dating my`, `in a relationship with`, `lost my`, and similar phrases
starting with short substrings are the highest exposure. Worth a
separate pass to add `\b` boundaries and re-measure every multi-word
keyword's precision — this may explain part of the theme-wide drift
observed in the smoke test.

### 6. Dominant FP vector across all groups: ChatGPTcomplaints meta-discourse

Independent agents all identified the same new FP category that
didn't exist at baseline:

- Satirical / invented OpenAI PR scripts that quote hypothetical user
  complaints (one post firing multiple romance keywords at once).
- Third-person reporter-style posts citing BBC / press coverage of the
  4o-retention campaign.
- Rhetorical / ironic use of romance phrases by companion-sub users
  pushing back on critics' mockery ("it's not because 'my AI boyfriend
  is gone'").

This is a structural FP pattern — first-person romance vocabulary
appearing inside third-person meta-commentary — not a keyword-by-keyword
issue. A keyword-level fix can't fully resolve it; it likely requires
stage-2 filtering (e.g., excluding posts that quote other users, or
detecting third-person framing).

## Recommendations

1. **Do not edit `config/keywords_v8.yaml` yet.** Most in-window
   samples are too thin. Only `wedding`, `in a relationship with`, and
   `honeymoon` have enough volume to act on, and all three were already
   on the edge (REVIEW or researcher-accepted).

2. **Fix the multi-word regex bug first** (`src/keyword_matching.py`),
   re-tag the corpus, then re-run this validation. Precision numbers
   before the fix aren't comparable to baseline precision numbers.

3. **Widen the re-validation window to 2025-06-01+ for the 6 keywords
   with ambiguous results.** Target n≥50 per keyword for borderline
   verdicts. Specifically: `ai husband`, `my ai boyfriend`, `ai lover`,
   `honeymoon`, `wedding`, `in a relationship with`.

4. **Treat the ChatGPTcomplaints meta-discourse pattern as a theme-wide
   FP category, not a per-keyword issue.** Consider a stage-2 filter
   that excludes posts with quotation markers + third-person pronouns,
   or explicitly tagged as satire/news.

5. **Investigate the volume collapse.** Romance keyword hits in the
   2026-01-01+ window are strikingly low (67 total matches across the
   four highest-baseline-volume keywords in Group D). This is worth
   understanding before any keyword decisions.

## Group reports

Detailed per-keyword classifications with example FP/YES posts:

- `validation_romance_revalidation_2026-04-20_groupA.md`
- `validation_romance_revalidation_2026-04-20_groupB.md`
- `validation_romance_revalidation_2026-04-20_groupC.md`
- `validation_romance_revalidation_2026-04-20_groupD.md`
