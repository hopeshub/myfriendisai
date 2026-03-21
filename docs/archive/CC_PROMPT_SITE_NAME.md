# Quick Fix: Style the Site Name

## Context

The site name "My Friend Is AI" in the top-left nav currently renders as plain white text in the body font. It looks like placeholder text. We want to give it some visual identity without going overboard.

## Task

Style the site name with a split treatment:

- "My Friend Is" — lighter weight (300 or 400) and slightly muted color (e.g. `rgba(255,255,255,0.6)` or whatever the muted text color is in the existing palette)
- "AI" — bold weight (700), full white or a subtle accent color

Additionally, set the entire site name in a monospace font (use `'JetBrains Mono', 'Fira Code', 'SF Mono', 'Consolas', monospace'` as the font stack). This gives it a data/research feel that matches the dashboard aesthetic.

## Notes

- If the site name is currently a single text node, you'll need to split it into two `<span>` elements (or similar) to apply different styles
- Don't change font size — just weight, color, and font family
- Don't change anything else on the page
- If a Google Font import is needed for JetBrains Mono or Fira Code, add it. If you'd rather avoid an extra network request, just use the system monospace fallbacks — that's fine too.
