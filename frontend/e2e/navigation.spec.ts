import { test, expect } from "@playwright/test";
import { injectAuth, mockUserMe, mockHomeDashboard, API_BASE } from "./helpers";

test.describe("Sidebar navigation", () => {
  test.beforeEach(async ({ page }) => {
    await injectAuth(page);
    await mockUserMe(page);
    await mockHomeDashboard(page);
    // Generic fallback for all API calls on sub-pages
    await page.route(`${API_BASE}/**`, (route) => {
      // Only fulfil routes not already handled
      route.fulfill({ json: [] });
    });
  });

  test("navigates to Import/Export page", async ({ page }) => {
    await page.goto("/");
    await page.waitForLoadState("networkidle");

    await page.getByRole("link", { name: /import/i }).first().click();
    await expect(page).toHaveURL(/import-export/);
    await expect(page.getByRole("heading", { level: 1 })).toBeVisible({
      timeout: 10_000,
    });
  });

  test("navigates to Analytics page", async ({ page }) => {
    await page.goto("/");
    await page.waitForLoadState("networkidle");

    await page.getByRole("link", { name: /analytics/i }).first().click();
    await expect(page).toHaveURL(/analytics/);
    await expect(page.getByRole("heading", { level: 1 })).toBeVisible({
      timeout: 10_000,
    });
  });

  test("navigates to RAG Chat page", async ({ page }) => {
    await page.goto("/");
    await page.waitForLoadState("networkidle");

    await page.getByRole("link", { name: /rag|knowledge base|semantic/i }).first().click();
    await expect(page).toHaveURL(/rag/);
    await expect(page.getByRole("heading", { level: 1 })).toBeVisible({
      timeout: 10_000,
    });
  });
});
