"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import type { SubredditSummary, CommunityActivity } from "@/lib/types";
import type { CommunityMetrics } from "@/lib/data";
import { hasCommentAverage } from "@/lib/metrics";
import Sparkline from "./Sparkline";

// Sort keys are the displayed values, not the raw export fields: posts/day is
// a 7-day mean derived at build time, and avg comments is blank for the
// communities whose comment threads this project doesn't collect.
type SortKey =
  | "subscribers"
  | "contributors"
  | "postsPerDay"
  | "avgComments"
  | "avgScore";

type Row = {
  sub: SubredditSummary;
  subscribers: number | null;
  contributors: number | null;
  postsPerDay: number | null;
  avgComments: number | null;
  avgScore: number | null;
  subscribersAsOf: string | null;
  avgScoreAsOf: string | null;
};

function fmt(n: number | null, decimals = 0): string {
  if (n == null) return "—";
  return n.toLocaleString("en-US", { maximumFractionDigits: decimals });
}

const TIER_LABELS: Record<number, string> = {
  0: "General AI",
  1: "Companion",
  2: "Platform",
  3: "Recovery",
  4: "Ambient",
};

const TIER_COLORS: Record<number, string> = {
  0: "bg-slate-400/10 text-slate-300",
  1: "bg-blue-400/10 text-blue-300",
  2: "bg-violet-400/10 text-violet-300",
  3: "bg-red-400/10 text-red-300",
  4: "bg-amber-400/10 text-amber-300",
};

function TierBadge({ tier }: { tier: number | null }) {
  if (tier == null) return null;
  return (
    <span className={`inline-flex text-xs font-medium px-2 py-0.5 rounded-full ${TIER_COLORS[tier] ?? "bg-slate-400/10 text-slate-300"}`}>
      {TIER_LABELS[tier] ?? `Tier ${tier}`}
    </span>
  );
}

function SortButton({
  label,
  sortKey,
  current,
  onSort,
}: {
  label: string;
  sortKey: SortKey;
  current: { key: SortKey; asc: boolean };
  onSort: (key: SortKey) => void;
}) {
  const active = current.key === sortKey;
  return (
    <button
      onClick={() => onSort(sortKey)}
      aria-label={
        active
          ? `Sort by ${label} — currently ${current.asc ? "ascending" : "descending"}`
          : `Sort by ${label}`
      }
      className={`flex items-center gap-1 ml-auto py-2 min-h-11 sm:min-h-0 text-sm sm:text-xs hover:text-[#C8D0DC] transition-colors ${active ? "text-[#F8FAFC]" : "text-[#7E8B9E]"}`}
    >
      {label}
      <span aria-hidden className="text-[11px]">
        {active ? (current.asc ? "↑" : "↓") : "↕"}
      </span>
    </button>
  );
}

export default function CommunitiesTable({
  subreddits,
  activity,
  metrics,
}: {
  subreddits: SubredditSummary[];
  activity: CommunityActivity;
  metrics: CommunityMetrics;
}) {
  const [sort, setSort] = useState<{ key: SortKey; asc: boolean }>({
    key: "subscribers",
    asc: false,
  });
  const [categoryFilter, setCategoryFilter] = useState("All");

  function handleSort(key: SortKey) {
    setSort((prev) => prev.key === key ? { key, asc: !prev.asc } : { key, asc: false });
  }

  const categories = ["All", ...Array.from(new Set(subreddits.map((s) => s.category).filter(Boolean) as string[]))];

  const rows: Row[] = useMemo(
    () =>
      subreddits.map((sub) => ({
        sub,
        subscribers: sub.subscribers,
        contributors: sub.unique_contributors_7d,
        postsPerDay: metrics.postsPerDay7d[sub.subreddit] ?? null,
        avgComments: hasCommentAverage(sub) ? sub.avg_comments_per_post : null,
        avgScore: sub.avg_score_per_post,
        subscribersAsOf: metrics.subscribersAsOf[sub.subreddit] ?? null,
        avgScoreAsOf: metrics.avgScoreAsOf[sub.subreddit] ?? null,
      })),
    [subreddits, metrics],
  );

  const filtered = rows.filter(
    (r) => categoryFilter === "All" || r.sub.category === categoryFilter
  );

  const sorted = [...filtered].sort((a, b) => {
    const av = a[sort.key];
    const bv = b[sort.key];
    // Missing values always sort to the bottom, ascending or descending.
    if (av == null && bv == null) return 0;
    if (av == null) return 1;
    if (bv == null) return -1;
    return sort.asc ? av - bv : bv - av;
  });

  const subscribersLabel = metrics.subscribersRange
    ? `Subscribers (${metrics.subscribersRange})`
    : "Subscribers";
  const avgScoreLabel = metrics.avgScoreRange
    ? `Avg score (${metrics.avgScoreRange})`
    : "Avg score";

  return (
    <div>
      {/* Category filter */}
      <div className="flex gap-2 flex-wrap mb-6">
        {categories.map((cat) => (
          <button
            key={cat}
            onClick={() => setCategoryFilter(cat)}
            className={`text-sm sm:text-xs px-3 py-2 sm:py-1 min-h-11 sm:min-h-0 rounded-full border transition-colors ${
              categoryFilter === cat
                ? "bg-[#1A1D27] text-[#F8FAFC] border-[#2A2D3A]"
                : "border-[#2A2D3A] text-[#9AA7B8] hover:border-[#475569]"
            }`}
          >
            {cat}
          </button>
        ))}
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left">
          <thead>
            <tr className="text-xs uppercase tracking-wide border-b border-[#2A2D3A]">
              <th className="pb-3 pr-4 font-medium text-[#7E8B9E]">Community</th>
              <th className="pb-3 pr-4 font-medium text-[#7E8B9E] hidden sm:table-cell">Activity</th>
              <th className="pb-3 pr-4 font-medium text-[#7E8B9E] hidden sm:table-cell">Tier</th>
              <th className="pb-3 pr-4 font-medium text-right">
                <SortButton label={subscribersLabel} sortKey="subscribers" current={sort} onSort={handleSort} />
              </th>
              <th className="pb-3 pr-4 font-medium text-right">
                <SortButton label="Contributors/wk" sortKey="contributors" current={sort} onSort={handleSort} />
              </th>
              <th className="pb-3 pr-4 font-medium text-right hidden sm:table-cell">
                <SortButton label="Posts/day (7-day avg)" sortKey="postsPerDay" current={sort} onSort={handleSort} />
              </th>
              <th className="pb-3 pr-4 font-medium text-right hidden md:table-cell">
                <SortButton label="Avg comments" sortKey="avgComments" current={sort} onSort={handleSort} />
              </th>
              <th className="pb-3 font-medium text-right hidden md:table-cell">
                <SortButton label={avgScoreLabel} sortKey="avgScore" current={sort} onSort={handleSort} />
              </th>
            </tr>
          </thead>
          <tbody>
            {sorted.map((r) => (
              <tr key={r.sub.subreddit} className="border-t border-[#2A2D3A] hover:bg-[#1A1D27] transition-colors">
                <td className="py-3 pr-4">
                  <Link
                    href={`/communities/${r.sub.subreddit}`}
                    className="font-medium text-sm text-[#F8FAFC] hover:underline"
                  >
                    r/{r.sub.subreddit}
                  </Link>
                  {r.sub.category && (
                    <div className="text-xs text-[#7E8B9E] mt-0.5">{r.sub.category}</div>
                  )}
                </td>
                <td className="py-3 pr-4 hidden sm:table-cell">
                  <Link
                    href={`/communities/${r.sub.subreddit}#activity`}
                    aria-label={`Full activity chart for r/${r.sub.subreddit}`}
                    className="flex items-center min-h-11 -my-3 py-3 opacity-80 hover:opacity-100 transition-opacity"
                  >
                    <Sparkline values={activity.activity[r.sub.subreddit] ?? []} />
                  </Link>
                </td>
                <td className="py-3 pr-4 hidden sm:table-cell">
                  <TierBadge tier={r.sub.tier} />
                </td>
                <td
                  className="py-3 pr-4 text-sm tabular-nums text-right text-[#C8D0DC]"
                  title={r.subscribersAsOf ? `Last collected ${r.subscribersAsOf}` : undefined}
                >
                  {fmt(r.subscribers)}
                </td>
                <td className="py-3 pr-4 text-sm tabular-nums text-right text-[#C8D0DC]">{fmt(r.contributors)}</td>
                <td className="py-3 pr-4 text-sm tabular-nums text-right text-[#C8D0DC] hidden sm:table-cell">{fmt(r.postsPerDay, 1)}</td>
                <td className="py-3 pr-4 text-sm tabular-nums text-right text-[#C8D0DC] hidden md:table-cell">{fmt(r.avgComments, 1)}</td>
                <td
                  className="py-3 text-sm tabular-nums text-right text-[#C8D0DC] hidden md:table-cell"
                  title={r.avgScoreAsOf ? `Last collected ${r.avgScoreAsOf}` : undefined}
                >
                  {fmt(r.avgScore, 0)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {sorted.length === 0 && (
        <p className="text-sm text-[#9AA7B8] py-8 text-center">No communities in this category.</p>
      )}

      <p className="mt-8 text-xs text-[#7E8B9E]">
        <strong>Activity</strong>{" "}— monthly post volume, from each
        community&apos;s first month to the last complete one; each sparkline
        is on its own scale (read the shape, not the height).{" "}
        <strong>Subscribers and Avg score</strong> — Direct (Reddit API),
        frozen at the date shown since Reddit closed unauthenticated access in
        May 2026.{" "}
        <strong>Contributors/wk</strong> — counted from post and comment
        authors in the archive over the past 7 days (comment authors from
        2026-03-12 onward).{" "}
        <strong>Posts/day</strong> — mean of the last 7 complete days; the
        current day is still filling up, so it is left out.{" "}
        <strong>Avg comments</strong> — Derived from the comment threads this
        project collects (companionship communities only; since June 2026
        those are gathered more completely than before, so read it within an
        era, not across June 2026).
      </p>
    </div>
  );
}
