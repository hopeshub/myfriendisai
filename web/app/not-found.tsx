import Link from "next/link";

export default function NotFound() {
  return (
    <div className="max-w-xl mx-auto px-4 py-24 text-center">
      <h1 className="text-4xl font-bold mb-4">404</h1>
      <p className="text-muted mb-8">
        There&apos;s no page at this address. The home page has the tracker;
        the about page explains how it all works.
      </p>
      <Link
        href="/"
        className="inline-block px-5 py-2.5 text-sm font-medium rounded-lg bg-card border border-border hover:bg-[#1F2233] transition-colors"
      >
        Back to home
      </Link>
    </div>
  );
}
