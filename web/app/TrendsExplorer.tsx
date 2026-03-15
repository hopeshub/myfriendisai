"use client";

import { useMemo, useRef, useState } from "react";
import {
  ComposedChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  ReferenceLine,
} from "recharts";
import type { ThemeData } from "./page";

// ─── Themes ────────────────────────────────────────────────────────────────

const THEMES = [
  { id: "therapy",       label: "Therapy",        emoji: "💊", color: "#EC4899" },
  { id: "consciousness", label: "Consciousness",  emoji: "🔮", color: "#A855F7" },
  { id: "addiction",     label: "Addiction",       emoji: "🔁", color: "#EF4444" },
  { id: "romance",       label: "Romance",        emoji: "💕", color: "#F97316" },
  { id: "sexual_erp",    label: "Sex / ERP",      emoji: "🔞", color: "#DC2626" },
  { id: "rupture",       label: "Rupture",        emoji: "💔", color: "#06B6D4" },
] as const;

type ThemeId = typeof THEMES[number]["id"];

// ─── Events ────────────────────────────────────────────────────────────────

const EVENTS = [
  { date: "2023-02-01", label: "Replika ERP ban" },
  { date: "2024-05-01", label: "4o launches" },
  { date: "2025-04-01", label: "Sycophancy fix" },
  { date: "2025-08-01", label: "4o 1st sunset" },
  { date: "2026-01-01", label: "4o sunset ann." },
  { date: "2026-02-01", label: "4o retired" },
];

// ─── Helpers ───────────────────────────────────────────────────────────────

type TimeRange = "6M" | "1Y" | "ALL";

const MONTH_NAMES = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];

function formatMonthTick(dateStr: string): string {
  const d = new Date(dateStr + "T00:00:00Z");
  return `${MONTH_NAMES[d.getUTCMonth()]} ${d.getUTCFullYear()}`;
}

function toMonth(dateStr: string): string {
  return dateStr.slice(0, 7) + "-01";
}

// ─── Component ─────────────────────────────────────────────────────────────

type Props = { themeData: ThemeData };

export default function TrendsExplorer({ themeData }: Props) {
  const [selected, setSelected] = useState<ThemeId | null>(null);
  const [timeRange, setTimeRange] = useState<TimeRange>("ALL");
  const chartRef = useRef<HTMLDivElement>(null);

  function toggleTheme(id: ThemeId) {
    setSelected(selected === id ? null : id);
  }

  // ── Monthly aggregation (raw counts) ──
  const allMonthlyRaw = useMemo(() => {
    const monthlyRaw: Record<string, Record<string, number>> = {};
    for (const theme of THEMES) {
      for (const pt of themeData[theme.id] ?? []) {
        const m = toMonth(pt.date);
        if (!monthlyRaw[m]) monthlyRaw[m] = {};
        monthlyRaw[m][theme.id] = (monthlyRaw[m][theme.id] ?? 0) + pt.value;
      }
    }
    return Object.keys(monthlyRaw)
      .sort()
      .map((m) => ({ date: m, ...monthlyRaw[m] }) as Record<string, number | string>);
  }, [themeData]);

  // ── Time range filter (on raw counts) ──
  const filteredRaw = useMemo(() => {
    if (timeRange === "ALL") return allMonthlyRaw;
    const monthsBack = timeRange === "1Y" ? 12 : 6;
    const cutoff = new Date();
    cutoff.setMonth(cutoff.getMonth() - monthsBack);
    const cutoffStr = cutoff.toISOString().slice(0, 7) + "-01";
    return allMonthlyRaw.filter((d) => (d.date as string) >= cutoffStr);
  }, [allMonthlyRaw, timeRange]);

  // ── Index 0-100 relative to peak within visible range ──
  const { chartData, peakMonths } = useMemo(() => {
    const peaks: Partial<Record<ThemeId, { month: string; count: number }>> = {};
    for (const theme of THEMES) {
      let peakMonth = "";
      let peakCount = 0;
      for (const row of filteredRaw) {
        const c = (row[theme.id] as number) ?? 0;
        if (c > peakCount) { peakCount = c; peakMonth = row.date as string; }
      }
      if (peakCount > 0) peaks[theme.id] = { month: peakMonth, count: peakCount };
    }
    const data = filteredRaw.map((row) => {
      const out: Record<string, number | string> = { date: row.date };
      for (const theme of THEMES) {
        const raw = (row[theme.id] as number) ?? 0;
        const peak = peaks[theme.id]?.count ?? 1;
        out[theme.id] = (raw / peak) * 100;
      }
      return out;
    });
    return { chartData: data, peakMonths: peaks };
  }, [filteredRaw]);

  // ── Visible events (filtered by current time range) ──
  const visibleEvents = useMemo(() => {
    if (!chartData.length) return [];
    const min = chartData[0].date as string;
    const max = chartData[chartData.length - 1].date as string;
    return EVENTS.filter((e) => e.date >= min && e.date <= max);
  }, [chartData]);

  // ── Date range for subtitle ──
  const dateRange = useMemo(() => {
    if (!allMonthlyRaw.length) return { start: "", end: "", count: 0 };
    const first = allMonthlyRaw[0].date as string;
    const last = allMonthlyRaw[allMonthlyRaw.length - 1].date as string;
    return {
      start: formatMonthTick(first),
      end: formatMonthTick(last),
      count: THEMES.length,
    };
  }, [allMonthlyRaw]);

  // ── Subtitle logic ──
  const summary = useMemo(() => {
    const activeTheme = selected ? THEMES.find((t) => t.id === selected) ?? null : null;

    if (!activeTheme) {
      // Count subreddits from themeData (unique dates tells us it's active)
      return {
        text: `Tracking AI companion discourse across ${dateRange.count} themes, ${dateRange.start} to ${dateRange.end}.`,
        themeName: null,
        themeColor: null,
      };
    }

    // Try YoY comparison
    const entries = themeData[activeTheme.id] ?? [];
    if (entries.length >= 90) {
      const sorted = entries.map((e) => e.date).sort();
      const latest = sorted[sorted.length - 1];
      const d = new Date(latest + "T00:00:00Z");
      const cutoff90 = new Date(d);
      cutoff90.setUTCDate(cutoff90.getUTCDate() - 90);
      const cutoff90Str = cutoff90.toISOString().split("T")[0];

      const priorEnd = new Date(d);
      priorEnd.setUTCFullYear(priorEnd.getUTCFullYear() - 1);
      const priorStart = new Date(priorEnd);
      priorStart.setUTCDate(priorStart.getUTCDate() - 90);
      const priorEndStr = priorEnd.toISOString().split("T")[0];
      const priorStartStr = priorStart.toISOString().split("T")[0];

      const recent = entries.filter((e) => e.date > cutoff90Str && e.date <= latest);
      const prior = entries.filter((e) => e.date > priorStartStr && e.date <= priorEndStr);

      const recentAvg = recent.length > 0 ? recent.reduce((s, e) => s + e.value, 0) / recent.length : 0;
      const priorAvg = prior.length > 0 ? prior.reduce((s, e) => s + e.value, 0) / prior.length : 0;

      if (priorAvg > 0 && prior.length >= 30) {
        const pct = Math.round(((recentAvg - priorAvg) / priorAvg) * 100);
        let text: string;
        if (Math.abs(pct) < 10) {
          text = `${activeTheme.label} has been stable vs same period last year.`;
        } else {
          const dir = pct > 0 ? "up" : "down";
          text = `${activeTheme.label} is ${dir} ${Math.abs(pct)}% vs same period last year.`;
        }
        return { text, themeName: activeTheme.label, themeColor: activeTheme.color };
      }
    }

    // Fallback: show peak month
    const peak = peakMonths[activeTheme.id];
    if (peak) {
      const text = `${activeTheme.label} peaked in ${formatMonthTick(peak.month)}.`;
      return { text, themeName: activeTheme.label, themeColor: activeTheme.color };
    }

    return { text: `Tracking ${activeTheme.label} discourse.`, themeName: activeTheme.label, themeColor: activeTheme.color };
  }, [selected, themeData, dateRange, peakMonths]);

  const minTickGap = timeRange === "6M" ? 40 : 60;

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 py-10">
      {/* Headline + dynamic summary */}
      <div className="mb-8">
        <h1 className="text-2xl sm:text-3xl font-bold text-[#F8FAFC] mb-2">
          How are people talking about AI companions?
        </h1>
        <p className="text-base text-[#94A3B8]">
          {summary.themeName && summary.themeColor ? (
            <>
              {summary.text.split(summary.themeName).map((part, i, arr) =>
                i < arr.length - 1 ? (
                  <span key={i}>
                    {part}
                    <span style={{ color: summary.themeColor! }}>{summary.themeName}</span>
                  </span>
                ) : (
                  <span key={i}>{part}</span>
                )
              )}
            </>
          ) : (
            summary.text
          )}
        </p>
      </div>

      {/* Theme toggles */}
      <div className="flex flex-nowrap overflow-x-auto gap-2 mb-5">
        {THEMES.map((theme) => {
          const active = selected === theme.id;
          return (
            <button
              key={theme.id}
              onClick={() => toggleTheme(theme.id)}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-semibold transition-all"
              style={{
                border: `1px solid ${active ? theme.color : "#2A2D3A"}`,
                backgroundColor: active ? `${theme.color}20` : "transparent",
                color: active ? theme.color : "#94A3B8",
              }}
            >
              <span
                className="w-2 h-2 rounded-full flex-shrink-0"
                style={{ backgroundColor: theme.color, opacity: active ? 1 : 0.35 }}
              />
              {theme.emoji} {theme.label}
            </button>
          );
        })}
      </div>

      {/* Time range selector */}
      <div className="flex gap-1 mb-6">
        {(["6M", "1Y", "ALL"] as TimeRange[]).map((range) => (
          <button
            key={range}
            onClick={() => setTimeRange(range)}
            className="px-3 py-1 text-xs font-medium rounded-md transition-colors"
            style={{
              backgroundColor: timeRange === range ? "#1A1D27" : "transparent",
              color: timeRange === range ? "#F8FAFC" : "#94A3B8",
              border: `1px solid ${timeRange === range ? "#2A2D3A" : "transparent"}`,
            }}
          >
            {range}
          </button>
        ))}
      </div>

      {/* Chart */}
      <div
        ref={chartRef}
        className="rounded-xl border p-4 sm:p-6"
        style={{ backgroundColor: "#1A1D27", borderColor: "#2A2D3A" }}
      >
        <div className="w-full h-[360px] sm:h-[440px] overflow-hidden">
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart
              data={chartData}
              margin={{ top: 80, right: 16, left: 0, bottom: 8 }}
            >
              <CartesianGrid
                strokeDasharray="3 3"
                stroke="#2A2D3A"
                vertical={false}
                horizontalPoints={[]}
              />

              <XAxis
                dataKey="date"
                tickFormatter={formatMonthTick}
                stroke="#2A2D3A"
                tick={{ fill: "#94A3B8", fontSize: 12 }}
                tickLine={false}
                axisLine={{ stroke: "#2A2D3A" }}
                minTickGap={minTickGap}
              />

              <YAxis
                yAxisId="index"
                domain={[0, 100]}
                ticks={[25, 50, 75, 100]}
                tickFormatter={(v) => String(v)}
                stroke="transparent"
                tick={{ fill: "#94A3B8", fontSize: 12 }}
                axisLine={false}
                tickLine={false}
                width={32}
              />

              <Tooltip
                content={({ active, payload, label }) => {
                  if (!active || !payload?.length || !label) return null;
                  const entries = selected
                    ? payload.filter((p) => p.dataKey === selected)
                    : [...payload].sort((a, b) => (b.value as number) - (a.value as number));
                  if (!entries.length) return null;
                  return (
                    <div
                      className="rounded-lg px-3 py-2 text-xs shadow-xl"
                      style={{ backgroundColor: "#0F1117", border: "1px solid #2A2D3A" }}
                    >
                      <div className="text-[#94A3B8] mb-1.5">{formatMonthTick(label as string)}</div>
                      {entries.map((p) => {
                        const tid = p.dataKey as ThemeId;
                        const theme = THEMES.find((t) => t.id === tid);
                        return (
                          <div key={tid} className="flex items-center gap-2 mb-0.5">
                            <span
                              className="w-2 h-2 rounded-full flex-shrink-0"
                              style={{ backgroundColor: theme?.color }}
                            />
                            <span style={{ color: "#94A3B8" }}>{theme?.label}</span>
                            <span className="text-[#F8FAFC] font-medium ml-auto pl-4">
                              {Math.round(p.value as number)}
                            </span>
                          </div>
                        );
                      })}
                    </div>
                  );
                }}
                cursor={{ stroke: "#2A2D3A", strokeWidth: 1 }}
              />

              {/* Event annotations */}
              {visibleEvents.map((event) => (
                <ReferenceLine
                  key={event.date}
                  yAxisId="index"
                  x={event.date}
                  stroke="#6B7280"
                  strokeDasharray="2 4"
                  strokeWidth={1}
                  label={{
                    value: event.label,
                    position: "insideTopLeft",
                    angle: -90,
                    fill: "#94A3B8",
                    fontSize: 9,
                    offset: 6,
                  }}
                />
              ))}

              {/* Theme lines */}
              {THEMES.map((theme) => {
                const isSelected = selected === theme.id;
                const isFaded = selected !== null && !isSelected;
                return (
                  <Line
                    key={theme.id}
                    yAxisId="index"
                    type="monotone"
                    dataKey={theme.id}
                    stroke={theme.color}
                    strokeWidth={isSelected ? 2.5 : 1.5}
                    strokeOpacity={isFaded ? 0.2 : 1}
                    dot={false}
                    activeDot={!isFaded ? { r: 3, fill: theme.color, stroke: "none" } : false}
                    isAnimationActive={false}
                    legendType="none"
                  />
                );
              })}
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
