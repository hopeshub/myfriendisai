"use client";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts";
import MeasuredChart from "@/app/MeasuredChart";
import type { Snapshot } from "@/lib/types";
import { usePrefersReducedMotion } from "@/lib/usePrefersReducedMotion";

const MONTH_NAMES = [
  "Jan", "Feb", "Mar", "Apr", "May", "Jun",
  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
];

function fmt(n: number | null, decimals = 0): string {
  if (n == null) return "—";
  return n.toLocaleString("en-US", { maximumFractionDigits: decimals });
}

// Same tick formatter as the post-volume and community-activity charts. The
// old one rounded to whole thousands, so a tick at 1,500 was labelled "2K".
function fmtCount(n: number): string {
  if (n >= 1000) return `${(n / 1000).toFixed(n >= 10000 ? 0 : 1)}k`;
  return String(n);
}

// A snapshot taken from the archive carries no comment sample: the exporter
// writes 0 rather than null for both fields. Treat that pair as "not
// collected", so the line crops instead of falling to a fabricated zero.
function hasCommentData(s: Snapshot): boolean {
  return !(s.avg_comments_per_post === 0 && s.unique_comment_authors_7d === 0);
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
  // This chart has no time-range/scope toggle, so it animates exactly once on
  // mount. Gated on reduced-motion since Recharts animation is JS-driven.
  const reducedMotion = usePrefersReducedMotion();

  const buckets: Record<string, { sum: number; n: number }> = {};
  for (const s of data) {
    const v = s[dataKey] as number | null;
    if (v == null) continue;
    if (dataKey === "avg_comments_per_post" && !hasCommentData(s)) continue;
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
      <h2 className="text-xs text-[#7E8B9E] uppercase tracking-widest mb-3">
        {label}
      </h2>
      {monthly.length === 0 ? (
        <div className="h-[140px] flex items-center text-sm text-[#7E8B9E]">
          No data yet.
        </div>
      ) : (
        <MeasuredChart
          style={{ height: 140 }}
          role="img"
          ariaLabel={`Line chart: ${label}, monthly average across the collected history.`}
        >
        {({ width, height }) => (
          <LineChart
            width={width}
            height={height}
            data={monthly}
            margin={{ top: 4, right: 4, left: 0, bottom: 0 }}
            accessibilityLayer={false}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#2A2D3A" />
            <XAxis
              dataKey="date"
              tickFormatter={fmtTick}
              tick={{ fontSize: 11, fill: "#7E8B9E" }}
              tickLine={false}
              axisLine={false}
              minTickGap={48}
              tickMargin={8}
            />
            <YAxis
              tick={{ fontSize: 11, fill: "#7E8B9E" }}
              tickLine={false}
              axisLine={false}
              width={50}
              tickCount={5}
              tickFormatter={fmtCount}
            />
            <Tooltip
              animationDuration={140}
              animationEasing="ease-out"
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
              activeDot={{ r: 4, fill: color, stroke: color }}
              strokeWidth={1.5}
              isAnimationActive={!reducedMotion}
              animationDuration={700}
              animationEasing="ease-out"
            />
          </LineChart>
        )}
        </MeasuredChart>
      )}
    </div>
  );
}

export default function Charts({ snapshots }: { snapshots: Snapshot[] }) {
  if (snapshots.length === 0) {
    return <p className="text-sm text-[#9AA7B8]">No snapshot data yet.</p>;
  }

  // Per-field latest non-null: archive-sourced snapshot rows legitimately
  // lack Reddit-only observables (subscribers; comment averages mature with
  // a 6-day lag), so each card shows its most recent known value rather
  // than blanking whenever the newest row has a hole.
  const lastKnown = (key: keyof Snapshot): number | null => {
    for (let i = snapshots.length - 1; i >= 0; i--) {
      if (key === "avg_comments_per_post" && !hasCommentData(snapshots[i])) continue;
      const v = snapshots[i][key];
      if (typeof v === "number") return v;
    }
    return null;
  };

  // Subscriber collection stopped on a different day for different
  // communities, so the card names this one's own last snapshot rather than a
  // hardcoded month.
  const lastSubscriberDate = (): string | null => {
    for (let i = snapshots.length - 1; i >= 0; i--) {
      if (typeof snapshots[i].subscribers === "number") {
        return snapshots[i].snapshot_date;
      }
    }
    return null;
  };
  const subsDate = lastSubscriberDate();
  const subsLabel = subsDate
    ? `Subscribers (${MONTH_NAMES[Number(subsDate.slice(5, 7)) - 1]} ${subsDate.slice(0, 4)})`
    : "Subscribers";

  return (
    <>
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mt-8 p-6 bg-[#1A1D27] rounded-xl">
        <div>
          <div className="text-2xl font-semibold tabular-nums text-[#F8FAFC]">{fmt(lastKnown("subscribers"))}</div>
          <div className="text-xs text-[#9AA7B8] mt-0.5">{subsLabel}</div>
        </div>
        <div>
          <div className="text-2xl font-semibold tabular-nums text-[#F8FAFC]">{fmt(lastKnown("unique_contributors_7d"))}</div>
          <div className="text-xs text-[#9AA7B8] mt-0.5">Contributors / week</div>
        </div>
        <div>
          <div className="text-2xl font-semibold tabular-nums text-[#F8FAFC]">{fmt(lastKnown("posts_today"))}</div>
          <div className="text-xs text-[#9AA7B8] mt-0.5">Posts / day</div>
        </div>
        <div>
          <div className="text-2xl font-semibold tabular-nums text-[#F8FAFC]">{fmt(lastKnown("avg_comments_per_post"), 1)}</div>
          <div className="text-xs text-[#9AA7B8] mt-0.5">Avg comments / post</div>
        </div>
      </div>

      <div className="mt-10">
        <p className="text-xs text-[#7E8B9E] mb-6">
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
