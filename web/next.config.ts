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
  // The public aggregate dataset (the durability bundle) is a folder of static
  // files under public/dataset/. Next serves public/ by exact path only and
  // does no directory-index resolution, so /dataset/v1 would 404 despite
  // index.html sitting right there. This rewrite makes the bundle URL — the
  // one printed in the dataset's own README and citation — actually open.
  async rewrites() {
    return [
      { source: "/dataset/:version", destination: "/dataset/:version/index.html" },
    ];
  },
};

export default nextConfig;
