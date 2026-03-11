"use client";

import { useMemo, useState } from "react";
import {
  ComposedChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
  CartesianGrid,
} from "recharts";
import type { ThemeData, ThemeDataPoint } from "./page";

// ─── Themes ────────────────────────────────────────────────────────────────

const THEMES = [
  { id: "romance",       label: "Romance",       color: "#F97316" },
  { id: "attachment",    label: "Attachment",    color: "#3B82F6" },
  { id: "dependency",    label: "Dependency",    color: "#EF4444" },
  { id: "consciousness", label: "Consciousness", color: "#A855F7" },
  { id: "therapy",       label: "Therapy",       color: "#EC4899" },
  { id: "memory",        label: "Memory",        color: "#F59E0B" },
  { id: "realism",       label: "Realism",       color: "#06B6D4" },
] as const;

type ThemeId = typeof THEMES[number]["id"];

// ─── Events ────────────────────────────────────────────────────────────────
// row controls vertical stagger to prevent label overlap

const EVENTS = [
  { date: "2023-02-01", label: "Replika removes ERP",        row: 0 },
  { date: "2024-05-13", label: "GPT-4o launches",             row: 1 },
  { date: "2025-04-01", label: "GPT-4o sycophancy update",   row: 0 },
  { date: "2025-08-07", label: "GPT-4o first retirement",    row: 1 },
  { date: "2026-01-29", label: "4o retirement announced",    row: 0 },
  { date: "2026-02-13", label: "GPT-4o permanently retired", row: 1 },
];

// ─── Helpers ───────────────────────────────────────────────────────────────

type TimeRange = "30D" | "90D" | "1Y" | "ALL";

function formatXTick(dateStr: string): string {
  const d = new Date(dateStr + "T00:00:00Z");
  const months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
  return `${months[d.getUTCMonth()]} '${d.getUTCFullYear().toString().slice(2)}`;
}

function formatCount(n: number): string {
  if (n >= 1000) return `${(n / 1000).toFixed(1)}k`;
  return n.toFixed(0);
}

function avg(arr: ThemeDataPoint[]): number {
  if (!arr.length) return 0;
  return arr.reduce((s, e) => s + e.value, 0) / arr.length;
}

// ─── Component ─────────────────────────────────────────────────────────────

type Props = { themeData: ThemeData };

export default function TrendsExplorer({ themeData }: Props) {
  const [highlighted, setHighlighted] = useState<Set<ThemeId>>(new Set());
  const [lastHighlighted, setLastHighlighted] = useState<ThemeId | null>(null);
  const [timeRange, setTimeRange] = useState<TimeRange>("ALL");

  // ── Toggle handler ──
  function toggleTheme(id: ThemeId) {
    const isActive = highlighted.has(id);
    const next = new Set(highlighted);
    if (isActive) {
      next.delete(id);
      if (lastHighlighted === id) {
        const rest = [...next] as ThemeId[];
        setLastHighlighted(rest.length ? rest[rest.length - 1] : null);
      }
    } else {
      next.add(id);
      setLastHighlighted(id);
    }
    setHighlighted(next);
  }

  // ── Unified chart data array ──
  const allChartData = useMemo(() => {
    const lookup: Record<string, Record<string, number>> = {};
    for (const theme of THEMES) {
      for (const pt of themeData[theme.id] ?? []) {
        if (!lookup[pt.date]) lookup[pt.date] = {};
        lookup[pt.date][theme.id] = pt.value;
      }
    }
    return Object.entries(lookup)
      .sort(([a], [b]) => a.localeCompare(b))
      .map(([date, vals]) => ({ date, ...vals }));
  }, [themeData]);

  // ── Time range filter ──
  const chartData = useMemo(() => {
    if (timeRange === "ALL") return allChartData;
    const daysMap: Record<string, number> = { "30D": 30, "90D": 90, "1Y": 365 };
    const cutoff = new Date();
    cutoff.setDate(cutoff.getDate() - daysMap[timeRange]);
    const cutoffStr = cutoff.toISOString().split("T")[0];
    return allChartData.filter((d) => d.date >= cutoffStr);
  }, [allChartData, timeRange]);

  // ── Visible events ──
  const visibleEvents = useMemo(() => {
    if (!chartData.length) return [];
    const min = chartData[0].date;
    const max = chartData[chartData.length - 1].date;
    return EVENTS.filter((e) => e.date >= min && e.date <= max);
  }, [chartData]);

  // ── Dynamic summary ──
  const summary = useMemo(() => {
    const activeTheme =
      lastHighlighted && highlighted.has(lastHighlighted)
        ? THEMES.find((t) => t.id === lastHighlighted) ?? null
        : null;

    if (!activeTheme) {
      return {
        text: "Tracking how people talk about AI companions across Reddit — from 2023 to today.",
        themeName: null,
        themeColor: null,
      };
    }

    const entries = themeData[activeTheme.id] ?? [];
    if (entries.length < 60) {
      return { text: `Tracking ${activeTheme.label} discourse across Reddit.`, themeName: activeTheme.label, themeColor: activeTheme.color };
    }

    const first30 = avg(entries.slice(0, 30));
    const last30 = avg(entries.slice(-30));
    if (first30 === 0) {
      return { text: `${activeTheme.label} language is tracked from 2023 to today.`, themeName: activeTheme.label, themeColor: activeTheme.color };
    }

    const pct = Math.round(((last30 - first30) / first30) * 100);
    const dir = pct >= 0 ? "increased" : "decreased";
    return {
      text: `${activeTheme.label} language has ${dir} ${Math.abs(pct)}% since early 2023.`,
      themeName: activeTheme.label,
      themeColor: activeTheme.color,
    };
  }, [lastHighlighted, highlighted, themeData]);

  const anyHighlighted = highlighted.size > 0;
  const minTickGap = timeRange === "30D" ? 40 : timeRange === "90D" ? 50 : 80;

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
      <div className="flex flex-wrap gap-2 mb-5">
        {THEMES.map((theme) => {
          const active = highlighted.has(theme.id);
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
              {theme.label}
            </button>
          );
        })}
      </div>

      {/* Time range selector */}
      <div className="flex gap-1 mb-6">
        {(["30D", "90D", "1Y", "ALL"] as TimeRange[]).map((range) => (
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
        className="rounded-xl border p-4 sm:p-6"
        style={{ backgroundColor: "#1A1D27", borderColor: "#2A2D3A" }}
      >
        <div className="w-full h-[360px] sm:h-[440px]">
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart
              data={chartData}
              margin={{ top: 36, right: 16, left: 0, bottom: 8 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#2A2D3A" vertical={false} />

              <XAxis
                dataKey="date"
                tickFormatter={formatXTick}
                stroke="#2A2D3A"
                tick={{ fill: "#94A3B8", fontSize: 12 }}
                tickLine={false}
                axisLine={{ stroke: "#2A2D3A" }}
                minTickGap={minTickGap}
              />

              {THEMES.map((theme) => {
                const isVisible = anyHighlighted && theme.id === lastHighlighted && highlighted.has(theme.id);
                return (
                  <YAxis
                    key={theme.id}
                    yAxisId={theme.id}
                    tickFormatter={formatCount}
                    stroke="transparent"
                    tick={isVisible ? { fill: "#94A3B8", fontSize: 12 } : false}
                    axisLine={false}
                    tickLine={false}
                    width={isVisible ? 44 : 0}
                    hide={!isVisible}
                  />
                );
              })}

              <Tooltip
                content={({ active, payload, label }) => {
                  if (!active || !payload?.length || !label) return null;
                  const entries = anyHighlighted
                    ? payload.filter((p) => highlighted.has(p.dataKey as ThemeId))
                    : [...payload]
                        .sort((a, b) => (b.value as number) - (a.value as number))
                        .slice(0, 4);
                  if (!entries.length) return null;
                  return (
                    <div
                      className="rounded-lg px-3 py-2 text-xs shadow-xl"
                      style={{ backgroundColor: "#0F1117", border: "1px solid #2A2D3A" }}
                    >
                      <div className="text-[#94A3B8] mb-1.5">{formatXTick(label as string)}</div>
                      {entries.map((p) => {
                        const theme = THEMES.find((t) => t.id === p.dataKey);
                        return (
                          <div key={p.dataKey as string} className="flex items-center gap-2 mb-0.5">
                            <span
                              className="w-2 h-2 rounded-full flex-shrink-0"
                              style={{ backgroundColor: theme?.color }}
                            />
                            <span style={{ color: "#94A3B8" }}>{theme?.label}</span>
                            <span className="text-[#F8FAFC] font-medium ml-auto pl-4">
                              {formatCount(p.value as number)}
                            </span>
                          </div>
                        );
                      })}
                    </div>
                  );
                }}
                cursor={{ stroke: "#2A2D3A", strokeWidth: 1 }}
              />

              {/* Event annotations — staggered to prevent label overlap */}
              {visibleEvents.map((event) => (
                <ReferenceLine
                  key={event.date}
                  yAxisId={THEMES[0].id}
                  x={event.date}
                  stroke="#6B7280"
                  strokeDasharray="2 4"
                  strokeWidth={1}
                  label={{
                    value: event.label,
                    position: "top",
                    fill: "#94A3B8",
                    fontSize: 10,
                    offset: event.row === 0 ? 6 : 22,
                  }}
                />
              ))}

              {/* Theme lines — faint when not highlighted, full when highlighted */}
              {THEMES.map((theme) => {
                const active = highlighted.has(theme.id);
                return (
                  <Area
                    key={theme.id}
                    yAxisId={theme.id}
                    type="monotone"
                    dataKey={theme.id}
                    stroke={theme.color}
                    strokeWidth={active ? 2 : 1}
                    strokeOpacity={active ? 1 : 0.2}
                    fill={theme.color}
                    fillOpacity={active ? 0.08 : 0}
                    dot={false}
                    activeDot={active ? { r: 3, fill: theme.color, stroke: "none" } : false}
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
