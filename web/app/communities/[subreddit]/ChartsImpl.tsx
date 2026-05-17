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

const MONTH_NAMES = [
  "Jan", "Feb", "Mar", "Apr", "May", "Jun",
  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
];

function fmt(n: number | null, decimals = 0): string {
  if (n == null) return "—";
  return n.toLocaleString("en-US", { maximumFractionDigits: decimals });
}

function fmtTick(d: string): string {
  const dt = new Date(d + "T00:00:00Z");
  return `${MONTH_NAMES[dt.getUTCMonth()]} '${String(dt.getUTCFullYear()).slice(2)}`;
}

function fmtTooltipLabel(d: unknown): string {
  if (typeof d !== "string") return "";
  const dt = new Date(d + "T00:00:00Z");
  return `${MONTH_NAMES[dt.getUTCMonth()]} ${dt.getUTCFullYear()}`;
}

// One metric, aggregated to a monthly mean. The snapshot history runs daily
// across 3+ years — plotting ~1,200 raw daily points in a small panel is an
// unreadable scribble, so each month collapses to the mean of its days.
function MetricChart({
  data,
  dataKey,
  label,
  color = "#7C9CD0",
  decimals = 0,
}: {
  data: Snapshot[];
  dataKey: keyof Snapshot;
  label: string;
  color?: string;
  decimals?: number;
}) {
  const buckets: Record<string, { sum: number; n: number }> = {};
  for (const s of data) {
    const v = s[dataKey] as number | null;
    if (v == null) continue;
    const m = s.snapshot_date.slice(0, 7);
    if (!buckets[m]) buckets[m] = { sum: 0, n: 0 };
    buckets[m].sum += v;
    buckets[m].n += 1;
  }
  const monthly = Object.keys(buckets)
    .sort()
    .map((m) => ({ date: m + "-01", value: buckets[m].sum / buckets[m].n }));

  return (
    <div>
      <p className="text-xs text-[#6B7689] uppercase tracking-widest mb-3">
        {label}
      </p>
      {monthly.length === 0 ? (
        <div className="h-[140px] flex items-center text-sm text-[#6B7689]">
          No data yet.
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={140}>
          <LineChart data={monthly} margin={{ top: 4, right: 4, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#2A2D3A" />
            <XAxis
              dataKey="date"
              tickFormatter={fmtTick}
              tick={{ fontSize: 11, fill: "#6B7689" }}
              tickLine={false}
              axisLine={false}
              minTickGap={48}
              tickMargin={8}
            />
            <YAxis
              tick={{ fontSize: 11, fill: "#6B7689" }}
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
              labelFormatter={fmtTooltipLabel}
              formatter={(v) =>
                typeof v === "number"
                  ? decimals > 0 ? v.toFixed(decimals) : fmt(v)
                  : String(v)
              }
              labelStyle={{ fontSize: 11, color: "#9AA7B8" }}
              itemStyle={{ color: "#F1F4F8" }}
              contentStyle={{
                fontSize: 11,
                backgroundColor: "#0F1117",
                borderColor: "#2A2D3A",
                borderRadius: 6,
              }}
            />
            <Line
              type="monotone"
              name={label}
              dataKey="value"
              stroke={color}
              dot={monthly.length === 1}
              strokeWidth={1.5}
            />
          </LineChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}

export default function Charts({ snapshots }: { snapshots: Snapshot[] }) {
  if (snapshots.length === 0) {
    return <p className="text-sm text-[#9AA7B8]">No snapshot data yet.</p>;
  }

  const latest = snapshots.at(-1)!;

  return (
    <>
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mt-8 p-6 bg-[#1A1D27] rounded-xl">
        <div>
          <div className="text-2xl font-semibold tabular-nums text-[#F8FAFC]">{fmt(latest.subscribers)}</div>
          <div className="text-xs text-[#9AA7B8] mt-0.5">Subscribers</div>
        </div>
        <div>
          <div className="text-2xl font-semibold tabular-nums text-[#F8FAFC]">{fmt(latest.unique_contributors_7d)}</div>
          <div className="text-xs text-[#9AA7B8] mt-0.5">Contributors / week</div>
        </div>
        <div>
          <div className="text-2xl font-semibold tabular-nums text-[#F8FAFC]">{fmt(latest.posts_today)}</div>
          <div className="text-xs text-[#9AA7B8] mt-0.5">Posts / day</div>
        </div>
        <div>
          <div className="text-2xl font-semibold tabular-nums text-[#F8FAFC]">{fmt(latest.avg_comments_per_post, 1)}</div>
          <div className="text-xs text-[#9AA7B8] mt-0.5">Avg comments / post</div>
        </div>
      </div>

      <div className="mt-10">
        <p className="text-xs text-[#6B7689] mb-6">
          Monthly averages across the collected history — the current figures
          are in the cards above.
        </p>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <MetricChart data={snapshots} dataKey="unique_contributors_7d" label="Contributors / week" color="#e8692a" />
          <MetricChart data={snapshots} dataKey="avg_comments_per_post" label="Avg comments per post" color="#8b5cf6" decimals={1} />
          <MetricChart data={snapshots} dataKey="avg_score_per_post" label="Avg score per post" color="#10b981" />
        </div>
      </div>
    </>
  );
}
