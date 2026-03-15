import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "My Friend Is AI",
  description:
    "Tracking the growth and cultural dynamics of AI companionship communities on Reddit.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=5" />
      </head>
      <body className="antialiased">
        <header className="border-b border-border">
          <div className="max-w-6xl mx-auto px-4 sm:px-6 py-4 flex items-center justify-between">
            <Link
              href="/"
              className="text-base font-semibold tracking-tight text-foreground hover:text-primary transition-colors"
            >
              My Friend Is AI
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
          <div className="max-w-6xl mx-auto px-4 sm:px-6 py-6 text-xs text-muted flex flex-col sm:flex-row items-start sm:items-center justify-between gap-1 sm:gap-0">
            <span>Data from Reddit&apos;s public endpoints · ~1.8M posts · 2023–present</span>
            <a href="/about" className="hover:text-foreground transition-colors">Methodology ↗</a>
          </div>
        </footer>
      </body>
    </html>
  );
}
