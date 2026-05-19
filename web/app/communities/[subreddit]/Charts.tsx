"use client";

// Thin client wrapper: lazy-loads the Recharts implementation so Recharts is
// not in the initial JS bundle of the (Server Component) pages that render it.
// The chart measures its container width on the client, so it cannot
// server-render at a real width anyway — ssr:false loses nothing.
import dynamic from "next/dynamic";

const Charts = dynamic(() => import("./ChartsImpl"), {
  ssr: false,
  // Responsive: stat cards + three metric charts that stack until lg,
  // then sit three-up. Sized to the post-monthly-aggregation layout.
  loading: () => <div className="min-h-[860px] lg:min-h-[400px]" />,
});

export default Charts;
