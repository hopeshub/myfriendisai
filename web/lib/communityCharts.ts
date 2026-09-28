// ── Per-community chart data, aggregated at build time ──────────────────────
// The community page's charts only ever draw monthly means, and its stat cards
// only ever show a handful of "latest known" figures. Shipping the full daily
// snapshot history (~1,300 rows × 11 fields) into the page props made every
// /communities/[subreddit] page ~400 KB; this reduces it server-side to exactly
// what the client renders. No file IO — pure functions over the snapshot rows.
import type { Snapshot } from "./types";
import { hasCommentAverage } from "./metrics";

export type MonthPoint = { date: string; value: number };

export type CommunityChartData = {
  /** Latest non-null subscriber count (Reddit-only; frozen since mid-2026). */
  subscribers: number | null;
  /** Latest non-null 7-day contributor count. */
  contributors: number | null;
  /** Latest measured comment average, or null (see lastCommentAverage). */
  avgComments: number | null;
  /** Last month ("YYYY-MM") the page has any snapshot for. */
  dataEndMonth: string;
  contributorsMonthly: MonthPoint[];
  commentsMonthly: MonthPoint[];
  scoreMonthly: MonthPoint[];
};

// One metric, aggregated to a monthly mean. The snapshot history runs daily
// across 3+ years — plotting ~1,200 raw daily points in a small panel is an
// unreadable scribble, so each month collapses to the mean of its days.
// Months with no reading produce no point at all, so a metric that stopped
// being collected ends its line where it stopped instead of running on.
function monthlyMean(
  data: Snapshot[],
  value: (s: Snapshot) => number | null,
): MonthPoint[] {
  const buckets: Record<string, { sum: number; n: number }> = {};
  for (const s of data) {
    const v = value(s);
    if (v == null) continue;
    const m = s.snapshot_date.slice(0, 7);
    if (!buckets[m]) buckets[m] = { sum: 0, n: 0 };
    buckets[m].sum += v;
    buckets[m].n += 1;
  }
  return Object.keys(buckets)
    .sort()
    .map((m) => ({ date: m + "-01", value: buckets[m].sum / buckets[m].n }));
}

/** Returns null when the community has no snapshot rows at all. */
export function buildCommunityChartData(
  snapshots: Snapshot[],
): CommunityChartData | null {
  if (snapshots.length === 0) return null;

  // Per-field latest non-null: archive-sourced snapshot rows legitimately
  // lack Reddit-only observables (subscribers; comment averages mature with
  // a 6-day lag), so each card shows its most recent known value rather
  // than blanking whenever the newest row has a hole.
  const lastKnown = (key: keyof Snapshot): number | null => {
    for (let i = snapshots.length - 1; i >= 0; i--) {
      const v = snapshots[i][key];
      if (typeof v === "number") return v;
    }
    return null;
  };

  // Avg comments: same walk-back for the collection lag, but it stops at the
  // newest row that reported anything at all. The collector writes a 0 for
  // communities whose comment threads it never gathers, and that 0 means "no
  // reading" — publishing it, or reaching past it for a months-old figure
  // from a different collection regime, would both be wrong.
  const lastCommentAverage = (): number | null => {
    for (let i = snapshots.length - 1; i >= 0; i--) {
      if (snapshots[i].avg_comments_per_post == null) continue;
      return hasCommentAverage(snapshots[i])
        ? snapshots[i].avg_comments_per_post
        : null;
    }
    return null;
  };

  const dataEndMonth = snapshots
    .reduce((max, s) => (s.snapshot_date > max ? s.snapshot_date : max), "")
    .slice(0, 7);

  return {
    subscribers: lastKnown("subscribers"),
    contributors: lastKnown("unique_contributors_7d"),
    avgComments: lastCommentAverage(),
    dataEndMonth,
    contributorsMonthly: monthlyMean(snapshots, (s) => s.unique_contributors_7d),
    commentsMonthly: monthlyMean(snapshots, (s) =>
      hasCommentAverage(s) ? s.avg_comments_per_post : null,
    ),
    scoreMonthly: monthlyMean(snapshots, (s) => s.avg_score_per_post),
  };
}
