/**
 * What apiFetch does with a 401, and where it must not do it.
 *
 * Spec: openspec/changes/fix-embed-widget-distribution — design decision 6.
 *
 * A public page still renders inside the app's provider tree, and those
 * providers call apiFetch on mount (branding settings, enrichment stats). With
 * no session those calls answer 401, and apiFetch responded by assigning
 * window.location.href = "/login" — a hard navigation that no route guard can
 * veto. That is the second reason a customer's iframe showed a broken document,
 * and it survived fixing the first one: /embed was allowlisted in the shell and
 * the page still bounced, because the bounce came from the fetch layer.
 *
 * It affects /catalogs/{slug} identically — the public catalog route predates the
 * embed work and has the same hole.
 */
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { apiFetch } from "../lib/api";

/** Replaces window.location with a recorder; jsdom cannot really navigate. */
function stubLocation(pathname: string) {
  const recorder = { pathname, href: `http://localhost:3004${pathname}` };
  Object.defineProperty(window, "location", {
    value: recorder,
    writable: true,
    configurable: true,
  });
  return recorder;
}

const realLocation = window.location;

beforeEach(() => {
  localStorage.setItem("ukip_token", "a-token-that-the-server-rejects");
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue(
      new Response(JSON.stringify({ detail: "Not authenticated" }), {
        status: 401,
        headers: { "Content-Type": "application/json" },
      })
    )
  );
});

afterEach(() => {
  vi.unstubAllGlobals();
  localStorage.clear();
  Object.defineProperty(window, "location", {
    value: realLocation,
    writable: true,
    configurable: true,
  });
});

describe("apiFetch on 401", () => {
  it("bounces a private page to the login screen", () => {
    const location = stubLocation("/entities");
    return apiFetch("/entities").then(() => {
      expect(location.href).toBe("/login");
    });
  });

  it("does NOT bounce an embed page — nobody is expected to be signed in", async () => {
    const location = stubLocation("/embed/00000000-0000-4000-8000-000000000000");
    const before = location.href;
    await apiFetch("/branding/settings");
    expect(location.href).toBe(before);
  });

  it("does NOT bounce a published catalog", async () => {
    const location = stubLocation("/catalogs/acme-2026");
    const before = location.href;
    await apiFetch("/branding/settings");
    expect(location.href).toBe(before);
  });

  it("still returns the 401 to the caller on a public page", async () => {
    // Not swallowing it matters: the component decides what to show. Suppressing
    // the redirect must not also suppress the error.
    stubLocation("/embed/00000000-0000-4000-8000-000000000000");
    const response = await apiFetch("/branding/settings");
    expect(response.status).toBe(401);
  });

  it("clears the stored token on a private page", async () => {
    stubLocation("/entities");
    await apiFetch("/entities");
    expect(localStorage.getItem("ukip_token")).toBeNull();
  });

  it("does not clear a stored token on a public page", async () => {
    // An operator browsing their own embed preview keeps their session: the 401
    // came from a background provider call, not from their credentials failing.
    stubLocation("/embed/00000000-0000-4000-8000-000000000000");
    await apiFetch("/branding/settings");
    expect(localStorage.getItem("ukip_token")).toBe(
      "a-token-that-the-server-rejects"
    );
  });

  it("never bounces when already on the login screen", async () => {
    const location = stubLocation("/login");
    const before = location.href;
    await apiFetch("/entities");
    expect(location.href).toBe(before);
  });
});
