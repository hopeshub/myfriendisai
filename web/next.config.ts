import type { NextConfig } from "next";

// Defensive headers applied to every route. HSTS is already set via Vercel's
// domain config, so we don't duplicate it here. CSP is intentionally omitted
// for now — it needs dedicated testing against Next.js hydration, Vercel
// Analytics, and Recharts inline styles before it can be enforced.
const securityHeaders = [
  { key: "X-Frame-Options", value: "DENY" },
  { key: "X-Content-Type-Options", value: "nosniff" },
  { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
  {
    key: "Permissions-Policy",
    value: "camera=(), microphone=(), geolocation=(), interest-cohort=()",
  },
  { key: "X-DNS-Prefetch-Control", value: "on" },
];

const nextConfig: NextConfig = {
  experimental: {
    optimizePackageImports: ["recharts"],
  },
  async headers() {
    return [
      {
        source: "/:path*",
        headers: securityHeaders,
      },
    ];
  },
};

export default nextConfig;
