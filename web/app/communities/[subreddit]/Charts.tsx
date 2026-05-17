"use client";

// Thin client wrapper: lazy-loads the Recharts implementation so Recharts is
// not in the initial JS bundle of the (Server Component) pages that render it.
// ResponsiveContainer cannot server-render at a real width anyway, so ssr:false
// loses nothing — the SSR'd chart is discarded and re-rendered client-side.
import dynamic from "next/dynamic";

const Charts = dynamic(() => import("./ChartsImpl"), {
  ssr: false,
  // Responsive: stat cards + three metric charts that stack until lg,
  // then sit three-up. Sized to the post-monthly-aggregation layout.
  loading: () => <div className="min-h-[860px] lg:min-h-[400px]" />,
});

export default Charts;
