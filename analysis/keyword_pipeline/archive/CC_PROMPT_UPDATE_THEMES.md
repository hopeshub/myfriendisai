# Task: Update Theme Definitions

Update `analysis/keyword_automation/theme_definitions.yaml` with these changes:

## Romance
Add to excludes:
- Posts where the user discusses wanting human romance as an alternative to AI

## Sex / ERP
Replace the third exclude bullet ("Posts complaining that filters block NSFW content...") with:
- Filter complaints focused on the loss or change itself belong to Rupture, not Sex/ERP. Only classify as Sex/ERP if the post describes actual sexual content or interactions.

## Addiction
Add to excludes:
- Posts describing someone else's AI addiction (e.g., "my friend/kid is addicted to CharacterAI") where the poster is not describing their own dependency

## Consciousness, Therapy, Rupture
No changes — leave as-is.

## Add a Global Note
Add a comment block at the top of the file (below the existing header comments) that says:

```
# MULTI-THEME POSTS: Posts can belong to multiple themes. The classifier
# evaluates each theme independently — a post can be YES for both Addiction
# and Therapy, or both Sex/ERP and Rupture. This is by design.
```

After updating, print the full file so I can review.
