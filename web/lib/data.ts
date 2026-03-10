import path from "path";
import fs from "fs";
import type { SubredditSummary, Snapshot } from "./types";

// Data files live at project root /data/, one level above /web/
const DATA_DIR = path.join(process.cwd(), "..", "data");

export function getSubreddits(): SubredditSummary[] {
  const file = path.join(DATA_DIR, "subreddits.json");
  if (!fs.existsSync(file)) return [];
  return JSON.parse(fs.readFileSync(file, "utf8")) as SubredditSummary[];
}

export function getSnapshots(): Snapshot[] {
  const file = path.join(DATA_DIR, "snapshots.json");
  if (!fs.existsSync(file)) return [];
  return JSON.parse(fs.readFileSync(file, "utf8")) as Snapshot[];
}

export function getSnapshotsForSubreddit(subreddit: string): Snapshot[] {
  return getSnapshots().filter((s) => s.subreddit === subreddit);
}
