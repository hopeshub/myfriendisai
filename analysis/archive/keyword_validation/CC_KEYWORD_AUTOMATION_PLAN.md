# Keyword Automation Pipeline — Project Plan

## Overview

A semi-automated pipeline for discovering, validating, and disambiguating keywords for the myfriendisai project. Three phases, each building on the last. The goal is to go from "multi-hour interactive brainstorm → manual scoring" to "run scripts to prepare data → CC classifies → review summary table → accept/reject."

No API key required. CC itself is the classification engine — scripts handle sampling, formatting, and storage; CC does the judgment.

## Architecture

```
Phase 3: Discovery          Phase 2: Validation          Phase 1: Disambiguation
┌─────────────────┐    ┌──────────────────────┐    ┌──────────────────────────┐
│ Corpus-driven    │───>│ Batch validation      │───>│ CC-powered classifier    │
│ candidate finder │    │ (100-post samples)    │    │ (post + theme → yes/no)  │
└─────────────────┘    └──────────────────────┘    └──────────────────────────┘
       OUTPUT:                OUTPUT:                      OUTPUT:
  Ranked candidate      Precision table with         Per-post classification
  list per theme        FP patterns                  stored in SQLite
```

Build right to left: Phase 1 first (it's the engine everything else depends on).

---

## Phase 1: CC-Powered Disambiguation Layer

**What it does:** Scripts prepare batches of posts for classification. CC reads the posts and theme definition, classifies each post YES/NO, and a script parses CC's output back into SQLite. No API key needed — CC is the LLM.

### Step 1.1: Theme Definitions
- Create `analysis/keyword_automation/theme_definitions.yaml` with a plain-language definition of each theme. These describe what DOES and DOES NOT count. Draft definitions:
  - **Romance**: Posts about romantic love, dating, emotional attachment, or relationship dynamics with an AI companion. NOT: fictional roleplay premises that happen to include romance; posts about human romantic relationships.
  - **Sex / ERP**: Posts about sexual or erotic roleplay interactions with AI. NOT: discussions of NSFW filter policies (unless describing personal sexual interactions); clinical/academic discussion of AI and sexuality.
  - **Consciousness**: Posts questioning whether AI has sentience, awareness, feelings, or inner experience. NOT: technical discussions of AI architecture; generic "AI is just code" dismissals without engaging the question.
  - **Therapy**: Posts about using AI as a therapist, counselor, emotional support tool, or mental health aid. NOT: casual venting to AI without framing it as therapeutic; posts about human therapists.
  - **Addiction**: Posts using language of dependency, compulsion, inability to stop, or withdrawal in relation to AI companion use. NOT: casual "I use it a lot"; posts about other addictions discussed with AI.
  - **Rupture**: Posts about the loss, degradation, or destruction of an AI companion's personality due to platform updates, model changes, filter changes, or shutdowns. NOT: real-world grief processed with AI; generic product complaints about AI quality; fictional/roleplay grief.
- IMPORTANT: These are starting drafts. Print them for Walker to review before proceeding. He may want to adjust.

### Step 1.2: Sample Preparation Script
- Create `analysis/keyword_automation/prepare_sample.py`
- Input: keyword, theme, sample size (default 100)
- Pulls sample posts containing the keyword from tracker.db (same sampling logic as existing validate_keyword.py — stratified across subreddits)
- Outputs a JSON file: `analysis/keyword_automation/samples/{keyword}_{theme}.json`
- Each entry contains: post_id, subreddit, title, body (truncated to ~500 words if needed)
- This file is what CC will read and classify

### Step 1.3: Classification Prompt Template
- Create `analysis/keyword_automation/classify_prompt_template.md`
- This is a prompt that CC will follow when classifying a batch. Template:

```
## Classification Task

Theme: {theme_name}
Definition: {theme_definition}

For each post below, classify YES if the post belongs to the "{theme_name}" theme per the definition above, or NO if it does not. Respond in CSV format: post_id,classification

Posts:

{formatted_posts}
```

- The prepare_sample.py script should also generate a ready-to-use version of this prompt with the posts filled in, saved as `analysis/keyword_automation/samples/{keyword}_{theme}_prompt.md`
- CC reads this file and outputs classifications

### Step 1.4: Results Parser Script
- Create `analysis/keyword_automation/parse_classifications.py`
- Input: keyword, theme, and CC's classification output (pasted or piped)
- Parses the CSV classifications
- Stores results in a new `llm_classifications` table in tracker.db:
  - post_id (TEXT)
  - theme (TEXT)
  - keyword (TEXT)
  - classification (TEXT — YES/NO)
  - classified_at (TIMESTAMP)
  - PRIMARY KEY (post_id, theme, keyword)
- Outputs a summary: precision, subreddit breakdown of YES vs NO, top 5 NO posts for spot-checking
- This table also acts as a cache — if a post has already been classified for this theme+keyword, skip it

### Step 1.5: Test with "grieving"
- Run prepare_sample.py for "grieving" / "rupture" using the same 100 posts from the existing manual validation
- CC classifies the batch using the prompt template
- Run parse_classifications.py to store and summarize
- Compare CC's classifications against the manual scores from the existing scoring sheet
- Report agreement rate — this tells us if CC's judgment aligns with Walker's manual scoring
- STOP and show results to Walker before proceeding

---

## Phase 1 Workflow (what it looks like in practice)

```bash
# Step 1: Prepare the sample (Walker runs this or tells CC to)
python3 analysis/keyword_automation/prepare_sample.py --keyword "soulless" --theme rupture

# Step 2: CC reads the generated prompt file and classifies
# Walker tells CC: "Read analysis/keyword_automation/samples/soulless_rupture_prompt.md and classify each post"

# Step 3: CC outputs CSV classifications, which get parsed
python3 analysis/keyword_automation/parse_classifications.py --keyword "soulless" --theme rupture --input <CC's output>
```

Total Walker effort: two commands + one CC prompt. No API key. No manual scoring.

---

## Phase 2: Streamlined Batch Validation

**What it does:** Wraps Phase 1 into a smoother batch workflow so Walker can validate multiple keywords in one session.

### Step 2.1: Batch Preparation Script
- Create `analysis/keyword_automation/prepare_batch.py`
- Input: a YAML file listing keyword/theme pairs to validate
- Runs prepare_sample.py for each pair
- Generates one combined prompt file with all keywords, clearly separated by headers
- CC can classify the whole batch in one pass (or Walker can break it into chunks if it's too large)

### Step 2.2: Batch Summary Script
- Create `analysis/keyword_automation/summarize_batch.py`
- Reads all classifications from llm_classifications table for a given batch
- Outputs a summary table:

```
Keyword       | Theme    | Hits | CC Precision | Top FP Pattern        
------------- | -------- | ---- | ------------ | ---------------------
grieving      | Rupture  | 255  | 87%          | real-world grief (8%)
soulless      | Rupture  | 75   | 72%          | generic complaint    
```

- STOP and show summary to Walker for accept/reject decisions

---

## Phase 3: Corpus-Driven Discovery

**What it does:** Instead of brainstorming keywords from intuition, empirically finds words that are statistically overrepresented in posts that match a given theme.

NOTE: Raw TF-IDF on Reddit data produces heavy noise from copypasta, character names,
usernames, and platform-specific artifacts. The filtering requirements below were developed
through trial and error and are essential for usable output.

### Step 3.1: Build Theme Corpus
- For each theme, pull all posts that match ANY existing accepted keyword for that theme
- This is your "positive" corpus for the theme

### Step 3.2: Overrepresentation Discovery
- Script: `analysis/keyword_automation/discover_keywords.py`
- Compare word frequencies in the theme corpus vs. a baseline sample of non-theme posts
- Score by overrepresentation ratio (theme frequency / baseline frequency)
- Filter out:
  - Words already in the current keywords yaml
  - Common stopwords
  - Words shorter than 5 characters (catches substrings of platform names)
  - Words with fewer than 10 distinct posts containing the term (raw token count is misleading — copypasta inflates frequency)
  - Words appearing in fewer than 3 distinct subreddits (too concentrated)
  - Proper nouns: words capitalized >80% of the time (character names, usernames)
  - Words that are substrings of subreddit names in the corpus
- Output: ranked list of top N candidate keywords per theme, with distinct post counts, subreddit spread, ratios, and corpus volume

### Step 3.3: Feed into Phase 2
- Use `--generate-batch` to auto-create a batch YAML from top candidates
- Run them through the Phase 2 batch workflow (prepare_batch → CC classifies → parse_batch)
- Walker reviews summary table, accepts/rejects

---

## File Structure

```
analysis/keyword_automation/
├── README.md                        # This plan
├── theme_definitions.yaml           # Theme definitions for classification prompts
├── prepare_sample.py                # Prepare posts for CC classification
├── classify_prompt_template.md      # Prompt template CC follows
├── parse_classifications.py         # Parse CC output → SQLite + summary
├── prepare_batch.py                 # Phase 2: multi-keyword prep
├── summarize_batch.py               # Phase 2: summary table
├── discover_keywords.py             # Phase 3: TF-IDF discovery
├── samples/                         # Generated sample files and prompts
└── results/                         # Output reports
```

---

## Working Agreements

- Complete each phase fully before moving to the next
- STOP at each checkpoint marked above and show results to Walker
- Each script should be runnable standalone from the command line with --help
- Don't over-engineer: simple scripts, not a framework
- Walker's accept/reject is always the final call
