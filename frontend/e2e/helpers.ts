import { Page } from "@playwright/test";

export const API_BASE = "http://localhost:8000";

export const MOCK_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInJvbGUiOiJzdXBlcl9hZG1pbiJ9.mock";

export const MOCK_USER = {
  id: 1,
  username: "admin",
  email: "admin@ukip.local",
  role: "super_admin",
  is_active: true,
};

/** Inject a valid auth token directly into localStorage so tests skip login. */
export async function injectAuth(page: Page) {
  await page.addInitScript((token) => {
    localStorage.setItem("ukip_token", token);
  }, MOCK_TOKEN);
}

/** Mock the /users/me endpoint (called on hydration and after login). */
export async function mockUserMe(page: Page) {
  await page.route(`${API_BASE}/users/me`, (route) =>
    route.fulfill({ json: MOCK_USER })
  );
}

/** Mock minimal home-page endpoints so the dashboard renders without a backend. */
export async function mockHomeDashboard(page: Page) {
  await page.route(`${API_BASE}/stats`, (route) =>
    route.fulfill({ json: { total_entities: 120, indexed: 95, enriched: 80 } })
  );
  await page.route(`${API_BASE}/enrich/stats`, (route) =>
    route.fulfill({ json: { total: 120, enriched: 80, pending: 40, failed: 0 } })
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
}
