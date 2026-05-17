"use client";

import { useEffect, useLayoutEffect, useRef, useState } from "react";

// ── Reveal ───────────────────────────────────────────────────────────────────
// Progressive-enhancement scroll reveal: a one-time fade + 12px rise the first
// time an element scrolls into view.
//
// Safety contract — content must NEVER be left stuck invisible:
//   • The wrapper is server-rendered with no animation class, so it is fully
//     visible if JS never runs.
//   • Only after the client mounts AND the element is still off-screen does it
//     get `.reveal-pending` (opacity:0). This is applied in useLayoutEffect,
//     before the browser paints, so there is no visible flash.
//   • If the element is already on-screen at mount (above the fold), it is
//     never hidden — it just stays visible, no animation.
//   • The IntersectionObserver fires once, swaps `.reveal-pending` for
//     `.reveal-in`, and unobserves. After the 450ms animation the element is
//     at its natural visible resting state.
//   • prefers-reduced-motion: the CSS block zeroes the animation duration, so
//     `.reveal-in` lands on the visible state instantly. We also skip hiding
//     entirely in that case for belt-and-suspenders safety.

export default function Reveal({
  children,
  className,
  delay = 0,
}: {
  children: React.ReactNode;
  className?: string;
  delay?: number;
}) {
  const ref = useRef<HTMLDivElement>(null);
  // `armed` becomes true only when we have decided to hide-then-reveal.
  const [armed, setArmed] = useState(false);

  // Decide synchronously, before paint, whether to hide the element.
  useLayoutEffect(() => {
    const el = ref.current;
    if (!el) return;

    const reduce =
      typeof window !== "undefined" &&
      window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reduce) return; // never hide under reduced motion

    // Only arm (hide) if the element is currently below the viewport. If it is
    // already visible we leave it alone — no flash, no animation.
    const rect = el.getBoundingClientRect();
    const belowFold = rect.top >= window.innerHeight;
    if (belowFold) {
      el.classList.add("reveal-pending");
      setArmed(true);
    }
  }, []);

  useEffect(() => {
    if (!armed) return;
    const el = ref.current;
    if (!el) return;

    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) {
            el.style.animationDelay = delay ? `${delay}ms` : "";
            el.classList.remove("reveal-pending");
            el.classList.add("reveal-in");
            observer.unobserve(el);
          }
        }
      },
      { threshold: 0.12 },
    );
    observer.observe(el);
    return () => observer.disconnect();
  }, [armed, delay]);

  return (
    <div ref={ref} className={className}>
      {children}
    </div>
  );
}
