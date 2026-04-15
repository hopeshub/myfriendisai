"use client";

import { useEffect, useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";
import type { Snapshot } from "@/lib/types";

function fmt(n: number | null, decimals = 0): string {
  if (n == null) return "—";
  return n.toLocaleString("en-US", { maximumFractionDigits: decimals });
}

function MetricChart({
  data,
  dataKey,
  label,
  color = "#18181b",
  decimals = 0,
}: {
  data: Snapshot[];
  dataKey: keyof Snapshot;
  label: string;
  color?: string;
  decimals?: number;
}) {
  const formatted = data.map((s) => ({
    date: s.snapshot_date,
    value: s[dataKey] as number | null,
  }));

  return (
    <div>
      <p className="text-xs text-zinc-400 uppercase tracking-widest mb-3">{label}</p>
      <ResponsiveContainer width="100%" height={140}>
        <LineChart data={formatted} margin={{ top: 4, right: 4, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f4f4f5" />
          <XAxis
            dataKey="date"
            tick={{ fontSize: 10, fill: "#a1a1aa" }}
            tickLine={false}
            axisLine={false}
          />
          <YAxis
            tick={{ fontSize: 10, fill: "#a1a1aa" }}
            tickLine={false}
            axisLine={false}
            width={50}
            tickFormatter={(v) =>
              v >= 1_000_000
                ? `${(v / 1_000_000).toFixed(1)}M`
                : v >= 1_000
                ? `${(v / 1_000).toFixed(0)}K`
                : String(v)
            }
          />
          <Tooltip
            formatter={(v) =>
              typeof v === "number"
                ? decimals > 0 ? v.toFixed(decimals) : fmt(v)
                : String(v)
            }
            labelStyle={{ fontSize: 11 }}
            contentStyle={{ fontSize: 11, borderColor: "#e4e4e7" }}
          />
          <Line
            type="monotone"
            dataKey="value"
            stroke={color}
            dot={data.length === 1}
            strokeWidth={1.5}
            connectNulls
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

export default function Charts({ subreddit }: { subreddit: string }) {
  const [snapshots, setSnapshots] = useState<Snapshot[] | null>(null);

  useEffect(() => {
    fetch(`/api/snapshots/${subreddit}`)
      .then((r) => r.json())
      .then(setSnapshots)
      .catch(() => setSnapshots([]));
  }, [subreddit]);

  if (snapshots === null) {
    return <p className="text-sm text-zinc-400">Loading…</p>;
  }

  if (snapshots.length === 0) {
    return <p className="text-sm text-zinc-400">No snapshot data yet.</p>;
  }

  const latest = snapshots.at(-1)!;

  return (
    <>
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mt-8 p-6 bg-zinc-50 rounded-xl">
        <div>
          <div className="text-2xl font-semibold tabular-nums">{fmt(latest.subscribers)}</div>
          <div className="text-xs text-zinc-400 mt-0.5">Subscribers</div>
        </div>
        <div>
          <div className="text-2xl font-semibold tabular-nums">{fmt(latest.unique_contributors_7d)}</div>
          <div className="text-xs text-zinc-400 mt-0.5">Contributors / week</div>
        </div>
        <div>
          <div className="text-2xl font-semibold tabular-nums">{fmt(latest.posts_today)}</div>
          <div className="text-xs text-zinc-400 mt-0.5">Posts today</div>
        </div>
        <div>
          <div className="text-2xl font-semibold tabular-nums">{fmt(latest.avg_comments_per_post, 1)}</div>
          <div className="text-xs text-zinc-400 mt-0.5">Avg comments / post</div>
        </div>
      </div>

      <div className="mt-8">
        <p className="text-sm text-zinc-500 mb-1">
          {snapshots.length} day{snapshots.length !== 1 ? "s" : ""} of data
          {snapshots.length === 1 && " — charts will grow as daily collection runs"}
        </p>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-10 mt-8">
          <MetricChart data={snapshots} dataKey="subscribers" label="Subscribers" color="#18181b" />
          <MetricChart data={snapshots} dataKey="unique_contributors_7d" label="Contributors / week (rolling 7d)" color="#e8692a" />
          <MetricChart data={snapshots} dataKey="posts_today" label="Posts / day" color="#3b82f6" />
          <MetricChart data={snapshots} dataKey="avg_comments_per_post" label="Avg comments per post" color="#8b5cf6" decimals={1} />
          <MetricChart data={snapshots} dataKey="avg_score_per_post" label="Avg score per post" color="#10b981" />
        </div>
      </div>
    </>
  );
}
