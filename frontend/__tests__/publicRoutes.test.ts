/**
 * Which paths the app shell may render without a session.
 *
 * Spec: openspec/changes/fix-embed-widget-distribution — design decision 6.
 *
 * This list existed as two inline booleans inside LayoutContent, and that is how
 * `/embed/{token}` came to be missing from it: the embed work exempted the route
 * from X-Frame-Options and emitted a per-widget frame-ancestors, and nothing
 * asked whether an anonymous visitor could reach the page at all. It could not —
 * the guard redirected to /login, which denies framing, so a customer's iframe
 * showed a broken document. The redirect is client-side, so the server answered
 * 200 with the full embed document and every response-level check passed.
 *
 * Naming the allowlist is the point. A predicate with tests is a place where
 * "is this public?" gets answered on purpose.
 */
import { describe, expect, it } from "vitest";
import { isPublicRoute, isStandaloneRoute } from "../lib/publicRoutes";

describe("isPublicRoute", () => {
  it("treats the login page as public", () => {
    expect(isPublicRoute("/login")).toBe(true);
  });

  it("treats a published catalog as public", () => {
    expect(isPublicRoute("/catalogs/acme-2026")).toBe(true);
  });

  it("does NOT treat the catalog index as public", () => {
    // /catalogs lists an operator's catalogs; only a specific published one is
    // public. This distinction predates the embed work and must survive it.
    expect(isPublicRoute("/catalogs")).toBe(false);
  });

  it("treats an embed page as public — it is the whole point of an embed", () => {
    expect(
      isPublicRoute("/embed/00000000-0000-4000-8000-000000000000")
    ).toBe(true);
  });

  it("does NOT treat the embed index as public", () => {
    // Same shape as /catalogs: there is no anonymous listing of embeds.
    expect(isPublicRoute("/embed")).toBe(false);
  });

  it("keeps the rest of the app behind the session", () => {
    for (const path of [
      "/",
      "/entities",
      "/dashboards/lake-explorer",
      "/settings/auth",
      "/admin",
      "/reports",
    ]) {
      expect(isPublicRoute(path)).toBe(false);
    }
  });

  it("does not let a public prefix smuggle in a private path", () => {
    // A path that merely *contains* a public segment is not public. Without
    // anchoring, "/admin/embed/x" or "/x?next=/embed/y" would slip through.
    expect(isPublicRoute("/admin/embed/00000000-0000-4000-8000-000000000000")).toBe(
      false
    );
    expect(isPublicRoute("/dashboard/catalogs/x")).toBe(false);
    expect(isPublicRoute("/loginx")).toBe(false);
    expect(isPublicRoute("/embedded/x")).toBe(false);
  });
});

describe("isStandaloneRoute", () => {
  // Separate from isPublicRoute because the two questions differ: "may an
  // anonymous visitor see this?" and "does this render without the sidebar and
  // header?". An embed answers yes to both, and it must answer yes to the second
  // *regardless of session* — otherwise an operator who is logged in sees the
  // whole app shell inside a 480x320 iframe, which is exactly the person most
  // likely to check their own widget.
  it("renders an embed page bare, session or not", () => {
    expect(
      isStandaloneRoute("/embed/00000000-0000-4000-8000-000000000000")
    ).toBe(true);
  });

  it("renders the login page bare", () => {
    expect(isStandaloneRoute("/login")).toBe(true);
  });

  it("keeps the shell on a published catalog", () => {
    // A catalog is a page of the app that happens to be public; it keeps the
    // chrome when an operator is signed in. Only embeds are chrome-free.
    expect(isStandaloneRoute("/catalogs/acme-2026")).toBe(false);
  });

  it("keeps the shell everywhere else", () => {
    expect(isStandaloneRoute("/entities")).toBe(false);
    expect(isStandaloneRoute("/")).toBe(false);
    expect(isStandaloneRoute("/embedded/x")).toBe(false);
  });
});
