import { test, expect } from "@playwright/test";
import { injectAuth, mockUserMe, API_BASE } from "./helpers";

test.describe("Import / Export page", () => {
  test.beforeEach(async ({ page }) => {
    await injectAuth(page);
    await mockUserMe(page);
    await page.route(`${API_BASE}/**`, (route) => route.fulfill({ json: [] }));
  });

  test("renders the page heading", async ({ page }) => {
    await page.goto("/import-export");

    await expect(page.getByRole("heading", { level: 1 })).toBeVisible({
      timeout: 10_000,
    });
  });

  test("shows Import tab content", async ({ page }) => {
    await page.goto("/import-export");

    await expect(
      page.getByRole("heading", { name: "Importar Datos", exact: true })
    ).toBeVisible({ timeout: 10_000 });
  });

  test("shows Export section", async ({ page }) => {
    await page.goto("/import-export");

    await expect(
      page.getByRole("heading", { name: "Exportar Datos", exact: true })
    ).toBeVisible({ timeout: 10_000 });
  });

  test("uploading a file completes ingest and the imported record is visible in the Entity Explorer @critical", async ({ page }) => {
    await page.route(`${API_BASE}/upload`, (route) =>
      route.fulfill({
        json: {
          message: "Import complete",
          total_rows: 1,
          matched_columns: ["title", "canonical_id"],
          unmatched_columns: [],
          format: "csv",
          domain: "default",
          import_batch_id: 9001,
          source_label: "e2e-fixture.csv",
        },
      })
    );

    await page.goto("/import-export");

    // Two file inputs exist on this page (this drop zone, and
    // DataSourceSchemaAnalyzer's); the Import section renders first in
    // source order, so .first() reliably targets this one.
    const fileInput = page.locator('input[type="file"]').first();
    await fileInput.setInputFiles({
      name: "e2e-fixture.csv",
      mimeType: "text/csv",
      buffer: Buffer.from("title,canonical_id\nNewly Ingested Entity,Q999999\n"),
    });

    await expect(
      page.getByText("Importación Exitosa", { exact: true })
    ).toBeVisible({ timeout: 10_000 });

    // Ingest → Entity Explorer: the imported record must actually surface in
    // the searchable entity list, not just in the upload confirmation panel.
    await page.route(`${API_BASE}/entities?**`, (route) =>
      route.fulfill({
        json: [
          {
            id: 4242,
            primary_label: "Newly Ingested Entity",
            secondary_label: null,
            canonical_id: "Q999999",
            entity_type: "publication",
            domain: "default",
            validation_status: "pending",
            enrichment_status: "none",
            enrichment_citation_count: null,
            source: "user",
            attributes_json: null,
            normalized_json: null,
            quality_score: null,
          },
        ],
        headers: { "X-Total-Count": "1" },
      })
    );

    await page.goto("/entities");
    await expect(
      page.getByRole("heading", { name: "Knowledge Explorer", exact: true })
    ).toBeVisible({ timeout: 10_000 });
    await expect(page.getByText("Newly Ingested Entity")).toBeVisible({
      timeout: 10_000,
    });
  });
});
