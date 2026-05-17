"use client";

// Thin client wrapper: lazy-loads the Recharts implementation so Recharts is
// not in the initial JS bundle of the (Server Component) pages that render it.
// ResponsiveContainer cannot server-render at a real width anyway, so ssr:false
// loses nothing — the SSR'd chart is discarded and re-rendered client-side.
import dynamic from "next/dynamic";

const RecoveryChart = dynamic(() => import("./RecoveryChartImpl"), {
  ssr: false,
  // Community legend + event legend + 240px chart.
  loading: () => <div style={{ minHeight: 310 }} />,
});

export default RecoveryChart;
