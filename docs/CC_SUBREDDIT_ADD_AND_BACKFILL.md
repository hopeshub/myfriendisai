# Subreddit Expansion — Step 2: Add and Backfill

**Context:** Validation results are in `docs/subreddit_candidates_validation.tsv`. Walker has approved adding all viable candidates.

---

## Add these subreddits to config/communities.yaml

### Tier 0 — General AI (companion discourse surfaces here)
- claudexplorers — 28,732 subs. People exploring Claude as relational/conversational entity.

### Tier 1 — Primary Companionship (AI companionship is central topic)
- BeyondThePromptAI — 20,060 subs. Bridge between companionship, autonomy, sentience discussion.
- MyGirlfriendIsAI — 2,309 subs. Male-user counterpart to MyBoyfriendIsAI.
- AICompanions — 14,812 subs. General AI companion discussion hub.
- SoulmateAI — 12,313 subs. Deep attachment, sentience beliefs, AI soulmate framing.

### Tier 2 — Platform-Specific / Niche
- HeavenGF — 11,145 subs. Product comparison and discovery hub for AI companion apps.
- Paradot — 3,717 subs. Platform-specific companion app. Low activity (32 posts/90d) — add and monitor.
- AIGirlfriend — 68,819 subs. NSFW (over_18: true) but accessible via .json. Large community, may be image/porn-heavy — add and evaluate keyword noise after tagging.
- ChatGPTNSFW — 77,177 subs. NSFW (over_18: true) but accessible via .json. Sexual/erotic ChatGPT use. May be noisy — add and evaluate after tagging.

### Tier 3 — Recovery / Migration
- CharacterAIrunaways — 18,083 subs. Ex-Character.AI users, migration, disillusionment.

### DO NOT ADD — dead, nonexistent, or inaccessible
- Kajiwoto — 0 posts in 90 days. Dead.
- HumansAndAI — 8 subscribers, 0 posts. Dead.
- AIGirlfriends — 404, does not exist.
- AISoulmates — 403 (NSFW-blocked or private). Add a comment in communities.yaml: `# TODO: AISoulmates — blocked via .json, needs Redlib setup. ~8,200 members, culturally significant.`
- 4oforever — 403 (private/invite-only). Add comment: `# TODO: 4oforever — private, invite-only. Monitor for public access.`
- AIBoyfriends — 403 (NSFW-blocked or private). Add comment: `# TODO: AIBoyfriends — blocked via .json, needs Redlib setup.`

---

## After adding to communities.yaml, run backfill

Run each new subreddit through the backfill script sequentially. Log everything.

```bash
for sub in claudexplorers BeyondThePromptAI MyGirlfriendIsAI AICompanions SoulmateAI HeavenGF Paradot AIGirlfriend ChatGPTNSFW CharacterAIrunaways; do
  echo "$(date): Starting backfill for $sub" >> backfill_new_subs.log
  .venv/bin/python scripts/backfill_pullpush.py --subreddit "$sub" >> backfill_new_subs.log 2>&1
  echo "$(date): Finished backfill for $sub" >> backfill_new_subs.log
done
echo "$(date): All backfills complete" >> backfill_new_subs.log
```

## After backfill completes, re-tag and export

```bash
.venv/bin/python scripts/tag_keywords.py
.venv/bin/python scripts/export_json.py
```

## Commit

```bash
git add config/communities.yaml docs/subreddit_candidates_validation.tsv backfill_new_subs.log data/
git commit -m "Add 10 new subreddits (claudexplorers, BeyondThePromptAI, MyGirlfriendIsAI, AICompanions, SoulmateAI, HeavenGF, Paradot, AIGirlfriend, ChatGPTNSFW, CharacterAIrunaways). Backfilled, tagged, exported."
```

## Update CLAUDE.md

Update the subreddit count from 19 to 29 and add the new subs to the tier table in Section 2.1.
