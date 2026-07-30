/**
 * The paths the app shell renders without a session.
 *
 * Kept here rather than inline in LayoutContent so the allowlist is a named
 * thing with tests. It was two inline booleans, and `/embed/{token}` was missing
 * from it — the embed work made the route framable and never asked whether an
 * anonymous visitor could reach it. See design decision 6 in
 * openspec/changes/fix-embed-widget-distribution.
 *
 * Adding a route here makes it readable with no login. Do not add a path that
 * renders tenant data unless a token in the path is itself the credential, which
 * is the case for both entries below.
 */

/** Paths public in their entirety, matched exactly. */
const EXACT: readonly string[] = ["/login"];

/**
 * Parents whose *children* are public while the parent itself is not.
 *
 * `/catalogs` lists an operator's catalogs and `/embed` has no anonymous
 * listing; only `/catalogs/{slug}` and `/embed/{token}` are public, and in both
 * cases the trailing segment is the credential.
 */
const PUBLIC_CHILDREN: readonly string[] = ["/catalogs", "/embed"];

/**
 * Whether `pathname` may render for a visitor with no session.
 *
 * Matching is anchored on segment boundaries: a path that merely contains a
 * public segment (`/admin/embed/x`) or extends one (`/loginx`, `/embedded/x`) is
 * not public.
 */
export function isPublicRoute(pathname: string): boolean {
  if (EXACT.includes(pathname)) return true;
  return PUBLIC_CHILDREN.some((parent) => hasChild(pathname, parent));
}

/**
 * Whether `pathname` renders without the sidebar and header — **regardless of
 * session**.
 *
 * A separate question from `isPublicRoute`. An embed is a standalone document
 * that a third party frames at 480x320; rendering the app shell inside it would
 * be wrong for an anonymous visitor and equally wrong for the signed-in operator
 * previewing their own widget. A published catalog, by contrast, is a page of the
 * app that happens to be public, and keeps its chrome for a signed-in operator.
 */
export function isStandaloneRoute(pathname: string): boolean {
  return pathname === "/login" || hasChild(pathname, "/embed");
}

/** `pathname` is a non-empty child of `parent`, matched on a segment boundary. */
function hasChild(pathname: string, parent: string): boolean {
  return (
    pathname.startsWith(`${parent}/`) && pathname.length > parent.length + 1
  );
}
