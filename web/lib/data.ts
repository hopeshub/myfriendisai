import path from "path";
import fs from "fs";
import type { SubredditSummary, Snapshot, CommunityActivity } from "./types";

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
