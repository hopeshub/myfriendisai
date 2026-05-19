"use client";

// Thin client wrapper: lazy-loads the Recharts implementation so Recharts is
// not in the initial JS bundle of the (Server Component) pages that render it.
// The chart measures its container width on the client, so it cannot
// server-render at a real width anyway — ssr:false loses nothing.
import dynamic from "next/dynamic";

const ThemeChart = dynamic(() => import("./ThemeChartImpl"), {
  ssr: false,
  loading: () => <div style={{ minHeight: 370 }} />,
});

export default ThemeChart;
