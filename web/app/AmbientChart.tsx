"use client";

// Thin client wrapper: lazy-loads the Recharts implementation so Recharts is
// not in the homepage's initial JS bundle. The chart measures its container
// width on the client, so ssr:false loses nothing.
import dynamic from "next/dynamic";

const AmbientChart = dynamic(() => import("./AmbientChartImpl"), {
  ssr: false,
  // Top line panel + bottom stacked panel — keep the page from jumping on load.
  loading: () => <div className="min-h-[560px]" />,
});

export default AmbientChart;
