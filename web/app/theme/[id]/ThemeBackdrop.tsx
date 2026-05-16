"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

/**
 * Theme-page shell. The centered content column sits inside a full-width
 * backdrop; clicking the empty side margins around it — or pressing Escape —
 * navigates back to the homepage atlas, a lightbox-style dismiss.
 *
 * The "← All themes" link and the bottom theme nav remain the primary,
 * keyboard-friendly way back; this is an additional convenience.
 */
export default function ThemeBackdrop({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();

  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if (e.key === "Escape") router.push("/");
    }
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [router]);

  return (
    <div
      // Only a click that lands on the backdrop itself (the side margins),
      // not on the content column, dismisses.
      onClick={(e) => {
        if (e.target === e.currentTarget) router.push("/");
      }}
      style={{ cursor: "pointer" }}
    >
      <div
        className="max-w-[720px] mx-auto px-4 sm:px-8 py-8"
        style={{ cursor: "auto" }}
      >
        {children}
      </div>
    </div>
  );
}
