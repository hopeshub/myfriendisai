"use client";

import { useState } from "react";
import Link from "next/link";
import type { SubredditSummary, CommunityActivity } from "@/lib/types";
import Sparkline from "./Sparkline";

type SortKey = keyof Pick<
  SubredditSummary,
  "subscribers" | "posts_today" | "avg_comments_per_post" | "avg_score_per_post" | "unique_authors" | "unique_contributors_7d"
>;

function fmt(n: number | null, decimals = 0): string {
  if (n == null) return "—";
  return n.toLocaleString("en-US", { maximumFractionDigits: decimals });
}

const TIER_LABELS: Record<number, string> = {
  0: "General AI",
  1: "Companion",
  2: "Platform",
  3: "Recovery",
};

const TIER_COLORS: Record<number, string> = {
  0: "bg-slate-400/10 text-slate-300",
  1: "bg-blue-400/10 text-blue-300",
  2: "bg-violet-400/10 text-violet-300",
  3: "bg-red-400/10 text-red-300",
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
      className={`flex items-center gap-1 ml-auto py-2 text-sm sm:text-xs hover:text-[#C8D0DC] transition-colors ${active ? "text-[#F8FAFC]" : "text-[#6B7689]"}`}
    >
      {label}
      <span className="text-[11px]">{active ? (current.asc ? "↑" : "↓") : "↕"}</span>
    </button>
  );
}

export default function CommunitiesTable({
  subreddits,
  activity,
}: {
  subreddits: SubredditSummary[];
  activity: CommunityActivity;
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

  const filtered = subreddits.filter(
    (s) => categoryFilter === "All" || s.category === categoryFilter
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
              <th className="pb-3 pr-4 font-medium text-[#6B7689]">Community</th>
              <th className="pb-3 pr-4 font-medium text-[#6B7689] hidden sm:table-cell">Activity</th>
              <th className="pb-3 pr-4 font-medium text-[#6B7689] hidden sm:table-cell">Tier</th>
              <th className="pb-3 pr-4 font-medium text-right">
                <SortButton label="Subscribers" sortKey="subscribers" current={sort} onSort={handleSort} />
              </th>
              <th className="pb-3 pr-4 font-medium text-right">
                <SortButton label="Contributors/wk" sortKey="unique_contributors_7d" current={sort} onSort={handleSort} />
              </th>
              <th className="pb-3 pr-4 font-medium text-right hidden sm:table-cell">
                <SortButton label="Posts/day" sortKey="posts_today" current={sort} onSort={handleSort} />
              </th>
              <th className="pb-3 pr-4 font-medium text-right hidden md:table-cell">
                <SortButton label="Avg comments" sortKey="avg_comments_per_post" current={sort} onSort={handleSort} />
              </th>
              <th className="pb-3 font-medium text-right hidden md:table-cell">
                <SortButton label="Avg score" sortKey="avg_score_per_post" current={sort} onSort={handleSort} />
              </th>
            </tr>
          </thead>
          <tbody>
            {sorted.map((s) => (
              <tr key={s.subreddit} className="border-t border-[#2A2D3A] hover:bg-[#1A1D27] transition-colors">
                <td className="py-3 pr-4">
                  <Link
                    href={`/communities/${s.subreddit}`}
                    className="font-medium text-sm text-[#F8FAFC] hover:underline"
                  >
                    r/{s.subreddit}
                  </Link>
                  {s.category && (
                    <div className="text-xs text-[#6B7689] mt-0.5">{s.category}</div>
                  )}
                </td>
                <td className="py-3 pr-4 hidden sm:table-cell">
                  <Link
                    href={`/communities/${s.subreddit}#activity`}
                    aria-label={`Full activity chart for r/${s.subreddit}`}
                    className="flex items-center min-h-11 -my-3 py-3 opacity-80 hover:opacity-100 transition-opacity"
                  >
                    <Sparkline values={activity.activity[s.subreddit] ?? []} />
                  </Link>
                </td>
                <td className="py-3 pr-4 hidden sm:table-cell">
                  <TierBadge tier={s.tier} />
                </td>
                <td className="py-3 pr-4 text-sm tabular-nums text-right text-[#C8D0DC]">{fmt(s.subscribers)}</td>
                <td className="py-3 pr-4 text-sm tabular-nums text-right text-[#C8D0DC]">{fmt(s.unique_contributors_7d)}</td>
                <td className="py-3 pr-4 text-sm tabular-nums text-right text-[#C8D0DC] hidden sm:table-cell">{fmt(s.posts_today)}</td>
                <td className="py-3 pr-4 text-sm tabular-nums text-right text-[#C8D0DC] hidden md:table-cell">{fmt(s.avg_comments_per_post, 1)}</td>
                <td className="py-3 text-sm tabular-nums text-right text-[#C8D0DC] hidden md:table-cell">{fmt(s.avg_score_per_post, 0)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {sorted.length === 0 && (
        <p className="text-sm text-[#9AA7B8] py-8 text-center">No communities in this category.</p>
      )}

      <p className="mt-8 text-xs text-[#6B7689]">
        <strong>Activity</strong> — monthly post volume, Jan 2023 to the last
        complete month; each sparkline is on its own scale (read the shape, not
        the height).{" "}
        <strong>Subscribers</strong> — Direct (Reddit API).{" "}
        <strong>Contributors/wk</strong> — Derived (distinct post + comment authors over the
        past 7 days; comment authors counted from 2026-03-10 onward).{" "}
        <strong>Posts/day</strong> — Inferred (posts in past 24h).{" "}
        <strong>Avg comments / Avg score</strong> — Inferred (sample of 100 posts).
      </p>
    </div>
  );
}
