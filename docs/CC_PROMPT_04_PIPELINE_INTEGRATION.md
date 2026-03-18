# CC Prompt 4: Daily Pipeline Integration

Read `docs/COMMENTS_SYSTEM_SPEC.md` first. This prompt covers Section 12 (Implementation Sequence, Prompt 4) — wiring comment collection and tagging into the automated daily run.

Also review:
- `scripts/collect_daily.py` — the existing daily pipeline
- `scripts/collect_comments.py` — comment collection (Prompt 2)
- `scripts/tag_comments.py` — comment tagging + propagation (Prompt 3)
- `scripts/tag_keywords.py` — existing post keyword tagger

---

## Goal

Update the daily pipeline so that a single run collects posts, tags posts, collects comments, tags comments, propagates comment tags, and exports JSON — all in the correct order, with logging and error handling.

---

## Execution Order

The daily pipeline should run these steps in order:

```
1. Collect subreddit data + posts       (existing — no changes)
2. Tag posts with keywords              (existing tag_keywords.py — wire in if not already called)
3. Collect comments for eligible posts   (NEW — collect_comments.py)
4. Tag comments + propagate to posts    (NEW — tag_comments.py)
5. Export all JSON                       (existing — no changes, already picks up comment-sourced tags)
6. Copy JSON to web/data/               (existing — no changes)
```

### Important note on step 2

From the Step A inspection in Prompt 1, we learned that `scripts/tag_keywords.py` is NOT currently called by `collect_daily.py` — it's run separately. For the comment pipeline to work correctly, post tagging must happen before comment tagging (because propagation needs to know which posts already have post-sourced tags). 

**Options:**
- **Option A**: Add `tag_keywords.py` to the daily pipeline before the comment steps. This means post tagging becomes automated too.
- **Option B**: Leave `tag_keywords.py` as a separate manual step, and just add comment collection + tagging to the daily pipeline. Comment propagation will still work — it just means if post tagging hasn't been run recently, some propagation comparisons may be stale.

**Go with Option A** — add post tagging to the pipeline. It's cleaner and ensures the full tagging state is consistent before comment tagging runs. If there's a reason it was kept separate historically (e.g., it's slow), add it but log its duration so we can monitor.

---

## Error Isolation

Each step should be wrapped so that a failure in one step doesn't kill the entire pipeline:

- If comment collection fails partway through, log the error and continue to comment tagging (tag whatever was collected)
- If comment tagging fails, log the error and continue to export (existing post tags still work)
- If export fails, log the error

The existing post collection steps should continue to work exactly as before — the comment steps are additive. A failure in comments should never prevent posts from being collected or exported.

---

## Pipeline Logging

Add a summary at the end of the daily run that includes timing for each step:

```
Daily pipeline complete:
  1. Post collection:      X min (Y posts collected)
  2. Post keyword tagging:  X min (Y posts tagged)
  3. Comment collection:   X min (Y comments from Z posts)
  4. Comment tagging:      X min (Y hits, Z posts newly tagged via comments)
  5. JSON export:          X min
  Total duration:          X min
  Total Reddit requests:   X
```

This is important for monitoring — we estimated ~37–46 minutes total. Actual numbers will tell us if we need to adjust.

---

## Testing

1. **Dry run the full pipeline** — if there's a dry-run mode or a way to test without making actual Reddit requests, do that first. If not, just run the pipeline normally (it should be safe since each component is already tested individually).

2. **Run the full pipeline once** and show me:
   - The complete summary log with timing for each step
   - How many comments were collected
   - How many comment-sourced tags were created
   - Confirmation that the JSON export completed and includes both metric views

3. **Verify the final state**:
   - Total rows in `comments` table
   - Total rows in `comment_keyword_hits` table  
   - Total rows in `post_keyword_tags` with `source='comment'` vs `source='post'`
   - Quick sanity check: are the `keyword_trends.json` numbers reasonable?

4. **Run the pipeline a second time** to confirm idempotency — posts already collected should be skipped, comments already tagged should be skipped, export should produce identical output.

Show me all results.
