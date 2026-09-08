"use client";

import { useCallback, useSyncExternalStore } from "react";

// ── usePrefersReducedMotion ──────────────────────────────────────────────────
// Reports whether the OS "reduce motion" setting is on. Used to gate Recharts'
// JS-driven draw-on animation, which the global CSS prefers-reduced-motion
// block cannot reach.
//
// The server snapshot is `true` (motion-reduced) so an unresolved query never
// animates; every component that calls this is behind a `dynamic(…, { ssr:
// false })` wrapper, so that snapshot never has to match a hydrated tree. On
// the client the real query is read during the first render — earlier than the
// old post-paint effect, so a non-reduced-motion reader no longer sees a
// static frame before the draw-on animation.

const QUERY = "(prefers-reduced-motion: reduce)";

export function usePrefersReducedMotion(): boolean {
  const subscribe = useCallback((onChange: () => void) => {
    const mq = window.matchMedia(QUERY);
    mq.addEventListener("change", onChange);
    return () => mq.removeEventListener("change", onChange);
  }, []);

  return useSyncExternalStore(
    subscribe,
    () => window.matchMedia(QUERY).matches,
    () => true,
  );
}
