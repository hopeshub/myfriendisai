"use client";

import { useEffect, useState } from "react";

type Status = {
  last_collection: string | null;
  last_successful_push: string | null;
  consecutive_push_failures?: number;
  last_push_error?: string | null;
};

const STALE_DAYS = 2;

export default function StaleDataBanner() {
  const [ageDays, setAgeDays] = useState<number | null>(null);
  const [lastRun, setLastRun] = useState<string | null>(null);

  useEffect(() => {
    fetch("/status.json", { cache: "no-store" })
      .then((r) => (r.ok ? (r.json() as Promise<Status>) : null))
      .then((d) => {
        // `last_collection` is the run that produced the data deployed with
        // this commit. `last_successful_push` is written after the push, so
        // the published copy always describes the *previous* run and reads a
        // day stale — use it only as a fallback.
        const stamp = d?.last_collection ?? d?.last_successful_push;
        if (!stamp) return;
        const ms = Date.now() - new Date(stamp).getTime();
        setAgeDays(Math.floor(ms / 86400000));
        setLastRun(stamp.slice(0, 10));
      })
      .catch(() => {});
  }, []);

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
      Data shown is {ageDays} days old — the daily pipeline hasn&apos;t
      published since {lastRun}.
    </div>
  );
}
