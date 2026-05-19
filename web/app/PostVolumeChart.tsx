"use client";

// Thin client wrapper: lazy-loads the Recharts implementation so Recharts is
// not in the initial JS bundle of the (Server Component) pages that render it.
// The chart measures its container width on the client, so it cannot
// server-render at a real width anyway — ssr:false loses nothing.
import dynamic from "next/dynamic";

const PostVolumeChart = dynamic(() => import("./PostVolumeChartImpl"), {
  ssr: false,
  // Two stacked panels (r/CharacterAI, then the composition area) at every
  // width — size the placeholder so the page doesn't jump on chart load.
  loading: () => <div className="min-h-[560px]" />,
});

export default PostVolumeChart;
