"use client";

import { useSyncExternalStore } from "react";

// Shows a banner when the data on the page is older than STALE_DAYS.
//
// The age is measured from the data's own end date (site_meta.json
// `date_end`, baked in at build time) against the viewer's clock, so a
// deploy that stops updating still ages in the browser. It deliberately
// does NOT read /status.json: that file's `last_successful_push` is written
// before the push and so always carries the PREVIOUS run's timestamp — one
// run behind — which made the banner flag a healthy site for an hour or
// more every afternoon while that day's deploy was still landing.
//
// Data for day D is published on D (~14:00 UTC). Age is floor(days since
// D 00:00 UTC): 0 on publish day, 1 the next day, 2 only if the following
// day's run has failed to land by midnight UTC.
const STALE_DAYS = 2;

function ageInDays(dataThrough: string): number | null {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(dataThrough)) return null;
  const ms = Date.now() - Date.parse(`${dataThrough}T00:00:00Z`);
  return Number.isNaN(ms) ? null : Math.floor(ms / 86400000);
}

const subscribeNoop = () => () => {};

export default function StaleDataBanner({ dataThrough }: { dataThrough: string }) {
  // Read the viewer's clock only on the client: the server snapshot is null
  // so the prerendered HTML never bakes in a build-time age, and the client
  // fills in the real value after hydration without a state-in-effect hop.
  const ageDays = useSyncExternalStore(
    subscribeNoop,
    () => ageInDays(dataThrough),
    () => null,
  );

  if (ageDays === null || ageDays < STALE_DAYS) return null;

  return (
    <div
      role="status"
      style={{
        background: "#7f1d1d",
        color: "#fef2f2",
        padding: "8px 16px",
        textAlign: "center",
        fontSize: 14,
        lineHeight: 1.4,
      }}
    >
      Data shown runs through {dataThrough} ({ageDays} days ago) &mdash; the
      daily update hasn&apos;t landed since.
    </div>
  );
}
