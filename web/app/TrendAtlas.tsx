"use client";

import { useCallback, useLayoutEffect, useMemo, useState } from "react";
import Link from "next/link";
import type { ThemeData } from "./themeData";
import { THEMES, EVENTS, type ThemeEvent, type ThemeId, type ThemeMeta } from "./themes";
import { textColor } from "./styles";
import { C, radius } from "@/app/styles";

// ── Trend Atlas: six channels ────────────────────────────────────────────────
// The six themes as six wide, short strips stacked on ONE shared time axis,
// like the channels of a chart recorder. Each strip has its own gain: it is
// scaled to its own range in the current view, and its gutter states that
// range ("full scale N per 1,000") instead of carrying y-axis ticks. Detection
// sensitivity differs ~10x between themes, so a line's height is never
// comparable with another strip's; its shape and timing against the shared
// axis are.
//
// Platform events are vertical marks cutting through all six strips at the
// same x, numbered once above the stack and written out in the legend.
// THEMES order is fixed and intentional — strips are never sorted by value
// (sorting by value would itself imply the cross-theme ranking we forbid).
//
// Hand-built SVG, not Recharts: every strip, the event band and the axis are
// drawn in the same grid column from one measured width and one x-scale, so
// x positions agree to the pixel at every viewport width. Each strip is a
// link to that theme's own page (/theme/[id]).

type TimeRange = "6M" | "1Y" | "2Y" | "ALL";
type NumberedEvent = ThemeEvent & { num: number; idx: number };
type Tick = { idx: number; label: string; major: boolean };
type Hover = { idx: number; theme: ThemeId } | null;

// ── Geometry (px) ────────────────────────────────────────────────────────────
const GUTTER = 176; // desktop left gutter: theme name + full scale
const VALUE_COL = 72; // desktop right column: the month's value
const ROW_H = 76; // desktop strip row, including its 1px top rule
const STRIP_H_MOBILE = 60; // mobile strip, under its own header line
const AXIS_H = 26;
const PAD_X = 6; // first/last month sit this far in from the plot edges
const PAD_TOP = 8; // headroom above full scale, so a peak is never clipped
const PAD_BOTTOM = 1.5; // zero sits on the rule that closes the strip

// ── Colours — palette roles (styles.ts) ──────────────────────────────
const RULE = C.grid; // strip rules (also each strip's zero line)
const GUIDE = C.guide; // very light chart-paper guides
const EVENT = C.event;
const EVENT_TEXT = C.eventText;
const CURSOR = C.cursor;
const BG = C.bg;
// A strip's own background (it lightens on hover), for halos that must
// match whatever is behind them. Set on each strip link below.
const ROW_BG = `var(--strip-bg, ${C.bg})`;
const ROW_CLASS =
  "group [--strip-bg:var(--c-bg)] hover:[--strip-bg:var(--c-surface)] bg-[var(--strip-bg)] transition-colors";

const MONTH_NAMES = [
  "Jan", "Feb", "Mar", "Apr", "May", "Jun",
  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
];

function fmtMonth(d: string): string {
  const dt = new Date(d + "T00:00:00Z");
  return `${MONTH_NAMES[dt.getUTCMonth()]} ${dt.getUTCFullYear()}`;
}

function fmtMonthShort(d: string): string {
  const dt = new Date(d + "T00:00:00Z");
  return `${MONTH_NAMES[dt.getUTCMonth()]} '${String(dt.getUTCFullYear()).slice(2)}`;
}

/** Bucket the series by month. loadThemeData already emits one pooled point
 *  per month, so this is a pass-through; it stays so the component still
 *  behaves if it is ever handed a daily series. */
function monthlySeries(
  points: { date: string; hitsPerK: number }[],
): { date: string; value: number }[] {
  const buckets: Record<string, { sum: number; n: number }> = {};
  for (const p of points) {
    const m = p.date.slice(0, 7) + "-01";
    if (!buckets[m]) buckets[m] = { sum: 0, n: 0 };
    buckets[m].sum += p.hitsPerK;
    buckets[m].n += 1;
  }
  return Object.keys(buckets)
    .sort()
    .map((m) => ({ date: m, value: buckets[m].sum / buckets[m].n }));
}

// Full scale is the visible maximum rounded up to a round number, so the
// gutter reads "full scale 9", not "full scale 8.37".
const NICE_STEPS = [1, 1.2, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10];
function niceCeil(v: number): number {
  if (!(v > 0)) return 1;
  const p = Math.pow(10, Math.floor(Math.log10(v)));
  const step = NICE_STEPS.find((s) => s >= v / p - 1e-9) ?? 10;
  return Number((step * p).toPrecision(3));
}

function fmtScale(v: number): string {
  return v >= 10 ? Math.round(v).toLocaleString("en-US") : String(v);
}

/** The one x-scale every strip, the event band and the axis share: month i
 *  of n across a plot `plotW` px wide. */
function xScale(n: number, plotW: number): (i: number) => number {
  return (i) => (n > 1 ? PAD_X + (i * (plotW - 2 * PAD_X)) / (n - 1) : plotW / 2);
}

/** Rough advance width of a label, for collision checks only. */
function textWidth(s: string, px: number): number {
  return s.length * px * 0.58;
}

/** Axis ticks for the view: years for ALL, quarters for 2Y/1Y, months for
 *  6M. A January tick is labelled with its year; the first tick of a view
 *  that does not start in January carries its year too. */
function buildTicks(months: string[], range: TimeRange): Tick[] {
  const every = range === "ALL" ? 12 : range === "6M" ? 1 : 3;
  const out: Tick[] = [];
  months.forEach((m, idx) => {
    const mm = Number(m.slice(5, 7));
    if ((mm - 1) % every !== 0) return;
    const major = mm === 1;
    const name = MONTH_NAMES[mm - 1];
    const label = major ? m.slice(0, 4) : out.length === 0 ? `${name} ${m.slice(0, 4)}` : name;
    out.push({ idx, label, major });
  });
  return out;
}

/** Measure an element's width (sub-pixel) before first paint and keep it in
 *  sync — the same approach as MeasuredChart, for a box whose height is set
 *  by its own content. */
function useWidth(): [(el: HTMLDivElement | null) => void, number] {
  const [el, setEl] = useState<HTMLDivElement | null>(null);
  const [width, setWidth] = useState(0);
  useLayoutEffect(() => {
    if (!el) return;
    const measure = () => {
      const w = el.getBoundingClientRect().width;
      setWidth((prev) => (Math.abs(prev - w) < 0.01 ? prev : w));
    };
    measure();
    const observer = new ResizeObserver(measure);
    observer.observe(el);
    return () => observer.disconnect();
  }, [el]);
  return [setEl, width];
}

// ── Event legend ─────────────────────────────────────────────────────────────
// Events visible in the selected range are numbered 1..n in chronological
// order, so the legend never shows a gap (e.g. "3, 4, 5"). Numbers re-index
// when the range changes — the legend and the marker band update together.
function EventLegend({
  events,
  mobile,
  style,
}: {
  events: NumberedEvent[];
  mobile: boolean;
  style?: React.CSSProperties;
}) {
  const hasMethodology = events.some((e) => e.methodology);
  // ≤768px: 14px mobile font floor.
  const fs = mobile ? 14 : 12;
  const smallFs = mobile ? 14 : 11;
  return (
    <div style={style}>
      <div
        style={{ display: "flex", flexWrap: "wrap", gap: "6px 16px", alignItems: "center" }}
      >
        <span style={{ fontSize: smallFs, color: textColor.caption }}>Events</span>
        {events.map((e) => (
          <span
            key={e.date}
            style={{ display: "inline-flex", alignItems: "center", gap: 6, fontSize: fs }}
          >
            <span
              aria-hidden
              style={{
                display: "inline-flex",
                alignItems: "center",
                justifyContent: "center",
                width: mobile ? 20 : 16,
                height: mobile ? 20 : 16,
                borderRadius: 999,
                fontSize: smallFs === 14 ? 12 : 11,
                fontWeight: 700,
                flexShrink: 0,
                color: e.methodology ? EVENT_TEXT : BG,
                backgroundColor: e.methodology ? "transparent" : EVENT,
                border: e.methodology ? `1px dashed ${EVENT}` : "none",
              }}
            >
              {e.num}
            </span>
            <span style={{ color: textColor.body }}>{e.label}</span>
            <span style={{ color: textColor.caption }}>{fmtMonthShort(e.date)}</span>
          </span>
        ))}
      </div>
      {hasMethodology && (
        <div style={{ fontSize: smallFs, color: textColor.caption, marginTop: 6 }}>
          A hollow marker is a change to the keyword set, applied back across
          the whole record — a measurement change, not a real-world event.
        </div>
      )}
    </div>
  );
}

// ── Event marker band ────────────────────────────────────────────────────────
// One numbered marker per event, above the stack, at the exact x of its mark.
// Markers that would touch are lifted to a second row, so numbers never
// collide even on a phone showing the whole record.
function EventBand({
  events,
  xOf,
  plotW,
  mobile,
}: {
  events: NumberedEvent[];
  xOf: (i: number) => number;
  plotW: number;
  mobile: boolean;
}) {
  const size = mobile ? 20 : 16;
  const stem = 6;
  const r = size / 2;
  const placed: { e: NumberedEvent; x: number; cx: number; row: number }[] = [];
  const lastRight = [-Infinity, -Infinity];
  for (const e of events) {
    const x = Math.round(xOf(e.idx)) + 0.5;
    // Keep the whole marker inside the plot; the stem stays on the true x.
    const cx = Math.min(Math.max(x, r), plotW - r);
    const row = cx - r >= lastRight[0] + 3 ? 0 : cx - r >= lastRight[1] + 3 ? 1 : 0;
    lastRight[row] = cx + r;
    placed.push({ e, x, cx, row });
  }
  const rows = placed.some((p) => p.row === 1) ? 2 : 1;
  const height = rows * (size + 4) + stem;
  if (!plotW) return <div style={{ height }} />;
  return (
    <svg
      width={plotW}
      height={height}
      style={{ display: "block", overflow: "visible" }}
      aria-hidden
    >
      {placed.map(({ e, x, cx, row }) => {
        const cy = height - stem - r - 2 - row * (size + 4);
        return (
          <g key={e.date}>
            <line
              x1={x}
              x2={x}
              y1={cy + r}
              y2={height}
              stroke={EVENT}
              strokeOpacity={0.7}
              strokeDasharray={e.methodology ? "2 3" : "5 3"}
            />
            <circle
              cx={cx}
              cy={cy}
              r={e.methodology ? r - 0.5 : r}
              fill={e.methodology ? BG : EVENT}
              stroke={e.methodology ? EVENT : "none"}
              strokeDasharray={e.methodology ? "2 2" : undefined}
            />
            <text
              x={cx}
              y={cy}
              textAnchor="middle"
              dominantBaseline="central"
              fontSize={mobile ? 12 : 11}
              fontWeight={700}
              fill={e.methodology ? EVENT_TEXT : BG}
            >
              {e.num}
            </text>
          </g>
        );
      })}
    </svg>
  );
}

// ── Shared time axis ─────────────────────────────────────────────────────────
function TimeAxis({
  ticks,
  xOf,
  plotW,
  overhang,
}: {
  ticks: Tick[];
  xOf: (i: number) => number;
  plotW: number;
  /** How far a label may run past the plot's right edge (into the empty
   *  value column on desktop; none on mobile). */
  overhang: number;
}) {
  if (!plotW) return null;
  const fs = 11;
  // Labels start just right of their tick; one that would run off the right
  // end is set to end at its tick instead. Then drop labels that would
  // collide, letting a year win over a month.
  const laid = ticks.map((t) => {
    const x = Math.round(xOf(t.idx)) + 0.5;
    const w = textWidth(t.label, fs);
    const fitsRight = x + 3 + w <= plotW + overhang;
    const anchor: "start" | "end" = fitsRight ? "start" : "end";
    return { ...t, x, w, left: fitsRight ? x + 3 : x - 3 - w, anchor };
  });
  const shown: typeof laid = [];
  for (const t of laid) {
    const prev = shown[shown.length - 1];
    if (prev && t.left < prev.left + prev.w + 8) {
      if (t.major && !prev.major) shown[shown.length - 1] = t;
      continue;
    }
    shown.push(t);
  }
  return (
    <svg
      width={plotW}
      height={AXIS_H}
      style={{ display: "block", overflow: "visible" }}
      aria-hidden
    >
      {laid.map((t) => (
        <line key={t.idx} x1={t.x} x2={t.x} y1={0} y2={4} stroke={RULE} />
      ))}
      {shown.map((t) => (
        <text
          key={t.idx}
          x={t.anchor === "start" ? t.x + 3 : t.x - 3}
          y={16}
          textAnchor={t.anchor}
          fontSize={fs}
          fill={textColor.caption}
        >
          {t.label}
        </text>
      ))}
    </svg>
  );
}

// ── One channel ──────────────────────────────────────────────────────────────
type StripModel = {
  theme: ThemeMeta;
  values: (number | null)[];
  /** First month index the theme is measurable in this view (n if none). */
  startIdx: number;
  fullScale: number;
};

function StripPlot({
  model,
  months,
  events,
  ticks,
  xOf,
  plotW,
  height,
  hover,
  onHover,
  mobile,
}: {
  model: StripModel;
  months: string[];
  events: NumberedEvent[];
  ticks: Tick[];
  xOf: (i: number) => number;
  plotW: number;
  height: number;
  hover: Hover;
  onHover: (h: Hover) => void;
  mobile: boolean;
}) {
  const { theme, values, startIdx, fullScale } = model;
  const n = months.length;
  const yOf = (v: number) =>
    PAD_TOP + (1 - v / fullScale) * (height - PAD_TOP - PAD_BOTTOM);

  // The trace: a path broken at every missing month (a hole in the record is
  // not a quiet month), with a dot for any month that stands alone.
  const { d, dots } = useMemo(() => {
    const scaleX = xScale(n, plotW);
    const scaleY = (v: number) =>
      PAD_TOP + (1 - v / fullScale) * (height - PAD_TOP - PAD_BOTTOM);
    let path = "";
    const lone: [number, number][] = [];
    for (let i = 0; i < n; i++) {
      const v = values[i];
      if (v == null) continue;
      const prevNull = i === 0 || values[i - 1] == null;
      const nextNull = i === n - 1 || values[i + 1] == null;
      const x = scaleX(i);
      const y = scaleY(v);
      if (prevNull && nextNull) lone.push([x, y]);
      path += `${prevNull ? "M" : "L"}${x.toFixed(2)},${y.toFixed(2)}`;
    }
    return { d: path, dots: lone };
  }, [values, n, plotW, height, fullScale]);

  if (!plotW) return <div style={{ height }} />;

  const startX = startIdx < n ? xOf(startIdx) : plotW;
  const snap = (x: number) => Math.round(x) + 0.5;
  const plotH = height - PAD_TOP - PAD_BOTTOM;

  // The blank before a theme becomes measurable is left blank — no guides, no
  // zero line — with a note at its edge when there is room for one.
  let blankLabel: string | null = null;
  if (startIdx > 0 && startIdx < n) {
    const room = startX - PAD_X - 8;
    for (const s of [
      `measurable from ${fmtMonth(months[startIdx])}`,
      `from ${fmtMonthShort(months[startIdx])}`,
    ]) {
      if (textWidth(s, 11) <= room) {
        blankLabel = s;
        break;
      }
    }
  }

  const hi = hover?.idx ?? null;
  const hv = hi != null ? values[hi] : null;
  const isHovered = hover?.theme === theme.id;

  const handleMove = (e: React.PointerEvent<HTMLDivElement>) => {
    if (e.pointerType === "touch" || n === 0) return;
    const rect = e.currentTarget.getBoundingClientRect();
    const x = ((e.clientX - rect.left) * plotW) / rect.width;
    const step = n > 1 ? (plotW - 2 * PAD_X) / (n - 1) : 1;
    const idx = Math.min(n - 1, Math.max(0, Math.round((x - PAD_X) / step)));
    if (hover?.idx !== idx || hover?.theme !== theme.id) onHover({ idx, theme: theme.id });
  };

  // Tooltip: month + value + units, beside the cursor, flipped to the cursor's
  // left past mid-strip, and above/below the point so it never sits on it.
  let tooltip: React.ReactNode = null;
  if (isHovered && hi != null) {
    const x = xOf(hi);
    const flip = x > plotW * 0.6;
    const pointHigh = hv != null && yOf(hv) < height / 2;
    tooltip = (
      <div
        style={{
          position: "absolute",
          left: x,
          top: pointHigh ? undefined : 2,
          bottom: pointHigh ? 2 : undefined,
          transform: flip ? "translateX(calc(-100% - 10px))" : "translateX(10px)",
          backgroundColor: BG,
          border: `1px solid ${RULE}`,
          borderRadius: radius(6),
          padding: "3px 8px",
          fontSize: mobile ? 14 : 12,
          whiteSpace: "nowrap",
          pointerEvents: "none",
          zIndex: 10,
        }}
      >
        <span style={{ color: textColor.lead }}>{fmtMonth(months[hi])}</span>
        <span style={{ color: textColor.lead }}>{"  ·  "}</span>
        {hv != null ? (
          <>
            <span style={{ color: textColor.heading, fontWeight: 600 }}>
              {hv.toFixed(1)}
            </span>
            <span style={{ color: textColor.lead }}> per 1,000 posts</span>
          </>
        ) : (
          <span style={{ color: textColor.lead }}>
            {hi < startIdx ? "not yet measurable" : "no record this month"}
          </span>
        )}
      </div>
    );
  }

  return (
    <div
      style={{ position: "relative", height }}
      onPointerMove={handleMove}
      onPointerLeave={() => onHover(null)}
    >
      <svg
        width={plotW}
        height={height}
        style={{ display: "block", overflow: "visible" }}
        aria-hidden
      >
        {/* Chart paper: quarter guides across the measured part only. */}
        {startIdx < n &&
          [0.25, 0.5, 0.75].map((f) => (
            <line
              key={f}
              x1={startX}
              x2={plotW}
              y1={Math.round(PAD_TOP + (1 - f) * plotH) + 0.5}
              y2={Math.round(PAD_TOP + (1 - f) * plotH) + 0.5}
              stroke={GUIDE}
            />
          ))}
        {ticks
          .filter((t) => t.idx >= startIdx)
          .map((t) => (
            <line
              key={t.idx}
              x1={snap(xOf(t.idx))}
              x2={snap(xOf(t.idx))}
              y1={0}
              y2={height}
              stroke={GUIDE}
            />
          ))}
        {startIdx > 0 && startIdx < n && (
          <line
            x1={snap(startX)}
            x2={snap(startX)}
            y1={0}
            y2={height}
            stroke={RULE}
            strokeDasharray="1 3"
          />
        )}
        {/* Events cut through every strip at the same x. */}
        {events.map((e) => (
          <line
            key={e.date}
            x1={snap(xOf(e.idx))}
            x2={snap(xOf(e.idx))}
            y1={0}
            y2={height}
            stroke={EVENT}
            strokeOpacity={0.7}
            strokeDasharray={e.methodology ? "2 3" : "5 3"}
          />
        ))}
        {/* Over the event marks, on a halo of background, so a mark that
            crosses the blank never strikes through the note. */}
        {blankLabel && (
          <text
            x={startX - 6}
            y={height / 2}
            textAnchor="end"
            dominantBaseline="central"
            fontSize={11}
            fill={textColor.caption}
            strokeWidth={4}
            strokeLinejoin="round"
            paintOrder="stroke"
            style={{ stroke: ROW_BG }}
          >
            {blankLabel}
          </text>
        )}
        {hi != null && (
          <line
            x1={snap(xOf(hi))}
            x2={snap(xOf(hi))}
            y1={0}
            y2={height}
            stroke={CURSOR}
          />
        )}
        <path
          d={d}
          fill="none"
          stroke={theme.color}
          strokeWidth={1.5}
          strokeLinejoin="round"
          strokeLinecap="round"
        />
        {dots.map(([x, y]) => (
          <circle key={x} cx={x} cy={y} r={1.75} fill={theme.color} />
        ))}
        {hi != null && hv != null && (
          <circle
            cx={xOf(hi)}
            cy={yOf(hv)}
            r={3.5}
            fill={theme.color}
            strokeWidth={1.5}
            style={{ stroke: ROW_BG }}
          />
        )}
      </svg>
      {tooltip}
    </div>
  );
}

export default function TrendAtlas({
  themeData,
  timeRange,
  isMobileStrip: mobile,
}: {
  themeData: ThemeData;
  timeRange: TimeRange;
  /** ≤768px — gutter stacks above each strip; 14px mobile font floor. */
  isMobileStrip: boolean;
}) {
  // The hovered month, tagged with the month domain it was set in (below).
  const [hoverState, setHoverState] = useState<{ hover: Hover; domain: string }>({
    hover: null,
    domain: "",
  });
  const [measureRef, plotW] = useWidth();

  // Each theme's monthly series and the shared month domain for the view.
  const { perTheme, months } = useMemo(() => {
    const series: Record<string, { date: string; value: number }[]> = {};
    const monthSet = new Set<string>();
    for (const t of THEMES) {
      const s = monthlySeries(themeData[t.id] ?? []);
      series[t.id] = s;
      for (const r of s) monthSet.add(r.date);
    }
    let domain = [...monthSet].sort();
    if (timeRange !== "ALL" && domain.length) {
      const back = timeRange === "2Y" ? 24 : timeRange === "1Y" ? 12 : 6;
      const last = new Date(domain[domain.length - 1] + "T00:00:00Z");
      last.setUTCMonth(last.getUTCMonth() - back);
      const cutoff = last.toISOString().slice(0, 10);
      domain = domain.filter((m) => m >= cutoff);
    }
    return { perTheme: series, months: domain };
  }, [themeData, timeRange]);

  const n = months.length;

  // Per-strip model: values aligned to the shared months, where the theme
  // becomes measurable, and the strip's own full scale for this view.
  const strips: StripModel[] = useMemo(
    () =>
      THEMES.map((theme) => {
        const series = perTheme[theme.id] ?? [];
        const byDate: Record<string, number> = {};
        for (const r of series) byDate[r.date] = r.value;
        const themeStart = series[0]?.date;
        const startIdx = themeStart ? months.findIndex((m) => m >= themeStart) : -1;
        const values = months.map((m) =>
          themeStart && m >= themeStart ? (byDate[m] ?? null) : null,
        );
        const max = Math.max(0, ...values.map((v) => v ?? 0));
        return {
          theme,
          values,
          startIdx: startIdx < 0 ? n : startIdx,
          fullScale: niceCeil(max),
        };
      }),
    [perTheme, months, n],
  );

  // Events inside the visible window, numbered 1..n in order. Compare at
  // month granularity: the axis holds "YYYY-MM-01" values, so a full-date
  // compare drops any event after the 1st of the latest month.
  const events: NumberedEvent[] = useMemo(() => {
    if (!n) return [];
    const first = months[0].slice(0, 7);
    const last = months[n - 1].slice(0, 7);
    return EVENTS.filter((e) => e.date.slice(0, 7) >= first && e.date.slice(0, 7) <= last)
      .map((e) => ({ e, idx: months.indexOf(`${e.date.slice(0, 7)}-01`) }))
      .filter(({ idx }) => idx >= 0)
      .map(({ e, idx }, i) => ({ ...e, num: i + 1, idx }));
  }, [months, n]);

  const ticks = useMemo(() => buildTicks(months, timeRange), [months, timeRange]);

  const xOf = xScale(n, plotW);

  // A hover index only means something in the month domain it was set in.
  // Changing the time range or scope reshapes `months` without moving the
  // mouse, and a stale index pointed past the end of the shorter domain
  // (months[readIdx] was undefined and the homepage fell to the error
  // boundary). So a hover is tagged with its domain and ignored once the
  // domain changes; the next pointer move sets a fresh one.
  const domain = n ? `${months[0]}|${months[n - 1]}|${n}` : "";
  const setHover = useCallback(
    (h: Hover) => setHoverState({ hover: h, domain }),
    [domain],
  );
  const liveHover: Hover =
    hoverState.domain === domain && hoverState.hover && hoverState.hover.idx < n
      ? hoverState.hover
      : null;

  // The right-hand figures follow the cursor: the hovered month's values
  // across all six strips, or the latest month when nothing is hovered.
  const readIdx = liveHover?.idx ?? n - 1;
  const readMonth = n ? fmtMonth(months[readIdx]) : "";
  const fmtValue = (v: number | null) => (v == null ? "–" : v.toFixed(1));

  const describe = (s: StripModel) => {
    const from = s.startIdx < n ? fmtMonth(months[s.startIdx]) : null;
    const latest = s.values[n - 1];
    return from
      ? `${s.theme.label}: validated-keyword mentions per 1,000 posts, by month, ${from} to ${fmtMonth(months[n - 1])}, on its own scale (full scale ${fmtScale(s.fullScale)} per 1,000). ${fmtMonth(months[n - 1])}: ${latest == null ? "no record" : latest.toFixed(1)}. ${s.theme.blurb}`
      : `${s.theme.label}: not yet measurable in this time range. ${s.theme.blurb}`;
  };

  const grid = `${GUTTER}px minmax(0, 1fr) ${VALUE_COL}px`;

  return (
    <div>
      {!mobile && events.length > 0 && (
        <EventLegend events={events} mobile={false} style={{ marginBottom: 14 }} />
      )}

      {/* Marker band: event numbers once, above the stack. On desktop the
          right column heads the figures below it with their month. */}
      <div
        style={
          mobile
            ? undefined
            : { display: "grid", gridTemplateColumns: grid, alignItems: "end" }
        }
      >
        {!mobile && <div />}
        <div>
          <EventBand events={events} xOf={xOf} plotW={plotW} mobile={mobile} />
        </div>
        {!mobile && (
          <div
            style={{
              paddingLeft: 12,
              paddingBottom: 4,
              fontSize: 12,
              lineHeight: "16px",
              color: liveHover ? textColor.body : textColor.caption,
              whiteSpace: "nowrap",
            }}
          >
            {readMonth}
          </div>
        )}
      </div>

      {strips.map((s) => {
        const value = s.values[readIdx] ?? null;
        const scaleText =
          s.startIdx < n
            ? `full scale ${fmtScale(s.fullScale)} per 1,000`
            : "not measurable in this range";
        const plot = (
          <StripPlot
            model={s}
            months={months}
            events={events}
            ticks={ticks}
            xOf={xOf}
            plotW={plotW}
            height={mobile ? STRIP_H_MOBILE : ROW_H - 1}
            hover={liveHover}
            onHover={setHover}
            mobile={mobile}
          />
        );
        const descId = `atlas-strip-${s.theme.id}`;
        const common = {
          href: `/theme/${s.theme.id}`,
          "aria-label": `${s.theme.label} — open theme page`,
          "aria-describedby": descId,
        };
        const desc = (
          <span id={descId} className="sr-only">
            {describe(s)}
          </span>
        );

        if (mobile) {
          return (
            <Link
              key={s.theme.id}
              {...common}
              className={`${ROW_CLASS} block`}
              style={{ borderTop: `1px solid ${RULE}` }}
            >
              {desc}
              <div
                className="flex items-baseline"
                style={{ gap: 8, paddingTop: 6, paddingBottom: 2, minHeight: 26 }}
              >
                <span style={{ fontSize: 14, fontWeight: 600, color: s.theme.color }}>
                  {s.theme.label}
                </span>
                <span style={{ fontSize: 12, color: textColor.caption }}>{scaleText}</span>
                <span className="ml-auto" style={{ whiteSpace: "nowrap" }}>
                  <span style={{ fontSize: 12, color: textColor.caption }}>
                    {n ? MONTH_NAMES[Number(months[readIdx].slice(5, 7)) - 1] : ""}{" "}
                  </span>
                  <span
                    style={{
                      fontSize: 14,
                      fontWeight: 500,
                      color: textColor.heading,
                      fontVariantNumeric: "tabular-nums",
                    }}
                  >
                    {fmtValue(value)}
                  </span>
                </span>
              </div>
              {plot}
            </Link>
          );
        }

        return (
          <Link
            key={s.theme.id}
            {...common}
            className={`${ROW_CLASS} grid`}
            style={{
              gridTemplateColumns: grid,
              height: ROW_H,
              borderTop: `1px solid ${RULE}`,
            }}
          >
            {desc}
            <div style={{ padding: "10px 16px 0 8px", minWidth: 0 }}>
              <div
                style={{
                  fontSize: 16,
                  fontWeight: 600,
                  lineHeight: "20px",
                  color: s.theme.color,
                  whiteSpace: "nowrap",
                }}
              >
                {s.theme.label}
                <span
                  aria-hidden
                  className="transition-colors group-hover:text-[var(--c-body)]"
                  style={{ marginLeft: 6, fontSize: 13, fontWeight: 400, color: textColor.caption }}
                >
                  &rarr;
                </span>
              </div>
              <div
                style={{
                  marginTop: 3,
                  fontSize: 12,
                  lineHeight: "16px",
                  color: textColor.caption,
                  whiteSpace: "nowrap",
                }}
              >
                {scaleText}
              </div>
            </div>
            {plot}
            <div
              style={{
                paddingLeft: 12,
                paddingTop: 10,
                fontSize: 16,
                lineHeight: "20px",
                fontWeight: 500,
                color: textColor.heading,
                fontVariantNumeric: "tabular-nums",
              }}
            >
              {fmtValue(value)}
            </div>
          </Link>
        );
      })}

      {/* Shared time axis, drawn once. Its plot cell is the one measured: it
          sits in the same column as every strip, so they share its width. */}
      <div
        style={{
          borderTop: `1px solid ${RULE}`,
          ...(mobile ? {} : { display: "grid", gridTemplateColumns: grid }),
        }}
      >
        {!mobile && <div />}
        <div ref={measureRef} style={{ height: AXIS_H, minWidth: 0 }}>
          <TimeAxis
            ticks={ticks}
            xOf={xOf}
            plotW={plotW}
            overhang={mobile ? 0 : VALUE_COL - 8}
          />
        </div>
        {!mobile && <div />}
      </div>

      {mobile && events.length > 0 && (
        <EventLegend events={events} mobile style={{ marginTop: 14 }} />
      )}
    </div>
  );
}
