import path from "path";
import fs from "fs";
import type { SubredditSummary, Snapshot, CommunityActivity } from "./types";
import { monthRange } from "./metrics";

// Data files are copied into web/data/ for Vercel compatibility.
// The Python collector writes to the project root data/ directory,
// and the copy step (in collect_daily.py or CI) syncs them here.
const DATA_DIR = path.join(process.cwd(), "data");

export function getSubreddits(): SubredditSummary[] {
  const file = path.join(DATA_DIR, "subreddits.json");
  if (!fs.existsSync(file)) return [];
  try {
    return JSON.parse(fs.readFileSync(file, "utf8")) as SubredditSummary[];
  } catch (e) {
    console.error("Failed to parse subreddits.json:", e);
    return [];
  }
}

// Module-level cache: snapshots.json is ~6.5 MB. The build prerenders all 26
// community pages in one process — parsing the file once per process instead
// of once per call keeps SSG fast. The data is read-only.
let _snapshotsCache: Snapshot[] | null = null;

export function getSnapshots(): Snapshot[] {
  if (_snapshotsCache) return _snapshotsCache;
  const file = path.join(DATA_DIR, "snapshots.json");
  if (!fs.existsSync(file)) return [];
  try {
    _snapshotsCache = JSON.parse(fs.readFileSync(file, "utf8")) as Snapshot[];
    return _snapshotsCache;
  } catch (e) {
    console.error("Failed to parse snapshots.json:", e);
    return [];
  }
}

export function getSnapshotsForSubreddit(subreddit: string): Snapshot[] {
  return getSnapshots().filter((s) => s.subreddit === subreddit);
}

// ── Derived per-community metrics ────────────────────────────────────────────
// Two things the daily export can't say for itself, both read off the snapshot
// history at build time:
//
//  · Posts/day. The newest snapshot's `posts_today` is a partial day — the
//    collector runs around midday UTC — so publishing it undercounts every
//    community and reads as 0 for the quiet ones. The table and the stat card
//    show the mean of the last 7 *completed* days instead.
//  · Frozen dates. Subscribers and avg score both come from Reddit's own API,
//    which closed to us in May 2026; each community's last real reading is a
//    fixed date in May or June 2026. Deriving the date rather than hardcoding
//    it keeps the labels honest if collection ever resumes.
const POSTS_PER_DAY_WINDOW = 7;

export type CommunityMetrics = {
  postsPerDay7d: Record<string, number | null>;
  subscribersAsOf: Record<string, string | null>;
  avgScoreAsOf: Record<string, string | null>;
  /** Span of the frozen readings across all communities, e.g. "May–Jun 2026". */
  subscribersRange: string;
  avgScoreRange: string;
};

function lastDateWithValue(rows: Snapshot[], key: keyof Snapshot): string | null {
  for (let i = rows.length - 1; i >= 0; i--) {
    if (typeof rows[i][key] === "number") return rows[i].snapshot_date;
  }
  return null;
}

// Same reasoning as the snapshots cache: the build prerenders 39 community
// pages plus the index, and each one wants the same derived numbers.
let _metricsCache: CommunityMetrics | null = null;

export function getCommunityMetrics(): CommunityMetrics {
  if (_metricsCache) return _metricsCache;
  const snapshots = getSnapshots();
  const latestDate = snapshots.reduce(
    (max, s) => (s.snapshot_date > max ? s.snapshot_date : max),
    "",
  );

  const bySub = new Map<string, Snapshot[]>();
  for (const s of snapshots) {
    const rows = bySub.get(s.subreddit);
    if (rows) rows.push(s);
    else bySub.set(s.subreddit, [s]);
  }

  const postsPerDay7d: Record<string, number | null> = {};
  const subscribersAsOf: Record<string, string | null> = {};
  const avgScoreAsOf: Record<string, string | null> = {};

  for (const [sub, unsorted] of bySub) {
    const rows = [...unsorted].sort((a, b) =>
      a.snapshot_date.localeCompare(b.snapshot_date),
    );
    const completed = rows.filter(
      (r) => r.snapshot_date < latestDate && r.posts_today != null,
    );
    const window = completed.slice(-POSTS_PER_DAY_WINDOW);
    postsPerDay7d[sub] = window.length
      ? window.reduce((sum, r) => sum + (r.posts_today as number), 0) /
        window.length
      : null;
    subscribersAsOf[sub] = lastDateWithValue(rows, "subscribers");
    avgScoreAsOf[sub] = lastDateWithValue(rows, "avg_score_per_post");
  }

  const span = (dates: Record<string, string | null>) => {
    const known = Object.values(dates).filter(Boolean).sort() as string[];
    return known.length
      ? monthRange(known[0], known[known.length - 1])
      : "";
  };

  _metricsCache = {
    postsPerDay7d,
    subscribersAsOf,
    avgScoreAsOf,
    subscribersRange: span(subscribersAsOf),
    avgScoreRange: span(avgScoreAsOf),
  };
  return _metricsCache;
}

export function getCommunityActivity(): CommunityActivity {
  const file = path.join(DATA_DIR, "community_activity.json");
  if (!fs.existsSync(file)) return { months: [], activity: {} };
  try {
    return JSON.parse(fs.readFileSync(file, "utf8")) as CommunityActivity;
  } catch (e) {
    console.error("Failed to parse community_activity.json:", e);
    return { months: [], activity: {} };
  }
}
