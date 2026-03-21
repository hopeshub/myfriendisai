# My Friend Is AI

A research dashboard tracking how people talk about AI companionship across Reddit. Visualizes engagement trends across 27 subreddits using daily snapshots and keyword analysis.

**Live site:** [myfriendisai.com](https://myfriendisai.com)

## What it tracks

- **27 subreddits** across 4 tiers: general AI (T0), primary companionship (T1), platform-specific (T2), and recovery/dependency (T3)
- **6 keyword themes** — Romance, Sex/ERP, Consciousness, Therapy, Addiction, Rupture
- **~3.8M posts** from January 2023 to present, updated daily
- **Keyword validation** — every keyword is manually scored against 100-post samples at 80%+ precision

## How the data works

Posts and comments are collected daily via Reddit's public `.json` endpoints (no API credentials needed). Each post is tagged against validated keyword lists using regex matching. Trends are normalized to mentions per 1,000 posts to account for community growth.

Historical data from January 2023 through March 2026 was backfilled from PullPush Reddit archives. Forward-looking comment collection began March 2026.

Full methodology is on the [About page](https://myfriendisai.com/about).

## Tech stack

| Layer | Technology |
|-------|-----------|
| Data collection | Python 3.11+ with `requests` |
| Database | SQLite (~22GB, 3.8M posts) |
| Keyword matching | Regex with word-boundary matching |
| Frontend | Next.js 16 (App Router) + TypeScript + Tailwind CSS |
| Charts | Recharts |
| Hosting | Vercel |
| Domain | myfriendisai.com |

## Project structure

```
├── config/              # Community list + keyword definitions
├── src/                 # Python collection + matching pipeline
├── scripts/             # Daily collection, tagging, backfill, export
├── data/                # SQLite DB + JSON exports (gitignored DB)
├── web/                 # Next.js frontend
│   ├── app/             # Pages and components
│   └── data/            # JSON data for static site generation
├── migrations/          # Database schema migrations
└── docs/archive/        # Historical specs and validation records
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
