import { test, expect } from "@playwright/test";
import { API_BASE, injectAuth, mockUserMe } from "./helpers";

/**
 * Critical path: entity search/detail read path (#291).
 *
 * The list and detail endpoints are mocked independently. Annotations and
 * authority records genuinely degrade gracefully on the page-wide `[]`
 * catch-all (the component maps over them as arrays). Quality and attention
 * do not: the detail page reads `attentionData.summary.active_sources` and
 * similar nested fields, so `[]` crashes the whole route via
 * entities/error.tsx ("Cannot read properties of undefined") — the same
 * class of bug the dashboard's EnrichmentSourceHealthCard hit (see
 * helpers.ts's mockExecutiveDashboard). Both get an explicit, correctly
 * shaped empty response instead.
 */
const ADA_LOVELACE = {
  id: 777,
  primary_label: "Ada Lovelace",
  secondary_label: "Countess of Lovelace",
  canonical_id: "Q7259",
  entity_type: "person",
  domain: "default",
  validation_status: "confirmed",
  enrichment_status: "completed",
  enrichment_citation_count: 12,
  source: "user",
  attributes_json: null,
  normalized_json: null,
  quality_score: 0.82,
};

// A second entity that does NOT match a "Lovelace" search. Its presence in
// the initial (unfiltered) list and absence from the filtered response is
// what proves the search request actually changed what's rendered, rather
// than the test re-asserting a result that was already on screen.
const DECOY_ENTITY = {
  id: 778,
  primary_label: "Bob Placeholder",
  secondary_label: null,
  canonical_id: "Q0",
  entity_type: "person",
  domain: "default",
  validation_status: "confirmed",
  enrichment_status: "none",
  enrichment_citation_count: null,
  source: "user",
  attributes_json: null,
  normalized_json: null,
  quality_score: 0.4,
};

const UNFILTERED_RESULT = [ADA_LOVELACE, DECOY_ENTITY];
const FILTERED_RESULT = [ADA_LOVELACE];

const ENTITY_DETAIL = {
  id: 777,
  import_batch_id: 1,
  primary_label: "Ada Lovelace",
  secondary_label: "Countess of Lovelace",
  canonical_id: "Q7259",
  entity_type: "person",
  domain: "default",
  validation_status: "confirmed",
  enrichment_status: "completed",
  enrichment_doi: null,
  enrichment_citation_count: 12,
  enrichment_concepts: null,
  enrichment_source: "wikidata",
  enrichment_work_type: null,
  quality_score: 0.82,
  source: "user",
  attributes_json: null,
  normalized_json: null,
  enrichment_issn_l: null,
};

test.describe("Entity search and detail read path (critical)", () => {
  test.beforeEach(async ({ page }) => {
    await injectAuth(page);
    // Every other endpoint the detail page calls (annotations, authority
    // records, quality, attention) degrades gracefully on an empty array —
    // only the two endpoints this journey actually reads are overridden.
    await page.route(`${API_BASE}/**`, (route) => route.fulfill({ json: [] }));
    await mockUserMe(page);
    // Initial, unfiltered load — includes a decoy entity so a later search
    // has something to actually prove it filtered out.
    await page.route(`${API_BASE}/entities?**`, (route) =>
      route.fulfill({ json: UNFILTERED_RESULT, headers: { "X-Total-Count": "2" } })
    );
    await page.route(`${API_BASE}/entities/777`, (route) =>
      route.fulfill({ json: ENTITY_DETAIL })
    );
    await page.route(`${API_BASE}/entities/777/quality`, (route) =>
      route.fulfill({ json: { score: 0.82, stored_score: 0.82, breakdown: {} } })
    );
    await page.route(`${API_BASE}/entities/777/attention`, (route) =>
      route.fulfill({
        json: {
          summary: {
            attention_score: 0,
            category: "none",
            total_mentions: 0,
            active_sources: 0,
            last_seen_at: null,
          },
          source_counts: {},
          source_breakdown: [],
          timeline: [],
          explanations: [],
          alerts: [],
        },
      })
    );
  });

  test("searching finds a result and opening it shows the entity detail @critical", async ({ page }) => {
    await page.goto("/entities");

    await expect(
      page.getByRole("heading", { name: "Knowledge Explorer", exact: true })
    ).toBeVisible({ timeout: 10_000 });

    const resultLink = page.getByRole("link", { name: "Ada Lovelace" });
    const decoyLink = page.getByRole("link", { name: "Bob Placeholder" });
    await expect(resultLink).toBeVisible({ timeout: 10_000 });
    // The decoy is part of the unfiltered response, so it must be visible
    // now — its later disappearance is what proves the search actually ran.
    await expect(decoyLink).toBeVisible({ timeout: 10_000 });

    // Search interaction: register a route for the exact filtered request
    // *before* triggering it (registered after the beforeEach catch-all, so
    // it takes precedence — same pattern as coauthorship.spec.ts), then wait
    // for that specific request/response rather than re-checking state that
    // was already on screen from the initial load.
    await page.route(`${API_BASE}/entities?**`, (route) => {
      const url = new URL(route.request().url());
      if (url.searchParams.get("search") === "Lovelace") {
        return route.fulfill({ json: FILTERED_RESULT, headers: { "X-Total-Count": "1" } });
      }
      return route.fulfill({ json: UNFILTERED_RESULT, headers: { "X-Total-Count": "2" } });
    });

    const searchBox = page.getByPlaceholder(/Buscar por título/i);
    const filteredResponsePromise = page.waitForResponse((response) => {
      const url = new URL(response.url());
      return url.pathname.endsWith("/entities") && url.searchParams.get("search") === "Lovelace";
    });
    await searchBox.fill("Lovelace");
    const filteredResponse = await filteredResponsePromise;
    expect(filteredResponse.ok()).toBe(true);

    // Only after that request/response completes: the decoy — present in
    // the unfiltered response, absent from the filtered one — is gone, and
    // the real match is still there.
    await expect(decoyLink).toHaveCount(0);
    await expect(resultLink).toBeVisible();

    await resultLink.click();
    await expect(page).toHaveURL(/\/entities\/777$/);
    // Note: deliberately not waitForLoadState("networkidle") here — the
    // detail page opens a WebSocket (presence) that reconnects on failure,
    // so the network never truly goes idle. Visibility-based waits below
    // are the correct synchronization for this page.

    // Detail read: core fields from the mocked detail response render.
    await expect(page.getByRole("heading", { name: "Ada Lovelace" }).first()).toBeVisible({
      timeout: 15_000,
    });
    await expect(page.getByText("Q7259")).toBeVisible({ timeout: 10_000 });
  });
});
