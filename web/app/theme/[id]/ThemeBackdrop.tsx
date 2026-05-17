/**
 * Theme-page shell — a centered content column.
 *
 * This was previously a lightbox-style backdrop: clicking the side margins or
 * pressing Escape navigated back to the homepage. That was removed — a theme
 * page is a full route with its own URL, scroll, and navigation, and a
 * full-page route should not behave like a modal. The "← All themes" link and
 * the bottom theme nav are the explicit, discoverable ways back.
 */
export default function ThemeBackdrop({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="max-w-[720px] mx-auto px-4 sm:px-8 py-8">{children}</div>
  );
}
