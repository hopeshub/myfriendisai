import path from "path";
import fs from "fs";
import type { SubredditSummary, Snapshot } from "./types";

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

export function getSnapshots(): Snapshot[] {
  const file = path.join(DATA_DIR, "snapshots.json");
  if (!fs.existsSync(file)) return [];
  try {
    return JSON.parse(fs.readFileSync(file, "utf8")) as Snapshot[];
  } catch (e) {
    console.error("Failed to parse snapshots.json:", e);
    return [];
  }
}

export function getSnapshotsForSubreddit(subreddit: string): Snapshot[] {
  return getSnapshots().filter((s) => s.subreddit === subreddit);
}
