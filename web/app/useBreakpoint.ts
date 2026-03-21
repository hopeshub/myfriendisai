"use client";

import { useEffect, useState } from "react";

export type Breakpoint = "mobile" | "tablet" | "desktop";

/**
 * Returns the current breakpoint and whether the viewport is ≤768px (mobile strip).
 * Both values start as null during SSR/hydration to avoid layout flash.
 */
export function useBreakpoint(): {
  bp: Breakpoint | null;
  isMobileStrip: boolean | null;
} {
  const [state, setState] = useState<{
    bp: Breakpoint | null;
    isMobileStrip: boolean | null;
  }>({ bp: null, isMobileStrip: null });

  useEffect(() => {
    function update() {
      const w = window.innerWidth;
      setState({
        bp: w < 640 ? "mobile" : w < 1024 ? "tablet" : "desktop",
        isMobileStrip: w <= 768,
      });
    }
    update();
    window.addEventListener("resize", update);
    return () => window.removeEventListener("resize", update);
  }, []);

  return state;
}
