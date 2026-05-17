"use client";

// Thin client wrapper: lazy-loads the Recharts implementation so Recharts is
// not in the initial JS bundle of the (Server Component) pages that render it.
// ResponsiveContainer cannot server-render at a real width anyway, so ssr:false
// loses nothing — the SSR'd chart is discarded and re-rendered client-side.
import dynamic from "next/dynamic";

const Charts = dynamic(() => import("./ChartsImpl"), {
  ssr: false,
  // Responsive: four metric charts stack on mobile, two-up from sm.
  loading: () => <div className="min-h-[1050px] sm:min-h-[540px]" />,
});

export default Charts;
