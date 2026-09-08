"use client";

// Thin client wrapper: lazy-loads the Recharts implementation so Recharts is
// not in the homepage's initial JS bundle. The chart measures its container
// width on the client, so ssr:false loses nothing.
import dynamic from "next/dynamic";

const AmbientChart = dynamic(() => import("./AmbientChartImpl"), {
  ssr: false,
  // Top line panel + bottom stacked panel. Heights measured in the production
  // build at 390 / 640 / 768 / 1280 so the placeholder matches what loads.
  loading: () => (
    <div className="min-h-[860px] sm:min-h-[780px] md:min-h-[745px] lg:min-h-[730px]" />
  ),
});

export default AmbientChart;
