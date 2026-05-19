# Frontend — myfriendisai.com

Next.js 16 (App Router) + TypeScript + Tailwind + Recharts.

```bash
npm install
npm run dev
```

Reads from `web/data/*.json`, which the daily collection pipeline (in the
project root) writes via `scripts/collect_daily.py`. Deployed to Vercel
automatically on push to `main`.
