// ── Event sparkline ──────────────────────────────────────────────────────────
// A small theme-line trace for an event card: the relevant theme's monthly
// per-1k rate, windowed ±6 months around the event, with the event month
// marked by a dashed line. Plain SVG, server-rendered — EventShowcase stays
// out of the JS bundle. Zero-based y-axis so the spike reads honestly.
//
// preserveAspectRatio="none" lets the trace stretch to the card width;
// vectorEffect="non-scaling-stroke" keeps the strokes crisp despite the
// stretch, and the event marker is a vertical line (a circle would distort).

export default function EventSparkline({
  values,
  eventIndex,
  color,
}: {
  values: number[];
  eventIndex: number;
  color: string;
}) {
  const n = values.length;
  if (n < 2) return null;

  const H = 46;
  const pad = 4;
  const max = Math.max(...values, 1);
  const x = (i: number) => (i / (n - 1)) * 100;
  const y = (v: number) => H - pad - (v / max) * (H - pad * 2);

  const line = values
    .map((v, i) => `${x(i).toFixed(2)},${y(v).toFixed(2)}`)
    .join(" ");
  const area = `0,${H} ${line} 100,${H}`;
  const evX = x(eventIndex).toFixed(2);

  return (
    <svg
      width="100%"
      height={H}
      viewBox={`0 0 100 ${H}`}
      preserveAspectRatio="none"
      aria-hidden
      style={{ display: "block", overflow: "visible" }}
    >
      <polygon points={area} fill={color} fillOpacity={0.14} />
      <line
        x1={evX}
        y1={0}
        x2={evX}
        y2={H}
        stroke="#C2974D"
        strokeWidth={1}
        strokeDasharray="3 2"
        strokeOpacity={0.75}
        vectorEffect="non-scaling-stroke"
      />
      <polyline
        points={line}
        fill="none"
        stroke={color}
        strokeWidth={1.75}
        strokeLinejoin="round"
        strokeLinecap="round"
        vectorEffect="non-scaling-stroke"
      />
    </svg>
  );
}
