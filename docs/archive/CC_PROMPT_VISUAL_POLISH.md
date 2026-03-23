# Visual Polish Pass

## Task

A set of small visual improvements to tighten the layout and reduce visual clutter. Each change is small but they compound.

## Changes

### 1. Remove "Select a theme to explore" text
- Delete this instructional text entirely. The cards are self-evidently clickable and the text adds an unnecessary layer between the controls and the cards.

### 2. Move methodology note below the chart
- The text that reads "Each theme tracks validated keywords. Mention rates reflect how distinctive each theme's vocabulary is, not necessarily how prevalent the topic is overall."
- Currently sits between the cards and the chart — move it below the chart on desktop (this may already be done for mobile in the Phase 2 responsive work, but do it for all viewports now)
- This lets the cards flow directly into the chart without a text interruption

### 3. Tighten the gap between cards and chart
- Reduce the vertical margin/spacing between the bottom of the card row and the top of the chart container by roughly 30-40%
- They should feel like one connected unit: selector → visualization

### 4. Reduce dead space in the controls row
- The time range buttons (6M, 1Y, 2Y, ALL) are left-aligned and the Absolute/Relative toggle is right-aligned
- This is fine, but check if there's excessive vertical padding/margin above and below this row
- Tighten vertical spacing so the controls feel tucked in, not floating in their own band

### What NOT to change
- Card design (colors, borders, sparklines, content)
- Chart design (lines, annotations, axes)
- Site name / nav
- Dark theme / colors
- Overall page width / max-width
