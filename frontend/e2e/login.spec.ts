import { test, expect } from "@playwright/test";
import { API_BASE, MOCK_TOKEN, MOCK_USER } from "./helpers";

test.describe("Login flow", () => {
  const usernameInput = (page: import("@playwright/test").Page) => page.getByPlaceholder(/superadmin/i);
  // Actual placeholder is "Mín. 8 caracteres" — the accented í is a distinct
  // code point from i, so a plain /i (case-insensitive) flag never matched
  // it. This locator could never have resolved before.
  const passwordInput = (page: import("@playwright/test").Page) => page.getByPlaceholder(/m[ií]n\.?\s*8\s*caracteres/i);
  const submitButton = (page: import("@playwright/test").Page) => page.getByRole("button", { name: /entrar a ukip/i });

  test.beforeEach(async ({ page }) => {
    // Ensure no stored token so we land on the login page
    await page.addInitScript(() => localStorage.clear());
    // The login screen's stakeholder carousel animates continuously.
    // Playwright's actionability check waits for an element's bounding box
    // to stay stable across frames before interacting with it, which an
    // animating page can keep from ever settling under CPU contention.
    // prefers-reduced-motion disables CSS transitions/animations — the
    // standard Playwright mechanism for this, not an arbitrary wait.
    await page.emulateMedia({ reducedMotion: "reduce" });
  });

  test("login page renders username and password inputs", async ({ page }) => {
    // Mock /users/me to return 401 so AuthContext treats user as unauthenticated
    await page.route(`${API_BASE}/users/me`, (route) =>
      route.fulfill({ status: 401, json: { detail: "Not authenticated" } })
    );

    await page.goto("/login");

    await expect(usernameInput(page)).toBeVisible();
    await expect(passwordInput(page)).toBeVisible();
    await expect(submitButton(page)).toBeVisible();
  });

  test("successful login redirects to home and lands in the authenticated workspace @critical", async ({ page }) => {
    await page.route(`${API_BASE}/**`, (route) => route.fulfill({ json: [] }));
    await page.route(`${API_BASE}/auth/token`, (route) =>
      route.fulfill({
        json: { access_token: MOCK_TOKEN, token_type: "bearer" },
      })
    );
    await page.route(`${API_BASE}/users/me`, (route) =>
      route.fulfill({ json: MOCK_USER })
    );
    // Mock home page endpoints
    await page.route(`${API_BASE}/stats`, (route) =>
      route.fulfill({ json: { total_entities: 0, indexed: 0, enriched: 0 } })
    );
    await page.route(`${API_BASE}/enrich/stats`, (route) =>
      route.fulfill({ json: { total: 0, enriched: 0, pending: 0, failed: 0 } })
    );
    await page.route(`${API_BASE}/domains`, (route) =>
      route.fulfill({ json: [] })
    );
    await page.route(`${API_BASE}/demo/status`, (route) =>
      route.fulfill({ json: { demo_active: false, demo_entity_count: 0 } })
    );
    await page.route(`${API_BASE}/brands**`, (route) =>
      route.fulfill({ json: [] })
    );
    await page.route(`${API_BASE}/rag/stats`, (route) =>
      route.fulfill({ json: { total_indexed: 0 } })
    );

    await page.goto("/login");

    await usernameInput(page).fill("admin");
    await passwordInput(page).fill("password");
    await submitButton(page).click();

    await expect(page).toHaveURL("/");
    // Landing on "/" alone doesn't prove the workspace hydrated — assert the
    // authenticated dashboard chrome actually rendered, not a blank/error page.
    await expect(page.locator("h1")).toBeVisible({ timeout: 10_000 });
    await expect(page.getByText(/total de entidades/i)).toBeVisible();
  });

  test("invalid credentials show error message", async ({ page }) => {
    await page.route(`${API_BASE}/auth/token`, (route) =>
      route.fulfill({ status: 401, json: { detail: "Incorrect credentials" } })
    );
    await page.route(`${API_BASE}/users/me`, (route) =>
      route.fulfill({ status: 401, json: { detail: "Not authenticated" } })
    );

    await page.goto("/login");

    await usernameInput(page).fill("wrong");
    await passwordInput(page).fill("wrong");
    await submitButton(page).click();

    await expect(page.getByText(/usuario o contraseña incorrectos/i)).toBeVisible();
  });
});
