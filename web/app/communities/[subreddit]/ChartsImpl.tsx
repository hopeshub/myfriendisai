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
import { hasCommentAverage, monthLabel, monthRange } from "@/lib/metrics";
import { usePrefersReducedMotion } from "@/lib/usePrefersReducedMotion";

const MONTH_NAMES = [
  "Jan", "Feb", "Mar", "Apr", "May", "Jun",
  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
];

// Below this many months a line is a couple of dots joined by a diagonal
// across an otherwise empty axis, which reads as a trend that isn't there.
const MIN_MONTHS_TO_CHART = 3;

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

type MonthPoint = { date: string; value: number };

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

function MetricChart({
  monthly,
  label,
  dataEndMonth,
  color = "#7C9CD0",
  decimals = 0,
}: {
  monthly: MonthPoint[];
  label: string;
  /** Last month the page has any data for — a metric ending earlier says so. */
  dataEndMonth: string;
  color?: string;
  decimals?: number;
}) {
  // This chart has no time-range/scope toggle, so it animates exactly once on
  // mount. Gated on reduced-motion since Recharts animation is JS-driven.
  const reducedMotion = usePrefersReducedMotion();

  const firstMonth = monthly[0]?.date.slice(0, 7) ?? "";
  const lastMonth = monthly[monthly.length - 1]?.date.slice(0, 7) ?? "";
  const endsEarly = lastMonth !== "" && lastMonth < dataEndMonth;

  return (
    <div>
      <p className="text-xs text-[#7E8B9E] uppercase tracking-widest mb-3">
        {label}
      </p>
      {monthly.length === 0 ? (
        <p className="text-sm text-[#7E8B9E]">Not collected for this community.</p>
      ) : monthly.length < MIN_MONTHS_TO_CHART ? (
        <p className="text-sm text-[#7E8B9E]">
          Not enough data to chart — collected only{" "}
          {monthRange(firstMonth + "-01", lastMonth + "-01")}.
        </p>
      ) : (
        <>
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
                tickFormatter={(v) =>
                  v >= 1_000_000
                    ? `${Number((v / 1_000_000).toFixed(1))}M`
                    : v >= 1_000
                    ? `${Number((v / 1_000).toFixed(1))}K`
                    : String(v)
                }
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
                dot={false}
                activeDot={{ r: 4, fill: color, stroke: color }}
                strokeWidth={1.5}
                isAnimationActive={!reducedMotion}
                animationDuration={700}
                animationEasing="ease-out"
              />
            </LineChart>
          )}
          </MeasuredChart>
          {endsEarly && (
            <p className="text-xs text-[#7E8B9E] mt-2">
              Ends {monthLabel(lastMonth)} — the last month this was collected.
            </p>
          )}
        </>
      )}
    </div>
  );
}

export default function Charts({
  snapshots,
  postsPerDay,
  subscribersAsOf,
}: {
  snapshots: Snapshot[];
  /** Mean posts per day over the last 7 complete days, derived at build time. */
  postsPerDay: number | null;
  subscribersAsOf: string | null;
}) {
  if (snapshots.length === 0) {
    return <p className="text-sm text-[#9AA7B8]">No snapshot data yet.</p>;
  }

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

  const dataEndMonth = snapshots.reduce(
    (max, s) => (s.snapshot_date > max ? s.snapshot_date : max),
    "",
  ).slice(0, 7);

  return (
    <>
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mt-8 p-6 bg-[#1A1D27] rounded-xl">
        <div>
          <div className="text-2xl font-semibold tabular-nums text-[#F8FAFC]">{fmt(lastKnown("subscribers"))}</div>
          <div className="text-xs text-[#9AA7B8] mt-0.5">Subscribers</div>
          {subscribersAsOf && (
            <div className="text-xs text-[#7E8B9E] mt-0.5 whitespace-nowrap">
              last collected {subscribersAsOf}
            </div>
          )}
        </div>
        <div>
          <div className="text-2xl font-semibold tabular-nums text-[#F8FAFC]">{fmt(lastKnown("unique_contributors_7d"))}</div>
          <div className="text-xs text-[#9AA7B8] mt-0.5">Contributors / week</div>
        </div>
        <div>
          <div className="text-2xl font-semibold tabular-nums text-[#F8FAFC]">{fmt(postsPerDay, 1)}</div>
          <div className="text-xs text-[#9AA7B8] mt-0.5">Posts / day (7-day avg)</div>
        </div>
        <div>
          <div className="text-2xl font-semibold tabular-nums text-[#F8FAFC]">{fmt(lastCommentAverage(), 1)}</div>
          <div className="text-xs text-[#9AA7B8] mt-0.5">Avg comments / post</div>
        </div>
      </div>

      <div className="mt-10">
        <p className="text-xs text-[#7E8B9E] mb-6">
          Monthly averages across the collected history — the current figures
          are in the cards above.
        </p>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <MetricChart
            monthly={monthlyMean(snapshots, (s) => s.unique_contributors_7d)}
            label="Contributors / week"
            dataEndMonth={dataEndMonth}
            color="#e8692a"
          />
          <MetricChart
            monthly={monthlyMean(snapshots, (s) =>
              hasCommentAverage(s) ? s.avg_comments_per_post : null,
            )}
            label="Avg comments per post"
            dataEndMonth={dataEndMonth}
            color="#8b5cf6"
            decimals={1}
          />
          <MetricChart
            monthly={monthlyMean(snapshots, (s) => s.avg_score_per_post)}
            label="Avg score per post"
            dataEndMonth={dataEndMonth}
            color="#10b981"
          />
        </div>
      </div>
    </>
  );
}
