import { defineConfig, devices } from "@playwright/test";

// Server strategy: `next dev --webpack` compiles pages on demand. Locally
// that's the right trade-off (hot reload), but in CI it proved unreliable —
// during #290 it repeatedly failed to answer even the home route within
// Playwright's 120s webServer timeout on a resource-constrained runner-like
// sandbox. `npm run build` + `next start` serves prebuilt pages: measured
// ~10-22s one-time startup, then 70-90ms per route thereafter (see
// docs/operating/PLAYWRIGHT_GATE.md for the full comparison). CI uses that;
// local dev keeps `next dev` unchanged so this doesn't touch local DX.
const isCI = !!process.env.CI;

export default defineConfig({
  testDir: "./e2e",
  fullyParallel: false,
  forbidOnly: isCI,
  retries: isCI ? 2 : 0,
  workers: 1,
  reporter: "html",
  use: {
    baseURL: "http://localhost:3004",
    channel: "chrome",
    trace: "on-first-retry",
    screenshot: "only-on-failure",
    launchOptions: {
      args: [
        "--disable-gpu",
        "--disable-dev-shm-usage",
        "--no-first-run",
        "--no-default-browser-check",
      ],
    },
  },
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
  ],
  webServer: {
    command: isCI
      ? "npm run build && node node_modules/next/dist/bin/next start -p 3004"
      : "node node_modules/next/dist/bin/next dev -p 3004 --webpack",
    url: "http://localhost:3004",
    reuseExistingServer: !isCI,
    // The build step alone is ~70-90s; budget generously so a slow CI
    // runner doesn't flake the gate on startup rather than on a real
    // assertion.
    timeout: isCI ? 300_000 : 120_000,
  },
});
