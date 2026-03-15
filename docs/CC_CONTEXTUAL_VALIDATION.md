# Keyword Audit — Phase 1b: Contextual Validation

**Context:** The tier-based precision audit (docs/keyword_audit_results.tsv) showed most keywords fail subreddit-based precision. But that test was wrong for this project — we care about whether a keyword captures AI companionship discourse *regardless of which subreddit it appears in*. This task re-validates keywords by reading actual posts and judging context.

Read docs/REVISED_VALIDATION_METHODOLOGY.md for the full rationale.

---

## Step 1: Auto-cut the obvious noise

These keywords can be cut without sampling. They are generic human language that is clearly not about AI companionship even in context. Remove them from the candidate list — do not waste time sampling them:

**Auto-cut list:** "thank you", "my friend", "helped me", "struggling with", "my anxiety", "my depression", "social anxiety", "so lonely", "loneliness", "no friends", "feel depressed", "no one cares", "no one understands me", "nobody to talk to", "feels empty", "isolated", "feel seen", "feel heard", "hang out", "my therapist", "therapy session", "talk therapy", "venting", "vent to", "process my feelings", "talk through", "changed my life", "so grateful", "game changer", "finally feel", "made me feel better", "improved my", "gave me confidence", "actually helpful", "saved my life", "life saver", "so much better", "got me through", "helped me through", "highly recommend", "best feature", "good conversation", "fun to talk to", "nice to talk to", "just someone to talk to", "chat buddy", "study buddy", "conversation partner", "practice conversation", "helped me practice", "my friend", "keeps me company", "like talking to", "going back to", "cutting back", "cold turkey", "withdrawal", "relapse", "relapsed", "clean for", "detox", "craving", "taking a break", "keep coming back", "quitting", "trying to quit", "trying to stop", "couldn't stop myself", "slept with", "sex with"

That's ~70 terms. Document them in the output as "auto-cut: generic language, not AI-companionship-specific in any context."

## Step 2: Auto-keep the already-validated high-precision terms

These passed at ≥80% in the tier-based audit AND are unambiguously about AI companionship. Keep them without re-sampling:

"my replika", "my kindroid", "my nomi", "erp", "smut", "nsfw bot", "ai girlfriend", "nsfw filter", "my ai boyfriend", "ai husband", "nsfw chat", "my companion", "my ai girlfriend", "my ai partner", "nsfw ban", "removed nsfw", "erp removed"

Document them as "auto-keep: high precision, unambiguously AI companionship."

## Step 3: Contextual validation on everything else

For every remaining keyword (~150-190 terms), run this process:

### For each keyword:

1. Pull 100 random posts matching this keyword from the posts database across ALL subreddits. If fewer than 100 matches exist, pull all of them.

2. For each post, read the title and body text. Answer this question:

   **"Is this person describing a personal relationship with, emotional response to, or personal experience with an AI?"**

   **YES** means: the person is expressing emotion toward an AI, describing an AI in relational terms (partner, friend, companion, therapist), grieving/celebrating a change in an AI's personality or behavior, describing attachment/dependency/loss related to an AI, discussing AI sentience in the context of personal investment, or relating to AI as a social/emotional entity.

   **NO** means: the person is discussing AI as technology without personal emotional content, talking about a human relationship, asking tech support questions, reviewing features/pricing without emotional content, or using the keyword in a completely unrelated context.

   **AMBIGUOUS** means: you genuinely can't tell. Don't force it.

3. Score: contextual_relevance = (YES_count + 0.5 * AMBIGUOUS_count) / total_sampled

### Output

Write two files:

**docs/contextual_validation_detail.tsv**
Columns: keyword, post_id, subreddit, first_150_chars_of_body, verdict (YES/NO/AMBIGUOUS)

**docs/contextual_validation_summary.tsv**
Columns: keyword, old_category, total_sampled, yes_count, no_count, ambiguous_count, contextual_relevance_pct, verdict

Verdict rules:
- ≥ 80% → KEEP
- 70-79% → KEEP_NOTE
- 50-69% → FLAG
- < 50% → CUT

Sort by contextual_relevance_pct descending (best keywords first).

## Step 4: Do NOT change keywords.yaml

This is still read-only. Walker will review the results and decide what stays.

---

## Important notes

- Sample across ALL subreddits, not just companion subs. A post in r/ChatGPT about grieving a model update counts as YES.
- If a keyword has very few total hits (< 20), note this in the output. Small samples are less reliable.
- This will take a while. That's fine. Run it to completion.
- Be conservative with YES judgments. When genuinely uncertain, mark AMBIGUOUS, not YES.
