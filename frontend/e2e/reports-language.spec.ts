import { test, expect } from "@playwright/test";
import { API_BASE, injectAuth, mockUserMe } from "./helpers";

/**
 * Critical path: reporting/language path, EN and ES (#291).
 *
 * Scope note: this covers what the frontend actually controls today — the
 * Reports page's own chrome (heading, generate button, completion toast)
 * must render in the app's active language, not fall back to English or an
 * unresolved catalog key. It intentionally does NOT assert on the language
 * of the generated artifact's *content*: the frontend does not currently
 * forward the UI language as the `language` query param that
 * `/reports/generate` and `/exports/*` accept (`backend/i18n/locale.py`'s
 * `resolve_report_language`), so every report is generated in the backend's
 * default language regardless of the UI's language setting. That gap predates
 * #291, is a frontend/backend wiring question rather than an E2E-gate
 * question, and is out of scope here — fixing it would be a product-behavior
 * change, which #291 is explicitly not authorized to make. The artifact's
 * own catalog-language correctness is covered separately by the backend
 * report-rendering tests (`backend/tests/test_report_pptx_presentation.py`
 * and the "no rendered format may show an unresolved catalog key" suite).
 */
const SECTIONS = [
  {
    id: "entity_stats",
    label: "Entity Statistics",
    formats: { html: true, pdf: true, excel: true, pptx: true },
  },
];

const BENCHMARK_PROFILES = [
  {
    id: "default",
    name: "Default",
    description: "E2E benchmark",
    region: "global",
    rules_count: 4,
    is_default: true,
  },
];

async function mockReportsPage(page: import("@playwright/test").Page) {
  await injectAuth(page);
  await page.route(`${API_BASE}/**`, (route) => route.fulfill({ json: [] }));
  await mockUserMe(page);
  await page.route(`${API_BASE}/reports/sections`, (route) =>
    route.fulfill({ json: SECTIONS })
  );
  await page.route(`${API_BASE}/analytics/benchmarks/profiles`, (route) =>
    route.fulfill({ json: BENCHMARK_PROFILES })
  );
  await page.route(`${API_BASE}/reports/generate`, (route) =>
    route.fulfill({
      status: 200,
      contentType: "text/html",
      headers: { "Content-Disposition": 'attachment; filename="ukip_report.html"' },
      body: "<html><body>UKIP report</body></html>",
    })
  );
}

test.describe("Reporting language path (critical)", () => {
  test("Spanish UI: report builder chrome and completion feedback do not fall back to English @critical", async ({ page }) => {
    await page.addInitScript(() => {
      localStorage.setItem("app_lang", "es");
    });
    await mockReportsPage(page);

    await page.goto("/reports");

    await expect(
      page.getByRole("heading", { name: "Generador de Reportes", exact: true })
    ).toBeVisible({ timeout: 10_000 });

    const generateButton = page.getByRole("button", { name: "Generar y Descargar" });
    await expect(generateButton).toBeVisible({ timeout: 10_000 });
    await generateButton.click();

    await expect(page.getByText("Reporte descargado", { exact: true })).toBeVisible({
      timeout: 10_000,
    });
    // Guard: neither the English string nor a raw unresolved catalog key
    // ("page.reports.title" etc.) may be visible while the UI is in Spanish.
    await expect(page.getByText("Report Builder", { exact: true })).toHaveCount(0);
    await expect(page.getByText("page.reports.title", { exact: true })).toHaveCount(0);
  });

  test("English UI: report builder chrome renders in English @critical", async ({ page }) => {
    await page.addInitScript(() => {
      localStorage.setItem("app_lang", "en");
    });
    await mockReportsPage(page);

    await page.goto("/reports");

    await expect(
      page.getByRole("heading", { name: "Report Builder", exact: true })
    ).toBeVisible({ timeout: 10_000 });

    const generateButton = page.getByRole("button", { name: "Generate & Download" });
    await expect(generateButton).toBeVisible({ timeout: 10_000 });
    await generateButton.click();

    await expect(page.getByText("Report downloaded", { exact: true })).toBeVisible({
      timeout: 10_000,
    });
  });
});
