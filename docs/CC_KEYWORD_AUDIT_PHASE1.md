# Keyword Audit — Phase 1: Precision Scoring

**Context:** The corpus now includes ~29 subreddits after the expansion backfill. All posts have been re-tagged. This task audits every keyword currently in `config/keywords.yaml` for precision — measuring whether each term actually captures AI companionship discourse or just background noise.

**Important:** This is a read-only audit. Do NOT change keywords.yaml. Just produce the report.

---

## What to do

For EVERY term in `config/keywords.yaml`, query the posts database:

1. **Total hits** — how many posts match this term (use the FTS5 index or the existing keyword_tags table)
2. **Companion hits** — how many of those matches come from Tier 1, 2, or 3 subreddits (as defined in `config/communities.yaml`)
3. **General hits** — how many come from Tier 0 subreddits
4. **Companion %** — companion_hits / total_hits, expressed as a percentage
5. **Category share %** — what percentage of this term's category total does this single term account for? (This flags concentration risk — if one keyword is 40%+ of a category, that category is fragile.)

## Output

Write results to `docs/keyword_audit_results.tsv` with these columns:

```
category	term	total_hits	companion_hits	general_hits	companion_pct	category_share_pct
```

**Sort by:** companion_pct ascending (worst precision first — makes problems easy to spot).

Also output a summary section at the bottom or in a separate file `docs/keyword_audit_summary.txt` showing:
- Total terms audited
- How many terms fall in each precision band:
  - ≥ 85% companion (strong)
  - 80-84% (borderline)
  - 60-79% (below threshold)
  - < 60% (noise)
  - < 5 total hits (too rare)
- Per-category breakdown: for each of the 15 categories, how many terms are strong / borderline / below / noise / rare
- Any terms where category_share_pct > 40% (concentration risk)

## Do NOT

- Do not modify keywords.yaml
- Do not modify communities.yaml
- Do not re-run the tagger or exporter
- Do not make any judgment calls about what to keep or cut — just report the numbers

Walker will review the output and make decisions from there.
