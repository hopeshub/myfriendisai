"use client";

import { useMemo, useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
  CartesianGrid,
} from "recharts";
import type { Snapshot, SubredditSummary } from "@/lib/types";
import { EVENTS } from "@/lib/events";
import { LENSES } from "@/lib/lenses";

type TimeRange = "30D" | "90D" | "1Y" | "ALL";

const TIME_RANGES: TimeRange[] = ["30D", "90D", "1Y", "ALL"];

function getDaysForRange(range: TimeRange): number | null {
  switch (range) {
    case "30D": return 30;
    case "90D": return 90;
    case "1Y": return 365;
    case "ALL": return null;
  }
}

function formatDate(dateStr: string): string {
  const d = new Date(dateStr + "T00:00:00");
  return d.toLocaleDateString("en-US", { month: "short", day: "numeric" });
}

function formatNumber(val: number): string {
  if (val >= 1_000_000) return `${(val / 1_000_000).toFixed(1)}M`;
  if (val >= 1_000) return `${(val / 1_000).toFixed(0)}K`;
  return val.toFixed(0);
}

type Props = {
  snapshots: Snapshot[];
  subreddits: SubredditSummary[];
};

export default function HeroChart({ snapshots, subreddits }: Props) {
  const [timeRange, setTimeRange] = useState<TimeRange>("90D");
  const [activeLens, setActiveLens] = useState("growth");

  const tierMap = useMemo(() => {
    const map: Record<string, number> = {};
    subreddits.forEach((s) => {
      if (s.tier !== null) map[s.subreddit] = s.tier;
    });
    return map;
  }, [subreddits]);

  const chartData = useMemo(() => {
    const byDate: Record<
      string,
      { companionship_activity: number; control_activity: number }
    > = {};

    for (const snap of snapshots) {
      const tier = tierMap[snap.subreddit];
      if (tier === undefined) continue;

      if (!byDate[snap.snapshot_date]) {
        byDate[snap.snapshot_date] = {
          companionship_activity: 0,
          control_activity: 0,
        };
      }

      const d = byDate[snap.snapshot_date];
      const posts = snap.posts_today ?? 0;
      const activity = (snap.avg_comments_per_post ?? 0) * posts;

      if (tier === 0) {
        d.control_activity += activity;
      } else {
        d.companionship_activity += activity;
      }
    }

    const sorted = Object.entries(byDate)
      .map(([date, d]) => ({
        date,
        companionship: d.companionship_activity,
        control: d.control_activity,
      }))
      .sort((a, b) => a.date.localeCompare(b.date));

    const days = getDaysForRange(timeRange);
    if (days === null) return sorted;

    const cutoff = new Date();
    cutoff.setDate(cutoff.getDate() - days);
    const cutoffStr = cutoff.toISOString().split("T")[0];
    return sorted.filter((d) => d.date >= cutoffStr);
  }, [snapshots, tierMap, timeRange]);

  const visibleEvents = useMemo(() => {
    if (chartData.length === 0) return [];
    const minDate = chartData[0].date;
    const maxDate = chartData[chartData.length - 1].date;
    return EVENTS.filter((e) => e.date >= minDate && e.date <= maxDate);
  }, [chartData]);

  if (chartData.length === 0) {
    return (
      <div className="h-64 flex items-center justify-center text-sm text-muted">
        No data yet — run the daily collector to populate charts.
      </div>
    );
  }

  return (
    <div>
      {/* Time range selector */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex gap-1">
          {TIME_RANGES.map((range) => (
            <button
              key={range}
              onClick={() => setTimeRange(range)}
              className={`px-3 py-1.5 text-xs font-medium rounded-md transition-colors ${
                timeRange === range
                  ? "bg-[#2a1a0e] text-[#f5f0eb] border border-[#2e2419]"
                  : "text-[#8a7060] hover:text-[#f5f0eb] hover:bg-[#2a1a0e]"
              }`}
            >
              {range}
            </button>
          ))}
        </div>
        <div className="text-xs text-muted">
          {chartData.length} day{chartData.length !== 1 ? "s" : ""} · engagement (posts × comments)
        </div>
      </div>

      {/* Chart */}
      <div className="w-full h-[350px] sm:h-[450px]">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart
            data={chartData}
            margin={{ top: 20, right: 10, left: 0, bottom: 10 }}
          >
            <CartesianGrid
              strokeDasharray="3 3"
              stroke="#2e2419"
              vertical={false}
            />
            <XAxis
              dataKey="date"
              tickFormatter={formatDate}
              stroke="#2e2419"
              tick={{ fill: "#8a7060", fontSize: 11 }}
              axisLine={{ stroke: "#2e2419" }}
              tickLine={false}
              minTickGap={60}
            />
            <YAxis
              tickFormatter={formatNumber}
              stroke="#2e2419"
              tick={{ fill: "#8a7060", fontSize: 11 }}
              axisLine={false}
              tickLine={false}
              width={50}
            />
            <Tooltip
              content={({ active, payload, label }) => {
                if (!active || !payload?.length || !label) return null;
                return (
                  <div className="bg-[#2a1a0e] border border-[#6b3d2e] rounded-lg px-3 py-2 text-xs">
                    <div className="text-[#8a7060] mb-1">
                      {formatDate(label as string)}
                    </div>
                    {payload.map((p) => (
                      <div
                        key={p.dataKey as string}
                        className="flex items-center gap-2"
                      >
                        <span
                          className="w-2 h-2 rounded-full inline-block"
                          style={{ background: p.color }}
                        />
                        <span className="text-[#8a7060]">
                          {p.dataKey === "companionship"
                            ? "Companionship"
                            : "Control"}
                        </span>
                        <span className="text-[#f5f0eb] font-medium ml-auto">
                          {formatNumber(p.value as number)}
                        </span>
                      </div>
                    ))}
                  </div>
                );
              }}
              cursor={{ stroke: "#6b3d2e", strokeDasharray: "3 3" }}
            />

            {/* Event markers */}
            {visibleEvents.map((event) => (
              <ReferenceLine
                key={event.date}
                x={event.date}
                stroke="#6b3d2e"
                strokeDasharray="2 4"
                label={{
                  value: `${event.emoji} ${event.label}`,
                  position: "top",
                  fill: "#8a7060",
                  fontSize: 10,
                  offset: 5,
                }}
              />
            ))}

            {/* Companionship line — primary orange */}
            <Line
              type="monotone"
              dataKey="companionship"
              stroke="#e8692a"
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 4, fill: "#e8692a" }}
              name="Companionship"
            />

            {/* Control line — muted */}
            <Line
              type="monotone"
              dataKey="control"
              stroke="#4a4540"
              strokeWidth={1.5}
              dot={false}
              activeDot={{ r: 3, fill: "#4a4540" }}
              strokeDasharray="4 2"
              name="Control"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Lens selector */}
      <div className="mt-6 flex gap-2 overflow-x-auto lens-scroll pb-2">
        {LENSES.map((lens) => (
          <button
            key={lens.id}
            onClick={() => setActiveLens(lens.id)}
            className={`flex items-center gap-1.5 px-3 py-2 text-sm font-medium rounded-lg whitespace-nowrap transition-colors ${
              activeLens === lens.id
                ? "bg-[#2a1a0e] text-[#f5f0eb] border border-[#6b3d2e]"
                : "text-[#8a7060] hover:text-[#f5f0eb] hover:bg-[#2a1a0e]"
            }`}
          >
            <span>{lens.emoji}</span>
            <span>{lens.label}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
