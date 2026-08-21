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
const SEARCH_RESULT = [
  {
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
  },
];

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
    await page.route(`${API_BASE}/entities?**`, (route) =>
      route.fulfill({ json: SEARCH_RESULT, headers: { "X-Total-Count": "1" } })
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
    await expect(resultLink).toBeVisible({ timeout: 10_000 });

    // Search interaction: typing must not break the already-rendered result
    // (the mock is search-agnostic, so this exercises the debounced fetch
    // path without coupling the assertion to query-string echoing).
    const searchBox = page.getByPlaceholder(/Buscar por título/i);
    await searchBox.fill("Lovelace");
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
