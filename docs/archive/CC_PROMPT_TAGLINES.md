# Task: Add Theme Taglines to Frontend Cards

## Context
Each theme card on the homepage (Romance, Sex/ERP, Consciousness, Therapy, Addiction, Rupture) needs a short descriptive tagline displayed below the theme name. These taglines explain what vocabulary each theme tracks.

## The taglines

| Theme         | Tagline                                                  |
|---------------|----------------------------------------------------------|
| Romance       | Language of love, dating, and romantic attachment         |
| Sex / ERP     | Language of sexual and erotic roleplay                   |
| Consciousness | Language of sentience, awareness, and inner experience   |
| Therapy       | Language of mental health support and emotional care     |
| Addiction     | Language of dependency and compulsion                    |
| Rupture       | Language of loss and grief                               |

## Requirements

1. Add the tagline text below the theme name on each card (the row of colored cards near the top of the page).
2. The tagline should sit between the theme name and the metric number (e.g., "4.8 mentions / 1k posts").
3. Style it as a subtle secondary line — smaller font size, muted/lower-opacity text so it doesn't compete with the theme name or the metric.
4. Make sure the taglines don't break the card layout — they need to work within the existing card dimensions without causing overflow or misalignment across the row.
5. The tagline data should live in whatever config or data structure already defines the theme names/colors, not be hardcoded in the template.
