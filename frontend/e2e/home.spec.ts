import { test, expect } from "@playwright/test";
import { injectAuth, mockUserMe, mockHomeDashboard } from "./helpers";

test.describe("Home dashboard", () => {
  test.beforeEach(async ({ page }) => {
    await injectAuth(page);
    await mockUserMe(page);
    await mockHomeDashboard(page);
  });

  test("home page renders stat cards", async ({ page }) => {
    await page.goto("/");

    // Wait for the page to hydrate
    await expect(page.locator("h1")).toBeVisible({ timeout: 10_000 });

    // StatCards should appear (4 cards: Entities, Enriched, Domains, Indexed)
    const cards = page.locator("[data-testid='stat-card'], .bg-white.rounded-xl");
    // At minimum the heading and some numeric values render
    await expect(page.getByText("120")).toBeVisible();
  });

  test("home page shows Knowledge Dashboard heading", async ({ page }) => {
    await page.goto("/");

    await expect(
      page.getByRole("heading", { name: /knowledge dashboard/i })
    ).toBeVisible({ timeout: 10_000 });
  });

  test("sidebar navigation links are visible", async ({ page }) => {
    await page.goto("/");

    // Sidebar should contain key navigation items
    await expect(page.getByRole("link", { name: /entities/i }).first()).toBeVisible({
      timeout: 10_000,
    });
    await expect(page.getByRole("link", { name: /import/i }).first()).toBeVisible();
  });
});
