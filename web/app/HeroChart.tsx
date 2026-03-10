"use client";

import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";
import type { Snapshot } from "@/lib/types";

type AggRow = {
  date: string;
  total_subscribers: number;
  total_posts: number;
  communities: number;
};

function aggregate(snapshots: Snapshot[]): AggRow[] {
  const byDate = new Map<string, AggRow>();
  for (const s of snapshots) {
    const existing = byDate.get(s.snapshot_date) ?? {
      date: s.snapshot_date,
      total_subscribers: 0,
      total_posts: 0,
      communities: 0,
    };
    existing.total_subscribers += s.subscribers ?? 0;
    existing.total_posts += s.posts_today ?? 0;
    existing.communities += 1;
    byDate.set(s.snapshot_date, existing);
  }
  return Array.from(byDate.values()).sort((a, b) => a.date.localeCompare(b.date));
}

function fmtM(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(0)}K`;
  return String(n);
}

export default function HeroChart({ snapshots }: { snapshots: Snapshot[] }) {
  const data = aggregate(snapshots);

  if (data.length === 0) {
    return (
      <div className="h-48 flex items-center justify-center text-sm text-zinc-400">
        No data yet — run the daily collector to populate charts.
      </div>
    );
  }

  return (
    <div className="mt-12">
      <p className="text-xs text-zinc-400 uppercase tracking-widest mb-1">
        Total subscribers across tracked communities
      </p>
      <p className="text-xs text-zinc-400 mb-4">
        {data.length} day{data.length !== 1 ? "s" : ""} of data ·{" "}
        {data.at(-1)?.communities} communities
      </p>
      <ResponsiveContainer width="100%" height={180}>
        <AreaChart data={data} margin={{ top: 4, right: 0, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id="heroGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#18181b" stopOpacity={0.08} />
              <stop offset="95%" stopColor="#18181b" stopOpacity={0} />
            </linearGradient>
          </defs>
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
            width={44}
            tickFormatter={fmtM}
          />
          <Tooltip
            formatter={(v) => (typeof v === "number" ? fmtM(v) : String(v))}
            labelStyle={{ fontSize: 11 }}
            contentStyle={{ fontSize: 11, borderColor: "#e4e4e7" }}
          />
          <Area
            type="monotone"
            dataKey="total_subscribers"
            stroke="#18181b"
            strokeWidth={1.5}
            fill="url(#heroGrad)"
            dot={data.length === 1}
            name="Total subscribers"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
