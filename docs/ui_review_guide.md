# UI/UX Review Guide — My Friend Is AI

A checklist for a thorough review of every page, chart, and piece of copy on
myfriendisai.com. The goal is to catch the class of small frustrations that
make a research site feel unpolished — crammed axis labels, unnamed chart
series, misleading empty states, over-written copy, inconsistent styling.

## How to use this guide

- Read the whole guide before you start.
- You review **code** — read each component and the data it renders, and
  reason about every rendered state, including edge cases you cannot see.
- Sample real data from `web/data/*.json` to reason about real values (long
  subreddit names, tiny numbers, huge numbers, sparse series).
- This is a **read-only audit**. Do NOT edit files. Produce a findings report.
- When something can only be confirmed visually on a real browser/device, say
  so — flag it rather than guessing.

## The review lenses

Check your assigned surface against every lens.

### 1. Charts & data visualisation

- **Axis labels** are human-readable — never raw ISO dates (`2024-03-25`), raw
  data keys, or unformatted numbers. Dates are formatted; long axes are spaced
  (`minTickGap`) so labels never crowd or overlap.
- **Series are named** — a Recharts tooltip must show the metric name, never
  the literal `value`.
- **Units are stated** — every axis / tooltip says what the number is (posts,
  per 1k posts, subscribers, %).
- **No misleading empty span** — a chart never renders a mostly-empty axis with
  a stub of real line in a corner (e.g. a metric that is null for most of its
  range should be cropped to where it has data).
- **Number formatting** — large numbers abbreviated (`11.5M`, not `11489880`);
  decimals sensible; no `NaN`, `Infinity`, or `undefined` reaching the screen.
- **Density** — a line isn't an unreadable scribble; if daily data is too
  noisy to read a trend, note it.
- **Empty / single-point / loading states** are handled gracefully and worded
  plainly.
- **Color** — chart colors come from the shared palette; lazy-load placeholders
  are sized so the chart doesn't jump in.
- **The claim the chart makes is honest** — the theme atlas is direction-only
  (per-panel scales; never invite cross-theme height comparison).

### 2. Data & edge states

For every data-driven element, reason about: empty / no data, a single data
point, all-null values, very small numbers, very large numbers, a very long
string (subreddit or keyword name), a partial current month, a community or
theme with little activity. Does it still look right and read clearly?

### 3. Copy

- **Succinct** — every sentence earns its place; cut anything that doesn't
  change what the reader knows.
- **Plain and direct** — no jargon without explanation, no throat-clearing.
- **Not over-hedged / over-defensive** — state limits once, clearly; don't
  re-litigate them in every paragraph.
- **No self-reference** — avoid "the project has found", "I wanted", "we
  decided"; describe what *is*, not the process.
- **Restrained punctuation** — em-dashes used sparingly, not as a default
  connector; no "precious" or ornamental phrasing.
- **Honest, not overclaiming** — the site measures *explicit theme vocabulary
  in curated communities over time*; it is NOT a measure of how common AI
  companionship is. Copy must never drift back into claiming the latter.
- **Consistent** — terms, capitalisation, and numbers agree across the site
  (e.g. the community count).

### 4. Visual consistency

Check everything against the design system in `web/app/styles.ts`:

- **Text-color ladder** (brighter = more important): Title `#F8FAFC`, Heading
  `#F1F4F8`, Body `#C8D0DC`, Lead `#9AA7B8`, Caption `#6B7689`, Eyebrow
  `#8293A6`. Flag any text color off this ladder.
- **Type scale** — font sizes come from the `fontSize` scale; flag ad-hoc sizes.
- **Reading measure** — running text is capped at the `measure` constant
  (680px); flag uncapped or oddly-capped text.
- **Section rhythm** — sections share the eyebrow + heading + intro pattern;
  spacing is consistent.

### 5. Layout & responsive

- No horizontal overflow at 375px; nothing crammed or clipped.
- Touch targets ≥ 44px; text ≥ 14px except chart axis ticks.
- Alignment is intentional — shared left/right edges, no lonely strips.
- Lazy-loaded chart placeholders are sized per breakpoint (no layout jump).

### 6. Clarity of meaning

- Each section and chart makes its point obvious without the reader working
  for it; headings and intros say what the thing *is*.
- Provenance is clear where it matters (Direct / Inferred / Derived).
- Links say where they go; nothing is a dead end.

## Recently fixed — look for *more of this class*

These were real bugs already fixed; they show the kind of thing to hunt for:

- A chart x-axis showing crammed full ISO dates instead of short month labels.
- A tooltip showing the literal series name `value` instead of the metric.
- A subscribers chart spanning 3 empty years (null backfill) with a stub of
  real line in the corner.
- Two charts on one page showing essentially the same thing (redundant).
- Over-defensive, em-dash-heavy, self-referential copy.

## Severity

- **High** — wrong, misleading, broken, or genuinely hard to read.
- **Medium** — clearly suboptimal; a reasonable reader would be mildly
  frustrated or confused.
- **Low / nit** — polish; consistency; a better word.

## Report format

Produce a findings list. For each finding:

- **Location** — `file:line` and the on-screen element.
- **Lens** — which lens above.
- **Severity** — High / Medium / Low.
- **Issue** — what's wrong, concretely.
- **Suggested fix** — a specific, concrete change.

Group by severity, highest first. Be honest about what's a real problem versus
a marginal nit. If a surface is genuinely fine, say so rather than inventing
issues.
