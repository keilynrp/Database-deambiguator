import { test, expect } from "@playwright/test";
import { injectAuth, mockUserMe, mockHomeDashboard, API_BASE } from "./helpers";

test.describe("Language switching", () => {
  test.beforeEach(async ({ page }) => {
    await injectAuth(page);
    await mockUserMe(page);
    await mockHomeDashboard(page);
    await page.route(`${API_BASE}/**`, (route) => route.fulfill({ json: [] }));
  });

  test("app defaults to Spanish (es) — sidebar shows Spanish labels", async ({
    page,
  }) => {
    // Ensure no language override in localStorage (default = es)
    await page.addInitScript(() => {
      localStorage.removeItem("app_lang");
    });

    await page.goto("/");
    await page.waitForLoadState("networkidle");

    // Spanish sidebar labels
    const sidebar = page.locator("nav, aside").first();
    await expect(sidebar.getByText(/entidades|importar|analítica/i).first()).toBeVisible({
      timeout: 10_000,
    });
  });

  test("switching to English shows English labels", async ({ page }) => {
    await page.addInitScript(() => {
      localStorage.setItem("app_lang", "en");
    });

    await page.goto("/");
    await page.waitForLoadState("networkidle");

    // English sidebar labels
    const sidebar = page.locator("nav, aside").first();
    await expect(sidebar.getByText(/entities|import|analytics/i).first()).toBeVisible({
      timeout: 10_000,
    });
  });

  test("language persists after page reload", async ({ page }) => {
    await page.addInitScript(() => {
      localStorage.setItem("app_lang", "en");
    });

    await page.goto("/");
    await page.waitForLoadState("networkidle");
    await page.reload();
    await page.waitForLoadState("networkidle");

    const sidebar = page.locator("nav, aside").first();
    await expect(sidebar.getByText(/entities|import|analytics/i).first()).toBeVisible({
      timeout: 10_000,
    });
  });
});
