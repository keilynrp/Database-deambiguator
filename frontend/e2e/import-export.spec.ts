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

    // The import tab should contain a file input or drop zone
    await expect(
      page.getByRole("tab", { name: /import/i }).or(
        page.getByText(/upload|drag.*drop|choose.*file/i).first()
      )
    ).toBeVisible({ timeout: 10_000 });
  });

  test("shows Export section", async ({ page }) => {
    await page.goto("/import-export");

    // Export button or section should be present
    await expect(
      page.getByRole("button", { name: /export/i }).or(
        page.getByText(/export entities/i).first()
      )
    ).toBeVisible({ timeout: 10_000 });
  });
});
