// ── Activity sparkline ───────────────────────────────────────────────────────
// A tiny inline trend line for the Communities table — one community's monthly
// post volume, normalized to its own min/max so the shape stays readable
// whatever the community's size. Direction-only, like the theme atlas: read the
// shape, not the height. Plain SVG, not Recharts — 26 of these in one table
// must stay light.

export default function Sparkline({
  values,
  width = 76,
  height = 22,
}: {
  values: number[];
  width?: number;
  height?: number;
}) {
  const clean = values?.filter((v) => Number.isFinite(v)) ?? [];
  if (clean.length < 2 || Math.max(...clean) === 0) {
    return (
      <span aria-hidden style={{ color: "#3F4654", fontSize: 12 }}>
        —
      </span>
    );
  }

  const max = Math.max(...clean);
  const min = Math.min(...clean);
  const range = max - min || 1;
  const n = clean.length;
  const pad = 1.5;
  const x = (i: number) => pad + (i / (n - 1)) * (width - pad * 2);
  const y = (v: number) =>
    height - pad - ((v - min) / range) * (height - pad * 2);
  const points = clean
    .map((v, i) => `${x(i).toFixed(1)},${y(v).toFixed(1)}`)
    .join(" ");

  return (
    <svg
      width={width}
      height={height}
      viewBox={`0 0 ${width} ${height}`}
      aria-hidden
      style={{ display: "block", overflow: "visible" }}
    >
      <polyline
        points={points}
        fill="none"
        stroke="#7C9CD0"
        strokeWidth={1.25}
        strokeLinejoin="round"
        strokeLinecap="round"
      />
      <circle cx={x(n - 1)} cy={y(clean[n - 1])} r={1.7} fill="#7C9CD0" />
    </svg>
  );
}
