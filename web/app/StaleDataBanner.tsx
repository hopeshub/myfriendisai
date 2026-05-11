"use client";

import { useEffect, useState } from "react";

type Status = {
  last_successful_push: string | null;
  consecutive_push_failures?: number;
  last_push_error?: string | null;
};

const STALE_DAYS = 2;

export default function StaleDataBanner() {
  const [ageDays, setAgeDays] = useState<number | null>(null);
  const [lastPush, setLastPush] = useState<string | null>(null);

  useEffect(() => {
    fetch("/status.json", { cache: "no-store" })
      .then((r) => (r.ok ? (r.json() as Promise<Status>) : null))
      .then((d) => {
        if (!d?.last_successful_push) return;
        const ms = Date.now() - new Date(d.last_successful_push).getTime();
        setAgeDays(Math.floor(ms / 86400000));
        setLastPush(d.last_successful_push.slice(0, 10));
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
      successfully published since {lastPush}.
    </div>
  );
}
