"use client";

import { useEffect } from "react";

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <main style={{
      minHeight: "60vh",
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      justifyContent: "center",
      padding: "2rem",
      textAlign: "center",
      gap: "1rem",
    }}>
      <h1 style={{ fontSize: "1.5rem", fontWeight: 600 }}>Something went wrong</h1>
      <p style={{ opacity: 0.7, maxWidth: "40ch" }}>
        The page hit an unexpected error while loading. Try again — if it keeps happening, the daily data export may be mid-update.
      </p>
      <button
        onClick={reset}
        style={{
          padding: "0.5rem 1rem",
          border: "1px solid currentColor",
          borderRadius: "0.375rem",
          background: "transparent",
          color: "inherit",
          cursor: "pointer",
          minHeight: "44px",
        }}
      >
        Try again
      </button>
    </main>
  );
}
