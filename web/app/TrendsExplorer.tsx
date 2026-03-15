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
  { id: "therapy",       label: "Therapy",       emoji: "💊", color: "#EC4899" },
  { id: "consciousness", label: "Conscious",     emoji: "🔮", color: "#A855F7" },
  { id: "addiction",     label: "Addiction",     emoji: "🔁", color: "#EF4444" },
  { id: "romance",       label: "Romance",       emoji: "💕", color: "#F97316" },
  { id: "sexual_erp",    label: "Sex / ERP",     emoji: "🔞", color: "#DC2626" },
  { id: "rupture",       label: "Rupture",       emoji: "💔", color: "#06B6D4" },
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
  return Math.round(n).toString();
}

function avg(arr: ThemeDataPoint[]): number {
  if (!arr.length) return 0;
  return arr.reduce((s, e) => s + e.value, 0) / arr.length;
}

// ─── Event label ───────────────────────────────────────────────────────────
// Custom SVG label for ReferenceLine — row controls vertical stagger

function EventLabel({ viewBox, event }: { viewBox?: { x: number; y: number }; event: typeof EVENTS[number] }) {
  if (!viewBox) return null;
  return (
    <text
      x={viewBox.x + 4}
      y={viewBox.y - 42 + event.row * 18}
      fill="#94A3B8"
      fontSize={10}
    >
      {event.label}
    </text>
  );
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

  // ── Adaptive rolling window by time range ──
  const smoothWindow = timeRange === "ALL" ? 7 : timeRange === "1Y" ? 7 : timeRange === "90D" ? 7 : 1;

  // ── Apply rolling average — O(N) per theme, not O(N²) ──
  const smoothedChartData = useMemo(() => {
    const n = chartData.length;

    // Compute a centered rolling average for all N points in one pass
    function rollingAvg(vals: number[], window: number): number[] {
      const half = Math.floor(window / 2);
      const out = new Array<number>(n);
      let sum = 0, count = 0, lo = 0, hi = -1;
      for (let i = 0; i < n; i++) {
        const newHi = Math.min(n - 1, i + half);
        while (hi < newHi) { hi++; sum += vals[hi]; count++; }
        const newLo = Math.max(0, i - half);
        while (lo < newLo) { sum -= vals[lo]; count--; lo++; }
        out[i] = count > 0 ? sum / count : 0;
      }
      return out;
    }

    // Extract raw values per theme once, then compute both windows
    const rows: Record<string, number[]> = {};
    const faintRows: Record<string, number[]> = {};
    for (const theme of THEMES) {
      const raw = chartData.map((d) => {
        const v = (d as unknown as Record<string, number>)[theme.id];
        return v != null && !isNaN(v) ? v : 0;
      });
      rows[theme.id] = smoothWindow > 1 ? rollingAvg(raw, smoothWindow) : raw;
      faintRows[theme.id] = rollingAvg(raw, 30);
    }

    return chartData.map((point, i) => {
      const result: Record<string, number | string> = { date: point.date };
      for (const theme of THEMES) {
        result[theme.id] = rows[theme.id][i];
        result[`${theme.id}_faint`] = faintRows[theme.id][i];
      }
      return result;
    });
  }, [chartData, smoothWindow]);

  // ── Visible events ──
  const visibleEvents = useMemo(() => {
    if (!chartData.length) return [];
    const min = chartData[0].date;
    const max = chartData[chartData.length - 1].date;
    return EVENTS.filter((e) => e.date >= min && e.date <= max);
  }, [chartData]);

  // ── Per-theme p99 domain cap + peak tracking (from smoothed data) ──
  const { domainCap, peakValue } = useMemo(() => {
    const cap: Partial<Record<ThemeId, number>> = {};
    const peak: Partial<Record<ThemeId, number>> = {};
    for (const theme of THEMES) {
      const vals = smoothedChartData
        .map((d) => (d as unknown as Record<string, number>)[theme.id])
        .filter((v) => v != null && !isNaN(v))
        .sort((a, b) => a - b);
      if (!vals.length) continue;
      cap[theme.id] = vals[Math.floor(vals.length * 0.99)];
      peak[theme.id] = vals[vals.length - 1]; // max
    }
    return { domainCap: cap, peakValue: peak };
  }, [smoothedChartData]);

  // ── Dynamic summary ──
  // Compare trailing 90-day avg to same 90-day window one year ago
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
    if (entries.length < 90) {
      return { text: `Tracking ${activeTheme.label} discourse across Reddit.`, themeName: activeTheme.label, themeColor: activeTheme.color };
    }

    // Build date→value lookup
    const byDate: Record<string, number> = {};
    for (const e of entries) byDate[e.date] = e.value;

    // Trailing 90 days and same period last year
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

    if (priorAvg === 0 || prior.length < 30) {
      return { text: `Tracking ${activeTheme.label} discourse across Reddit.`, themeName: activeTheme.label, themeColor: activeTheme.color };
    }

    const pct = Math.round(((recentAvg - priorAvg) / priorAvg) * 100);
    let text: string;
    if (Math.abs(pct) < 10) {
      text = `${activeTheme.label} language has been stable compared to the same period last year.`;
    } else {
      const dir = pct > 0 ? "up" : "down";
      text = `${activeTheme.label} language is ${dir} ${Math.abs(pct)}% compared to the same period last year.`;
    }

    return { text, themeName: activeTheme.label, themeColor: activeTheme.color };
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
      <div className="flex flex-nowrap overflow-x-auto gap-2 mb-5">
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
              {theme.emoji} {theme.label}
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
              data={smoothedChartData}
              margin={{ top: 56, right: 16, left: 0, bottom: 8 }}
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
                    width={isVisible ? 52 : 0}
                    hide={!isVisible}
                    domain={[0, domainCap[theme.id] ?? "auto"]}
                    label={isVisible ? { value: "posts/day", angle: -90, position: "insideLeft", fill: "#94A3B8", fontSize: 10, dx: 10 } : undefined}
                  />
                );
              })}

              <Tooltip
                content={({ active, payload, label }) => {
                  if (!active || !payload?.length || !label) return null;
                  const themeIdOf = (key: string) => key.replace(/_faint$/, "") as ThemeId;
                  const entries = anyHighlighted
                    ? payload.filter((p) => highlighted.has(themeIdOf(p.dataKey as string)))
                    : [...payload]
                        .filter((p) => !(p.dataKey as string).endsWith("_faint"))
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
                        const tid = themeIdOf(p.dataKey as string);
                        const theme = THEMES.find((t) => t.id === tid);
                        const val = p.value as number;
                        const cap = domainCap[tid];
                        const isClipped = cap != null && val > cap;
                        return (
                          <div key={p.dataKey as string} className="flex items-center gap-2 mb-0.5">
                            <span
                              className="w-2 h-2 rounded-full flex-shrink-0"
                              style={{ backgroundColor: theme?.color }}
                            />
                            <span style={{ color: "#94A3B8" }}>{theme?.label}</span>
                            <span className="text-[#F8FAFC] font-medium ml-auto pl-4">
                              {formatCount(val)}{isClipped ? " (clipped)" : ""}
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
                  label={<EventLabel event={event} />}
                />
              ))}

              {/* Clipped-peak cap line — shows actual peak when data exceeds y-axis */}
              {THEMES.map((theme) => {
                if (!highlighted.has(theme.id)) return null;
                const cap = domainCap[theme.id];
                const peak = peakValue[theme.id];
                if (cap == null || peak == null || peak <= cap) return null;
                return (
                  <ReferenceLine
                    key={`cap-${theme.id}`}
                    yAxisId={theme.id}
                    y={cap}
                    stroke={theme.color}
                    strokeDasharray="4 4"
                    strokeOpacity={0.4}
                    strokeWidth={1}
                    label={{
                      value: `peak: ${formatCount(peak)}`,
                      position: "right",
                      fill: theme.color,
                      fontSize: 10,
                      opacity: 0.7,
                    }}
                  />
                );
              })}

              {/* Theme lines — faint when not highlighted, full when highlighted */}
              {THEMES.map((theme) => {
                const active = highlighted.has(theme.id);
                return (
                  <Area
                    key={theme.id}
                    yAxisId={theme.id}
                    type="monotone"
                    dataKey={active ? theme.id : `${theme.id}_faint`}
                    stroke={theme.color}
                    strokeWidth={active ? 2 : 1}
                    strokeOpacity={active ? 1 : 0.1}
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
