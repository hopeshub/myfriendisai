"use client";

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

function fmt(n: number | null): string {
  if (n == null) return "—";
  return n.toLocaleString("en-US");
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

export default function Charts({ snapshots }: { snapshots: Snapshot[] }) {
  if (snapshots.length === 0) {
    return <p className="text-sm text-zinc-400">No snapshot data yet.</p>;
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-10 mt-8">
      <MetricChart
        data={snapshots}
        dataKey="subscribers"
        label="Subscribers"
        color="#18181b"
      />
      <MetricChart
        data={snapshots}
        dataKey="posts_today"
        label="Posts / day"
        color="#3b82f6"
      />
      <MetricChart
        data={snapshots}
        dataKey="avg_comments_per_post"
        label="Avg comments per post"
        color="#8b5cf6"
        decimals={1}
      />
      <MetricChart
        data={snapshots}
        dataKey="avg_score_per_post"
        label="Avg score per post"
        color="#10b981"
        decimals={0}
      />
    </div>
  );
}
