# Researcher-Accepted Keywords: Methodology Language

## For CLAUDE.md (internal methodology doc)

Add this to the keyword validation section:

### Researcher-Accepted Keywords

Keywords scoring in the review band (60-79%) may be accepted at the researcher's discretion when all of the following conditions are met:

1. False positive patterns are well-defined and categorizable (not random noise)
2. No cross-theme collisions above 30%
3. The keyword captures vocabulary not already represented by existing keywords in the theme
4. False positive patterns are amenable to future LLM-based disambiguation (stage 2 filtering)

These decisions are logged with rationale in the keyword's scoring sheet. Researcher-accepted keywords are tagged as such in keywords_v8.yaml (or current version) to distinguish them from auto-accepted (≥80%) keywords.

Current researcher-accepted keywords:
- "grieving" → Rupture (74.0%) — FPs are real-world grief, fictional roleplay, and lawsuit coverage; TPs cleanly hit 4o deprecation, Replika Feb 2023, SoulmateAI shutdown. No cross-theme collisions. Accepted for vocabulary diversity (first emotional-register keyword in a theme dominated by the lobotomy metaphor).

---

## For the About page (public-facing)

Keywords are validated through manual scoring of 100-post samples. Keywords scoring 80% or above are automatically accepted. Keywords in the 60-79% range may be accepted at the researcher's discretion when false positive patterns are well-defined and the keyword adds meaningful vocabulary diversity to the theme. All validation decisions are documented and available on GitHub.
