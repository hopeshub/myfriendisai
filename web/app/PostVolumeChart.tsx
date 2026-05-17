"use client";

// Thin client wrapper: lazy-loads the Recharts implementation so Recharts is
// not in the initial JS bundle of the (Server Component) pages that render it.
// ResponsiveContainer cannot server-render at a real width anyway, so ssr:false
// loses nothing — the SSR'd chart is discarded and re-rendered client-side.
import dynamic from "next/dynamic";

const PostVolumeChart = dynamic(() => import("./PostVolumeChartImpl"), {
  ssr: false,
  // Responsive: two stacked panels on mobile, side-by-side from sm up — size
  // the placeholder per breakpoint so the page doesn't jump on chart load.
  loading: () => <div className="min-h-[560px] sm:min-h-[300px]" />,
});

export default PostVolumeChart;
