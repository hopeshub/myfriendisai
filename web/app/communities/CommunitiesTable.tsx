"use client";

import { useState } from "react";
import Link from "next/link";
import type { SubredditSummary } from "@/lib/types";

type SortKey = keyof Pick<
  SubredditSummary,
  "subscribers" | "posts_today" | "avg_comments_per_post" | "avg_score_per_post" | "unique_authors"
>;

function fmt(n: number | null, decimals = 0): string {
  if (n == null) return "—";
  return n.toLocaleString("en-US", { maximumFractionDigits: decimals });
}

const TIER_LABELS: Record<number, string> = {
  0: "Control",
  1: "Companion",
  2: "Platform",
  3: "Recovery",
};

const TIER_COLORS: Record<number, string> = {
  0: "bg-zinc-100 text-zinc-500",
  1: "bg-blue-50 text-blue-600",
  2: "bg-violet-50 text-violet-600",
  3: "bg-red-50 text-red-600",
};

function TierBadge({ tier }: { tier: number | null }) {
  if (tier == null) return null;
  return (
    <span className={`inline-flex text-xs font-medium px-2 py-0.5 rounded-full ${TIER_COLORS[tier] ?? "bg-zinc-100 text-zinc-500"}`}>
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
      className={`flex items-center gap-1 ml-auto hover:text-zinc-700 transition-colors ${active ? "text-zinc-800" : "text-zinc-400"}`}
    >
      {label}
      <span className="text-[10px]">{active ? (current.asc ? "↑" : "↓") : "↕"}</span>
    </button>
  );
}

const CATEGORIES = ["All", "Foundation / Control", "Primary Companionship", "Platform-Specific", "Recovery & Dependency", "Adjacent"];

export default function CommunitiesTable({ subreddits }: { subreddits: SubredditSummary[] }) {
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
    const av = a[sort.key] ?? -Infinity;
    const bv = b[sort.key] ?? -Infinity;
    return sort.asc ? (av as number) - (bv as number) : (bv as number) - (av as number);
  });

  return (
    <div>
      {/* Category filter */}
      <div className="flex gap-2 flex-wrap mb-6">
        {categories.map((cat) => (
          <button
            key={cat}
            onClick={() => setCategoryFilter(cat)}
            className={`text-xs px-3 py-1 rounded-full border transition-colors ${
              categoryFilter === cat
                ? "bg-zinc-900 text-white border-zinc-900"
                : "border-zinc-200 text-zinc-500 hover:border-zinc-400"
            }`}
          >
            {cat}
          </button>
        ))}
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left">
          <thead>
            <tr className="text-xs uppercase tracking-wide border-b border-zinc-200">
              <th className="pb-3 pr-4 font-medium text-zinc-400">Community</th>
              <th className="pb-3 pr-4 font-medium text-zinc-400 hidden sm:table-cell">Tier</th>
              <th className="pb-3 pr-4 font-medium text-right">
                <SortButton label="Subscribers" sortKey="subscribers" current={sort} onSort={handleSort} />
              </th>
              <th className="pb-3 pr-4 font-medium text-right">
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
              <tr key={s.subreddit} className="border-t border-zinc-100 hover:bg-zinc-50 transition-colors">
                <td className="py-3 pr-4">
                  <Link
                    href={`/communities/${s.subreddit}`}
                    className="font-medium text-sm hover:underline"
                  >
                    r/{s.subreddit}
                  </Link>
                  {s.category && (
                    <div className="text-xs text-zinc-400 mt-0.5">{s.category}</div>
                  )}
                </td>
                <td className="py-3 pr-4 hidden sm:table-cell">
                  <TierBadge tier={s.tier} />
                </td>
                <td className="py-3 pr-4 text-sm tabular-nums text-right">{fmt(s.subscribers)}</td>
                <td className="py-3 pr-4 text-sm tabular-nums text-right">{fmt(s.posts_today)}</td>
                <td className="py-3 pr-4 text-sm tabular-nums text-right hidden md:table-cell">{fmt(s.avg_comments_per_post, 1)}</td>
                <td className="py-3 text-sm tabular-nums text-right hidden md:table-cell">{fmt(s.avg_score_per_post, 0)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {sorted.length === 0 && (
        <p className="text-sm text-zinc-400 py-8 text-center">No communities in this category.</p>
      )}

      <p className="mt-8 text-xs text-zinc-400">
        <strong>Subscribers</strong> — Direct.{" "}
        <strong>Posts/day</strong> — Inferred (posts in past 24h).{" "}
        <strong>Avg comments / Avg score</strong> — Inferred (sample of 100 posts).
      </p>
    </div>
  );
}
