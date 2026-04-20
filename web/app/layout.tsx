import type { Metadata } from "next";
import Link from "next/link";
import { readFileSync } from "fs";
import { join } from "path";
import { Inter } from "next/font/google";
import { GeistSans } from "geist/font/sans";
import { Analytics } from "@vercel/analytics/next";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "My Friend Is AI",
  description:
    "Tracking the growth and cultural dynamics of AI companionship communities on Reddit.",
  metadataBase: new URL("https://myfriendisai.com"),
  openGraph: {
    title: "My Friend Is AI",
    description:
      "Tracking AI companion discourse on Reddit across six themes — romance, addiction, consciousness, therapy, rupture, and sexual roleplay.",
    url: "https://myfriendisai.com",
    siteName: "My Friend Is AI",
    type: "website",
    locale: "en_US",
  },
  twitter: {
    card: "summary_large_image",
    title: "My Friend Is AI",
    description:
      "Tracking AI companion discourse on Reddit across six themes.",
  },
  robots: {
    index: true,
    follow: true,
  },
};

function getSiteMeta() {
  try {
    const raw = readFileSync(join(process.cwd(), "data", "site_meta.json"), "utf-8");
    return JSON.parse(raw) as { total_posts: number; date_start: string; date_end: string };
  } catch (e) {
    // Fallback is deliberately conservative — if you see this in prod, site_meta.json
    // is missing or malformed and the daily export pipeline needs investigation.
    console.error("Failed to load site_meta.json, using fallback:", e);
    return { total_posts: 0, date_start: "2023-01-01", date_end: "" };
  }
}

function formatPostCount(n: number): string {
  return `~${(n / 1_000_000).toFixed(1)}M`;
}

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  const meta = getSiteMeta();
  const startYear = meta.date_start.slice(0, 4);

  return (
    <html lang="en">
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=5" />
      </head>
      <body className={`antialiased ${inter.className}`}>
        <header className="border-b border-border">
          <div className="max-w-6xl mx-auto px-4 sm:px-6 py-4 flex items-center justify-between">
            <Link
              href="/"
              className={`text-lg tracking-tight hover:text-primary transition-colors ${GeistSans.className}`}
            >
              <span style={{ fontWeight: 300, color: "rgba(255,255,255,0.6)" }}>My Friend Is</span>
              {" "}
              <span style={{ fontWeight: 700, color: "#F8FAFC" }}>AI</span>
            </Link>
            <nav className="flex gap-6 text-sm text-muted">
              <Link
                href="/about"
                className="hover:text-foreground transition-colors"
              >
                About
              </Link>
              <a
                href="https://github.com/hopeshub/myfriendisai"
                target="_blank"
                rel="noopener noreferrer"
                className="hover:text-foreground transition-colors"
              >
                GitHub ↗
              </a>
            </nav>
          </div>
        </header>

        <main>{children}</main>

        <footer className="border-t border-border mt-20">
          <div className="max-w-6xl mx-auto px-4 sm:px-6 py-6 text-sm text-muted">
            <span>Data from Reddit&apos;s public endpoints · {formatPostCount(meta.total_posts)} posts · {startYear}–present</span>
          </div>
        </footer>
        <Analytics />
      </body>
    </html>
  );
}
