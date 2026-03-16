"use client";

import { useMemo, useRef, useState } from "react";
import {
  ComposedChart,
  Line,
  LineChart,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  ReferenceLine,
} from "recharts";
import type { ThemeData } from "./page";
import { useBreakpoint } from "./useBreakpoint";

// ─── Themes ────────────────────────────────────────────────────────────────

const THEMES = [
  { id: "therapy",       label: "Therapy",        emoji: "🫂", color: "#3B82F6" },
  { id: "consciousness", label: "Consciousness",  emoji: "🧠", color: "#A855F7" },
  { id: "addiction",     label: "Addiction",       emoji: "💊", color: "#fd7112" },
  { id: "romance",       label: "Romance",        emoji: "💕", color: "#FF69B4" },
  { id: "sexual_erp",    label: "Sex / ERP",      emoji: "🔞", color: "#dc2625" },
  { id: "rupture",       label: "Rupture",        emoji: "🥀", color: "#22C55E" },
] as const;

type ThemeId = (typeof THEMES)[number]["id"];

// ─── Events ────────────────────────────────────────────────────────────────

const EVENTS = [
  { date: "2023-02-01", label: "Replika ERP removal" },
  { date: "2024-05-01", label: "4o launches" },
  { date: "2025-04-01", label: "Sycophancy update" },
  { date: "2025-08-01", label: "4o 1st sunset" },
  { date: "2026-01-01", label: "4o 2nd sunset" },
  { date: "2026-02-01", label: "4o retired" },
];

// ─── Helpers ───────────────────────────────────────────────────────────────

type TimeRange = "6M" | "1Y" | "2Y" | "ALL";
type ChartMode = "absolute" | "relative";

const MONTH_NAMES = [
  "Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec",
];

function formatMonthTick(dateStr: string): string {
  const d = new Date(dateStr + "T00:00:00Z");
  return `${MONTH_NAMES[d.getUTCMonth()]} ${d.getUTCFullYear()}`;
}

function formatMonthTickShort(dateStr: string): string {
  const d = new Date(dateStr + "T00:00:00Z");
  const yr = String(d.getUTCFullYear()).slice(2);
  return `${MONTH_NAMES[d.getUTCMonth()]} '${yr}`;
}

/** Round up to a clean axis max (matches typical charting library behavior) */
function niceMax(v: number): number {
  if (v <= 0) return 10;
  const exp = Math.pow(10, Math.floor(Math.log10(v)));
  const frac = v / exp;
  if (frac <= 1) return exp;
  if (frac <= 2) return 2 * exp;
  if (frac <= 5) return 5 * exp;
  return 10 * exp;
}

function toMonth(dateStr: string): string {
  return dateStr.slice(0, 7) + "-01";
}

function downsample(data: number[], maxPoints: number): number[] {
  if (data.length <= maxPoints) return data;
  const step = data.length / maxPoints;
  const result: number[] = [];
  for (let i = 0; i < maxPoints; i++) {
    const start = Math.floor(i * step);
    const end = Math.floor((i + 1) * step);
    let sum = 0;
    for (let j = start; j < end; j++) sum += data[j];
    result.push(sum / (end - start));
  }
  return result;
}

/** Clip values above p95 so outlier spikes don't flatten the sparkline */
function clipOutliers(data: number[]): number[] {
  if (data.length < 5) return data;
  const sorted = [...data].sort((a, b) => a - b);
  const p95 = sorted[Math.floor(sorted.length * 0.95)];
  return data.map((v) => Math.min(v, p95));
}

// ─── Sparkline ─────────────────────────────────────────────────────────────

function Sparkline({
  data,
  color,
  height,
}: {
  data: number[];
  color: string;
  height: number;
}) {
  const chartData = data.map((v, i) => ({ v, i }));
  return (
    <ResponsiveContainer width="100%" height={height}>
      <LineChart data={chartData}>
        <Line
          type="monotone"
          dataKey="v"
          stroke={color}
          strokeWidth={1.2}
          dot={false}
          isAnimationActive={false}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}

// ─── Component ─────────────────────────────────────────────────────────────

type Props = { themeData: ThemeData };

export default function TrendsExplorer({ themeData }: Props) {
  const [selected, setSelected] = useState<Set<ThemeId>>(new Set());
  const [timeRange, setTimeRange] = useState<TimeRange>("1Y");
  const [chartMode, setChartMode] = useState<ChartMode>("absolute");
  const [autoSwitched, setAutoSwitched] = useState(false);
  const userModeRef = useRef<ChartMode>("absolute");
  const [eventsExpanded, setEventsExpanded] = useState(false);
  const chartRef = useRef<HTMLDivElement>(null);
  const mouseYRef = useRef<number>(0);
  const [nearestTheme, setNearestTheme] = useState<ThemeId | null>(null);
  const bp = useBreakpoint();

  function toggleTheme(id: ThemeId) {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }

  // ── Time range cutoff ──
  const cutoffDate = useMemo(() => {
    if (timeRange === "ALL") return null;
    const monthsBack = timeRange === "2Y" ? 24 : timeRange === "1Y" ? 12 : 6;
    const cutoff = new Date();
    cutoff.setMonth(cutoff.getMonth() - monthsBack);
    return cutoff.toISOString().split("T")[0];
  }, [timeRange]);

  // ── 90-day cutoff for metric card values ──
  const last90Cutoff = useMemo(() => {
    let latestDate = "";
    for (const theme of THEMES) {
      const pts = themeData[theme.id] ?? [];
      for (const p of pts) {
        if (p.date > latestDate) latestDate = p.date;
      }
    }
    if (!latestDate) return "";
    const d = new Date(latestDate + "T00:00:00Z");
    d.setUTCDate(d.getUTCDate() - 90);
    return d.toISOString().split("T")[0];
  }, [themeData]);

  // ── Metric card data (value = 90-day avg hitsPerK, sparkline = selected time range) ──
  const metricCards = useMemo(() => {
    const cards = THEMES.map((theme) => {
      const points = themeData[theme.id] ?? [];

      // 90-day average for the display value (always, regardless of time range)
      const recent = last90Cutoff
        ? points.filter((p) => p.date >= last90Cutoff)
        : points;
      const recentHpk = recent.map((p) => p.hitsPerK);
      const avgValue =
        recentHpk.length > 0
          ? recentHpk.reduce((s, v) => s + v, 0) / recentHpk.length
          : 0;

      // Sparkline uses the selected time range
      const filtered = cutoffDate
        ? points.filter((p) => p.date >= cutoffDate)
        : points;
      const sparkHpk = filtered.map((p) => p.hitsPerK);

      return {
        ...theme,
        value: Math.round(avgValue * 10) / 10,
        sparklineData: downsample(clipOutliers(sparkHpk), 60),
      };
    });
    return cards.sort((a, b) => b.value - a.value);
  }, [themeData, cutoffDate, last90Cutoff]);

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
      .map(
        (m) => ({ date: m, ...monthlyRaw[m] }) as Record<string, number | string>,
      );
  }, [themeData]);

  // ── Monthly aggregation (absolute: average hitsPerK per month) ──
  const allMonthlyAbsolute = useMemo(() => {
    const monthly: Record<
      string,
      Record<string, { sum: number; count: number }>
    > = {};
    for (const theme of THEMES) {
      for (const pt of themeData[theme.id] ?? []) {
        const m = toMonth(pt.date);
        if (!monthly[m]) monthly[m] = {};
        if (!monthly[m][theme.id])
          monthly[m][theme.id] = { sum: 0, count: 0 };
        monthly[m][theme.id].sum += pt.hitsPerK;
        monthly[m][theme.id].count += 1;
      }
    }
    return Object.keys(monthly)
      .sort()
      .map((m) => {
        const row: Record<string, number | string> = { date: m };
        for (const theme of THEMES) {
          const d = monthly[m]?.[theme.id];
          row[theme.id] = d ? d.sum / d.count : 0;
        }
        return row;
      });
  }, [themeData]);

  // ── Time range filter (on raw counts) ──
  const filteredRaw = useMemo(() => {
    if (timeRange === "ALL") return allMonthlyRaw;
    const monthsBack = timeRange === "2Y" ? 24 : timeRange === "1Y" ? 12 : 6;
    const cutoff = new Date();
    cutoff.setMonth(cutoff.getMonth() - monthsBack);
    const cutoffStr = cutoff.toISOString().slice(0, 7) + "-01";
    return allMonthlyRaw.filter((d) => (d.date as string) >= cutoffStr);
  }, [allMonthlyRaw, timeRange]);

  // ── Time range filter (on absolute hitsPerK) ──
  const filteredAbsolute = useMemo(() => {
    if (timeRange === "ALL") return allMonthlyAbsolute;
    const monthsBack = timeRange === "2Y" ? 24 : timeRange === "1Y" ? 12 : 6;
    const cutoff = new Date();
    cutoff.setMonth(cutoff.getMonth() - monthsBack);
    const cutoffStr = cutoff.toISOString().slice(0, 7) + "-01";
    return allMonthlyAbsolute.filter((d) => (d.date as string) >= cutoffStr);
  }, [allMonthlyAbsolute, timeRange]);

  // ── Chart data: absolute (hitsPerK) or relative (% of peak) ──
  const { chartData, peakMonths } = useMemo(() => {
    // Always compute peaks from raw data (used by summary)
    const peaks: Partial<Record<ThemeId, { month: string; count: number }>> = {};
    for (const theme of THEMES) {
      let peakMonth = "";
      let peakCount = 0;
      for (const row of filteredRaw) {
        const c = (row[theme.id] as number) ?? 0;
        if (c > peakCount) {
          peakCount = c;
          peakMonth = row.date as string;
        }
      }
      if (peakCount > 0)
        peaks[theme.id] = { month: peakMonth, count: peakCount };
    }

    if (chartMode === "absolute") {
      const data = filteredAbsolute.map((row) => {
        const out: Record<string, number | string> = { date: row.date };
        for (const theme of THEMES) {
          out[theme.id] = (row[theme.id] as number) ?? 0;
        }
        return out;
      });
      return { chartData: data, peakMonths: peaks };
    }

    // Relative mode — normalize each theme to its own peak = 100
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
  }, [filteredRaw, filteredAbsolute, chartMode]);

  // ── Y-axis domain max (explicit so tooltip pixel math matches the chart) ──
  const yDomainMax = useMemo(() => {
    if (chartMode === "relative") return 100;
    let max = 0;
    for (const row of chartData) {
      for (const theme of THEMES) {
        const v = (row[theme.id] as number) ?? 0;
        if (v > max) max = v;
      }
    }
    return niceMax(max);
  }, [chartMode, chartData]);

  // ── Visible events ──
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

  // ── Subtitle logic (show single-theme summary when exactly one selected) ──
  const summary = useMemo(() => {
    const activeId = selected.size === 1 ? [...selected][0] : null;
    const activeTheme = activeId
      ? THEMES.find((t) => t.id === activeId) ?? null
      : null;

    if (!activeTheme) {
      return {
        text: `Tracking AI companion discourse across ${dateRange.count} themes, ${dateRange.start} to ${dateRange.end}.`,
        themeName: null,
        themeColor: null,
      };
    }

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

      const recent = entries.filter(
        (e) => e.date > cutoff90Str && e.date <= latest,
      );
      const prior = entries.filter(
        (e) => e.date > priorStartStr && e.date <= priorEndStr,
      );

      const recentAvg =
        recent.length > 0
          ? recent.reduce((s, e) => s + e.value, 0) / recent.length
          : 0;
      const priorAvg =
        prior.length > 0
          ? prior.reduce((s, e) => s + e.value, 0) / prior.length
          : 0;

      if (priorAvg > 0 && prior.length >= 30) {
        const pct = Math.round(((recentAvg - priorAvg) / priorAvg) * 100);
        let text: string;
        if (Math.abs(pct) < 10) {
          text = `${activeTheme.label} has been stable vs same period last year.`;
        } else {
          const dir = pct > 0 ? "up" : "down";
          text = `${activeTheme.label} is ${dir} ${Math.abs(pct)}% vs same period last year.`;
        }
        return {
          text,
          themeName: activeTheme.label,
          themeColor: activeTheme.color,
        };
      }
    }

    const peak = peakMonths[activeTheme.id];
    if (peak) {
      const text = `${activeTheme.label} peaked in ${formatMonthTick(peak.month)}.`;
      return {
        text,
        themeName: activeTheme.label,
        themeColor: activeTheme.color,
      };
    }

    return {
      text: `Tracking ${activeTheme.label} discourse.`,
      themeName: activeTheme.label,
      themeColor: activeTheme.color,
    };
  }, [selected, themeData, dateRange, peakMonths]);

  // ── Responsive chart config ──
  const chartConfig = useMemo(() => {
    if (bp === "mobile") {
      return {
        height: 280,
        margin: { top: 10, right: 8, bottom: 30, left: 8 },
        xTickCount: 4,
        minTickGap: 30,
        strokeActive: 2.5,
        strokeInactive: 1.5,
        yAxisWidth: 0,
        showYAxis: false,
        eventLabelAngle: 0,
        showEventLabels: false,
        tickFormatter: formatMonthTickShort,
      };
    }
    if (bp === "tablet") {
      return {
        height: 360,
        margin: { top: 80, right: 20, bottom: 30, left: 40 },
        xTickCount: 6,
        minTickGap: 40,
        strokeActive: 2.5,
        strokeInactive: 1.5,
        yAxisWidth: 32,
        showYAxis: true,
        eventLabelAngle: -45,
        showEventLabels: true,
        tickFormatter: formatMonthTickShort,
      };
    }
    return {
      height: 440,
      margin: { top: 100, right: 64, bottom: 8, left: 0 },
      xTickCount: 8,
      minTickGap: timeRange === "6M" ? 40 : 60,
      strokeActive: 2,
      strokeInactive: 1,
      yAxisWidth: 32,
      showYAxis: true,
      eventLabelAngle: -60,
      showEventLabels: true,
      tickFormatter: formatMonthTick,
    };
  }, [bp, timeRange]);

  // ── Sparkline height by breakpoint ──
  const sparklineHeight = bp === "mobile" ? 20 : 24;

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 py-6 sm:py-10">
      {/* Headline + dynamic summary */}
      <div className="mb-6 sm:mb-8">
        <h1 className="text-[22px] sm:text-2xl lg:text-3xl font-bold text-[#F8FAFC] mb-2">
          How are people talking about AI companions?
        </h1>
        <p className="text-sm sm:text-base text-[#94A3B8] line-clamp-2 sm:line-clamp-none">
          {summary.themeName && summary.themeColor ? (
            <>
              {summary.text.split(summary.themeName).map((part, i, arr) =>
                i < arr.length - 1 ? (
                  <span key={i}>
                    {part}
                    <span style={{ color: summary.themeColor! }}>
                      {summary.themeName}
                    </span>
                  </span>
                ) : (
                  <span key={i}>{part}</span>
                ),
              )}
            </>
          ) : (
            summary.text
          )}
        </p>
      </div>

      {/* Time range selector + chart mode toggle */}
      <div className="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-0 mb-4">
        <div className="flex gap-1">
          {(["6M", "1Y", "2Y", "ALL"] as TimeRange[]).map((range) => (
            <button
              key={range}
              onClick={() => {
                setTimeRange(range);
                if (range === "ALL" && userModeRef.current === "absolute") {
                  setChartMode("relative");
                  setAutoSwitched(true);
                } else if (range !== "ALL" && autoSwitched) {
                  setChartMode(userModeRef.current);
                  setAutoSwitched(false);
                }
              }}
              className="flex-1 sm:flex-none h-11 sm:h-auto px-3 py-1 text-xs font-medium rounded-md transition-colors"
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
        <div className="hidden sm:block flex-1" />
        <div className="flex flex-col items-end gap-1">
          <div className="grid grid-cols-2 sm:flex gap-1">
            {(["absolute", "relative"] as ChartMode[]).map((mode) => (
              <button
                key={mode}
                onClick={() => {
                  setChartMode(mode);
                  userModeRef.current = mode;
                  setAutoSwitched(false);
                }}
                className="h-11 sm:h-auto px-3 py-1 text-xs font-medium rounded-md transition-colors"
                style={{
                  backgroundColor: chartMode === mode ? "#1A1D27" : "transparent",
                  color: chartMode === mode ? "#F8FAFC" : "#94A3B8",
                  border: `1px solid ${chartMode === mode ? "#2A2D3A" : "transparent"}`,
                }}
              >
                {mode === "absolute" ? "Absolute" : "Relative"}
              </button>
            ))}
          </div>
          {autoSwitched && (
            <span className="text-[10px]" style={{ color: "#94A3B8" }}>
              Showing relative scale for full timeline
            </span>
          )}
        </div>
      </div>

      {/* Metric cards */}
      <div
        className="grid gap-[6px] sm:gap-2 mb-5"
        style={{
          gridTemplateColumns:
            bp === "mobile"
              ? "repeat(2, 1fr)"
              : bp === "tablet"
                ? "repeat(3, 1fr)"
                : "repeat(6, 1fr)",
        }}
      >
        {metricCards.map((card) => {
          const isActive = selected.has(card.id as ThemeId);
          const dimmed = selected.size > 0 && !isActive;

          return (
            <button
              key={card.id}
              onClick={() => toggleTheme(card.id as ThemeId)}
              aria-pressed={isActive}
              aria-label={`${card.label}: ${card.value.toFixed(1)} hits per 1000 posts`}
              className="metric-card text-left rounded-lg cursor-pointer"
              style={{
                backgroundColor: "#1A1D27",
                borderLeft: `3px solid ${card.color}`,
                padding: "12px 10px",
                opacity: dimmed ? 0.5 : 1,
                "--card-color": card.color,
              } as React.CSSProperties}
            >
              <div
                className="text-[11px] leading-tight flex items-center gap-1"
                style={{ color: "#94A3B8" }}
              >
                <span>{card.emoji}</span>
                <span>{card.label}</span>
              </div>
              <div
                className="text-[18px] sm:text-[20px] font-medium leading-tight mt-0.5"
                style={{
                  color: card.color,
                  fontVariantNumeric: "tabular-nums",
                }}
              >
                {card.value.toFixed(1)}
              </div>
              <div
                className="text-[10px] leading-tight"
                style={{ color: "#94A3B8" }}
              >
                hits / 1k posts
              </div>
              <div className="mt-1.5 pointer-events-none">
                <Sparkline
                  data={card.sparklineData}
                  color={card.color}
                  height={sparklineHeight}
                />
              </div>
            </button>
          );
        })}
      </div>

      {/* Chart */}
      <div
        ref={chartRef}
        className="rounded-xl border p-0 sm:p-4 lg:p-6"
        style={{ backgroundColor: "#1A1D27", borderColor: "#2A2D3A" }}
      >
        <div
          className="w-full overflow-hidden"
          style={{ height: chartConfig.height }}
        >
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart
              data={chartData}
              margin={chartConfig.margin}
              onMouseMove={(_state, event) => {
                if (!event || !chartRef.current) return;
                const rect = chartRef.current.getBoundingClientRect();
                mouseYRef.current =
                  event.clientY - rect.top - chartConfig.margin.top;
              }}
            >
              <CartesianGrid
                strokeDasharray="3 3"
                stroke="#2A2D3A"
                vertical={false}
                horizontalPoints={[]}
              />

              <XAxis
                dataKey="date"
                tickFormatter={chartConfig.tickFormatter}
                stroke="#2A2D3A"
                tick={{
                  fill: "#94A3B8",
                  fontSize: bp === "mobile" ? 10 : 12,
                }}
                tickLine={false}
                axisLine={{ stroke: "#2A2D3A" }}
                minTickGap={chartConfig.minTickGap}
              />

              {chartConfig.showYAxis && (
                <YAxis
                  yAxisId="index"
                  domain={[0, yDomainMax]}
                  ticks={
                    chartMode === "relative"
                      ? [25, 50, 75, 100]
                      : undefined
                  }
                  tickFormatter={(v: number) =>
                    chartMode === "absolute"
                      ? v < 10
                        ? v.toFixed(1)
                        : String(Math.round(v))
                      : String(v)
                  }
                  stroke="transparent"
                  tick={{ fill: "#94A3B8", fontSize: 12 }}
                  axisLine={false}
                  tickLine={false}
                  width={chartConfig.yAxisWidth}
                  label={{
                    value:
                      chartMode === "absolute"
                        ? "per 1k posts"
                        : "% of peak",
                    angle: -90,
                    position: "insideLeft",
                    fill: "#94A3B8",
                    fontSize: 10,
                    offset: 4,
                  }}
                />
              )}

              {!chartConfig.showYAxis && (
                <YAxis
                  yAxisId="index"
                  domain={[0, yDomainMax]}
                  hide
                  width={0}
                />
              )}

              <Tooltip
                content={({ active, payload, label }) => {
                  if (!active || !payload?.length || !label) {
                    if (nearestTheme !== null) setNearestTheme(null);
                    return null;
                  }

                  // Filter to selected themes, or use all if none selected
                  const candidates =
                    selected.size > 0
                      ? payload.filter((p) =>
                          selected.has(p.dataKey as ThemeId),
                        )
                      : payload;
                  if (!candidates.length) {
                    if (nearestTheme !== null) setNearestTheme(null);
                    return null;
                  }

                  // Find the single closest theme to cursor Y
                  const cursorY = mouseYRef.current;
                  const plotHeight =
                    chartConfig.height -
                    chartConfig.margin.top -
                    chartConfig.margin.bottom;

                  let closest = candidates[0];
                  let closestDist = Infinity;
                  for (const p of candidates) {
                    const val = (p.value as number) ?? 0;
                    const pixelY =
                      plotHeight - (val / yDomainMax) * plotHeight;
                    const dist = Math.abs(cursorY - pixelY);
                    if (dist < closestDist) {
                      closestDist = dist;
                      closest = p;
                    }
                  }

                  const tid = closest.dataKey as ThemeId;
                  const theme = THEMES.find((t) => t.id === tid);
                  if (!theme) return null;

                  if (nearestTheme !== tid) setNearestTheme(tid);

                  const val =
                    chartMode === "absolute"
                      ? `${(closest.value as number).toFixed(1)} per 1k`
                      : `${Math.round(closest.value as number)}% of peak`;

                  return (
                    <div
                      className="rounded-md px-2.5 py-1.5 text-xs shadow-xl whitespace-nowrap"
                      style={{
                        backgroundColor: "#0F1117",
                        border: "1px solid #2A2D3A",
                      }}
                    >
                      <span style={{ color: "#94A3B8" }}>
                        {formatMonthTick(label as string)}
                      </span>
                      <span style={{ color: "#94A3B8" }}>{" \u00B7 "}</span>
                      <span style={{ color: theme.color }}>
                        {theme.label}
                      </span>
                      <span style={{ color: "#94A3B8" }}>{" \u00B7 "}</span>
                      <span className="text-[#F8FAFC] font-medium">
                        {val}
                      </span>
                    </div>
                  );
                }}
                cursor={false}
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
                  label={
                    chartConfig.showEventLabels
                      ? {
                          value: event.label,
                          position: "insideTopLeft",
                          angle: chartConfig.eventLabelAngle,
                          fill: "#94A3B8",
                          fontSize: 9,
                          offset: 6,
                        }
                      : undefined
                  }
                />
              ))}

              {/* Theme lines */}
              {THEMES.map((theme) => {
                const isSelected = selected.has(theme.id);
                const hasSelection = selected.size > 0;
                const isFaded = hasSelection && !isSelected;
                // Default (no selection): all lines faint at 20% per FRONTEND_DESIGN_SPEC
                const opacity = hasSelection
                  ? isFaded
                    ? 0.2
                    : 1
                  : 0.2;
                const isNearest = nearestTheme === theme.id;
                return (
                  <Line
                    key={theme.id}
                    yAxisId="index"
                    type="monotone"
                    dataKey={theme.id}
                    stroke={theme.color}
                    strokeWidth={
                      isSelected
                        ? chartConfig.strokeActive
                        : chartConfig.strokeInactive
                    }
                    strokeOpacity={opacity}
                    dot={false}
                    activeDot={
                      isNearest
                        ? { r: 4, fill: theme.color, stroke: "#0F1117", strokeWidth: 2 }
                        : false
                    }
                    isAnimationActive={false}
                    legendType="none"
                  />
                );
              })}
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Mobile event list */}
      {bp === "mobile" && visibleEvents.length > 0 && (
        <div className="mt-3">
          {!eventsExpanded ? (
            <button
              onClick={() => setEventsExpanded(true)}
              className="text-xs text-[#94A3B8] hover:text-[#F8FAFC] transition-colors"
            >
              View events ({visibleEvents.length})
            </button>
          ) : (
            <div
              className="rounded-lg p-3 text-xs"
              style={{
                backgroundColor: "#1A1D27",
                border: "1px solid #2A2D3A",
              }}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-[#94A3B8] font-medium">Events</span>
                <button
                  onClick={() => setEventsExpanded(false)}
                  className="text-[#94A3B8] hover:text-[#F8FAFC] transition-colors text-xs"
                >
                  Close
                </button>
              </div>
              <div className="space-y-1.5 max-h-40 overflow-y-auto">
                {visibleEvents.map((event) => (
                  <div key={event.date} className="flex gap-2 text-[#94A3B8]">
                    <span className="text-[#F8FAFC] whitespace-nowrap">
                      {formatMonthTickShort(event.date)}
                    </span>
                    <span>&mdash;</span>
                    <span>{event.label}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
