import { test, expect } from "@playwright/test";
import { API_BASE, injectAuth, mockUserMe } from "./helpers";

/**
 * Critical path: reporting/language path, EN and ES (#291).
 *
 * The frontend forwards the UI's active language to the backend's existing
 * `language` query parameter on `/reports/generate` /`/exports/*`
 * (`backend/i18n/locale.py`'s `resolve_report_language`) — see
 * `frontend/app/reports/page.tsx`'s `handleGenerate`. This test proves both
 * ends of that wiring from the browser, without a live backend:
 *
 *   1. the outgoing request actually carries `language=es` / `language=en`
 *      matching the active UI language (asserted via the mock route's own
 *      request inspection — the same pattern `geographic.spec.ts` uses);
 *   2. the resulting downloaded artifact is the language-specific content
 *      the (mocked) backend served for that request, not a same-for-every-
 *      request placeholder — i.e. changing the UI language actually changes
 *      what comes back, which is what "does not fall back to English" means
 *      end-to-end from the frontend's side.
 *
 * The mock's fallback branch (front-end language param missing/incorrect)
 * deliberately returns a third, distinct "unexpected" body so a regression
 * in the request-construction fails loud rather than silently matching the
 * wrong assertion.
 *
 * What this does not cover: the *rendering correctness* of catalog-sourced
 * text inside a real artifact for a given language — that's a backend
 * concern, already covered by `backend/tests/test_report_render_boundary.py
 * ::test_no_format_shows_an_unresolved_catalog_key` (parametrized en/es
 * across every export format) and `test_report_pptx_presentation.py`. This
 * test's job is the frontend↔backend wiring, not re-deriving that coverage.
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

const ARTIFACT_BODY: Record<"en" | "es" | "unexpected", string> = {
  en: "<html><body>UKIP Report — EN</body></html>",
  es: "<html><body>Informe UKIP — ES</body></html>",
  unexpected:
    "<html><body>UNEXPECTED: request did not carry a recognized language param</body></html>",
};

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
  await page.route(`${API_BASE}/reports/generate**`, (route) => {
    const url = new URL(route.request().url());
    const requestedLanguage = url.searchParams.get("language");
    const body =
      requestedLanguage === "es" ? ARTIFACT_BODY.es :
      requestedLanguage === "en" ? ARTIFACT_BODY.en :
      ARTIFACT_BODY.unexpected;
    return route.fulfill({
      status: 200,
      contentType: "text/html",
      headers: { "Content-Disposition": 'attachment; filename="ukip_report.html"' },
      body,
    });
  });
}

test.describe("Reporting language path (critical)", () => {
  test("Spanish UI: report request carries language=es and the downloaded artifact is the Spanish body, not the English fallback @critical", async ({ page }) => {
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

    const [download] = await Promise.all([
      page.waitForEvent("download"),
      generateButton.click(),
    ]);
    const stream = await download.createReadStream();
    const chunks: Buffer[] = [];
    for await (const chunk of stream) chunks.push(chunk as Buffer);
    const downloaded = Buffer.concat(chunks).toString("utf8");

    expect(downloaded).toBe(ARTIFACT_BODY.es);
    expect(downloaded).not.toBe(ARTIFACT_BODY.en);
    expect(downloaded).not.toBe(ARTIFACT_BODY.unexpected);

    await expect(page.getByText("Reporte descargado", { exact: true })).toBeVisible({
      timeout: 10_000,
    });
    // Guard: neither the English string nor a raw unresolved catalog key
    // ("page.reports.title" etc.) may be visible while the UI is in Spanish.
    await expect(page.getByText("Report Builder", { exact: true })).toHaveCount(0);
    await expect(page.getByText("page.reports.title", { exact: true })).toHaveCount(0);
  });

  test("English UI: report request carries language=en and the downloaded artifact is the English body @critical", async ({ page }) => {
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

    const [download] = await Promise.all([
      page.waitForEvent("download"),
      generateButton.click(),
    ]);
    const stream = await download.createReadStream();
    const chunks: Buffer[] = [];
    for await (const chunk of stream) chunks.push(chunk as Buffer);
    const downloaded = Buffer.concat(chunks).toString("utf8");

    expect(downloaded).toBe(ARTIFACT_BODY.en);
    expect(downloaded).not.toBe(ARTIFACT_BODY.es);
    expect(downloaded).not.toBe(ARTIFACT_BODY.unexpected);

    await expect(page.getByText("Report downloaded", { exact: true })).toBeVisible({
      timeout: 10_000,
    });
  });
});
