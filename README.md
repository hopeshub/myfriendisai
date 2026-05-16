# My Friend Is AI

An independent, one-person research dashboard tracking how people talk about AI companionship across Reddit. Visualizes validated-keyword trends across 27 subreddits using daily snapshots and regex matching, normalized per 1,000 posts. The chart uses keyword counts only — there is no AI classification in it.

**Live site:** [myfriendisai.com](https://myfriendisai.com)

## What this is

This project tracks the **language** people use when discussing AI companions — not the phenomenon itself. It measures how often validated keyword patterns appear in Reddit posts, normalized per 1,000 posts to account for community growth.

It does **not** measure sentiment, prevalence, or how many people are actually in relationships with AI. A rising trend line means more people are using that theme's distinctive vocabulary, not that the underlying behavior is necessarily increasing.

## What it tracks

- **27 subreddits** across 4 tiers: general AI (T0), primary companionship (T1), platform-specific (T2), and recovery/dependency (T3)
- **6 keyword themes** — Romance, Sex/ERP, Consciousness, Therapy, Addiction, Rupture
- **~4.0M posts** from 2017 to present, updated daily
- **Keyword validation** — every keyword is manually scored against 100-post samples; only keywords at 80%+ precision are accepted (60-79% may be accepted when false positive patterns are well-defined)

## How the data works

Posts and comments are collected daily via Reddit's public `.json` endpoints. Each post is tagged against validated keyword lists using regex matching with word-boundary constraints. The published chart shows raw keyword counts — there is no AI classification in it. (An LLM verification layer was built and evaluated in May 2026; it is not used in the chart, because it corrects precision while the project's larger accuracy gap is recall — see the [About page](https://myfriendisai.com/about) for the full reasoning.) Trends are normalized to mentions per 1,000 posts.

Historical data (2017 – early 2026) was backfilled from public Reddit archives (PullPush and Arctic Shift). Forward-looking comment collection began March 2026.

**Important limitations:**
- Keyword matching captures distinctive vocabulary, not all discussion of a topic. Themes expressed through everyday language (e.g., romance) are undercounted relative to themes with clinical vocabulary (e.g., addiction).
- Mention rates are **not comparable across themes** — they reflect vocabulary distinctiveness, not phenomenon size.
- Data comes from Reddit only and represents the subset of people who post publicly.

Full methodology: [myfriendisai.com/about](https://myfriendisai.com/about)

## Tech stack

| Layer | Technology |
|-------|-----------|
| Data collection | Python with `requests` |
| Database | SQLite (~4.0M posts) |
| Keyword matching | Regex with word-boundary matching |
| Keyword drift check | Monthly LLM-assisted sample review — monitoring only, not in the chart |
| Frontend | Next.js 16 + TypeScript + Tailwind CSS |
| Charts | Recharts |
| Hosting | Vercel |

## Project structure

```
├── config/              # Tracked communities + keyword theme definitions
├── src/                 # Python collection + keyword-matching pipeline
├── scripts/             # Daily collection, tagging, backfill, JSON export
├── migrations/          # SQLite schema migrations
├── tests/               # Pytest suite for the pipeline
├── data/                # SQLite DB (gitignored) + JSON exports
├── analysis/            # Keyword-validation tooling (scripts + configs)
├── docs/                # Methodology, validation, and data-accuracy reports
└── web/                 # Next.js frontend
    ├── app/             # Pages and components
    └── data/            # JSON data for static site generation
```

## Running locally

**Data pipeline:**
```bash
pip install -r requirements.txt
python scripts/collect_daily.py
```

**Frontend:**
```bash
cd web
npm install
npm run dev
```

## License

MIT
