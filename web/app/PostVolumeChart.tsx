"use client";

// Thin client wrapper: lazy-loads the Recharts implementation so Recharts is
// not in the initial JS bundle of the (Server Component) pages that render it.
// The chart measures its container width on the client, so it cannot
// server-render at a real width anyway — ssr:false loses nothing.
import dynamic from "next/dynamic";

const PostVolumeChart = dynamic(() => import("./PostVolumeChartImpl"), {
  ssr: false,
  // Two stacked panels (r/CharacterAI, then the composition area) at every
  // width. Heights measured in the production build at 390 / 640 / 768 / 1280
  // so the placeholder matches what loads.
  loading: () => (
    <div className="min-h-[790px] sm:min-h-[675px] md:min-h-[660px] lg:min-h-[635px]" />
  ),
});

export default PostVolumeChart;
