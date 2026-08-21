# Playwright Critical-Path Gate

Introduced: 2026-08-21 (#291). Owner: frontend/platform test owner.

This document is the authoritative reference for UKIP's blocking browser-level
release gate: what it covers, why it's built the way it is, and the
ownership/flakiness policy that keeps it small and trustworthy.

---

## 1. What this gate is (and isn't)

`frontend/e2e/` contains UKIP's full Playwright suite — critical-path smoke
tests, deep single-feature coverage (e.g. the Geographic Intelligence panel),
and visual regression baselines. Only a **tagged subset** is the blocking CI
gate. The rest is available for local/manual use but does not block PRs.

Selection is by test title tag (`@critical`), filtered in CI with
`npx playwright test --grep @critical`. A test earns the tag by covering one
of the five business-critical journeys below and being deterministic
end-to-end. Nothing else gets the tag — see §7 for why.

---

## 2. Critical-path matrix

| Journey | Spec / test | Fixture strategy | External dependencies | Result |
| --- | --- | --- | --- | --- |
| 1. Login + authenticated workspace entry | `login.spec.ts` → "successful login redirects to home and lands in the authenticated workspace" | Mocked `/auth/token`, `/users/me`, home dashboard endpoints | None | Pass |
| 2. Ingest/import → Entity Explorer | `import-export.spec.ts` → "uploading a file completes ingest and the imported record is visible in the Entity Explorer" | Mocked `/upload`, then mocked `/entities` reflecting the uploaded record | None | Pass |
| 3. Entity search/detail read path | `entities.spec.ts` → "searching finds a result and opening it shows the entity detail" (new file — no prior spec covered this journey) | Mocked `/entities` (search) and `/entities/777` (detail); every other detail-page endpoint degrades on the existing catch-all | None | Pass |
| 4. Analytics/dashboard load with representative data | `navigation.spec.ts` → "navigates to Analytics page and loads representative dashboard data" | Existing `mockExecutiveDashboard` helper fixture (120 entities, 66.7% enrichment) | None | Pass |
| 5. Reporting language path, EN + ES | `reports-language.spec.ts` (new file) → one test per language | Mocked `/reports/sections`, `/analytics/benchmarks/profiles`, `/reports/generate` | None | Pass |

All five reuse the existing `frontend/e2e/helpers.ts` (`injectAuth`,
`mockUserMe`, `mockHomeDashboard`, `mockExecutiveDashboard`) and the
`API_BASE` route-glob convention already established by the pre-#291 suite.
Three of the five **tighten an existing spec in place** rather than adding a
new file (journeys 1, 2, 4); journeys 3 and 5 had no prior coverage at all,
so a new file was the only option, not a duplicate.

### Journey 5 scope note

`reports-language.spec.ts` asserts that the Reports page's own chrome
(heading, generate button, completion toast) renders in the active UI
language and never falls back to English or an unresolved catalog key. It
does **not** assert on the generated artifact's content language, because the
frontend does not currently forward the UI's language as the `language`
query parameter `/reports/generate` and `/exports/*` accept
(`backend/i18n/locale.py`'s `resolve_report_language`) — every report is
generated in the backend's default language today regardless of the UI
language setting. That gap predates #291 and is a frontend/backend wiring
question, not something a CI test-infrastructure change is authorized to fix
(see #291's contract: no product-behavior changes). The artifact's own
catalog-language correctness is covered separately by
`backend/tests/test_report_pptx_presentation.py` and the "no rendered format
may show an unresolved catalog key" backend suite. Tracked as a remaining
risk in the #291 PR, not silently worked around.

---

## 3. Baseline audit (pre-#291)

| Spec | Current purpose | Deterministic? | Selected for gate? | Action |
| --- | --- | --- | --- | --- |
| `login.spec.ts` | Login form + auth flow | Yes | Yes (journey 1) | Tightened: added workspace-content assertion, tagged `@critical` |
| `home.spec.ts` | Home dashboard rendering | Yes | No | Left as-is; overlaps with the tightened login test's workspace-entry assertion |
| `navigation.spec.ts` | Sidebar → page navigation | Yes | Yes (journey 4, Analytics only) | Tightened the Analytics test with KPI assertions, tagged `@critical`; Import/Export and RAG Chat navigation tests left untagged |
| `import-export.spec.ts` | Import/export page headings | Yes | Yes (journey 2) | Added a new upload → Entity Explorer test, tagged `@critical`; existing heading tests left untagged |
| `entities.spec.ts` | — (did not exist) | — | Yes (journey 3) | New file |
| `reports-language.spec.ts` | — (did not exist) | — | Yes (journey 5) | New file |
| `language.spec.ts` | Sidebar EN/ES label switching | Yes | No | General i18n coverage, not one of the five journeys; left untagged |
| `coauthorship.spec.ts` | Coauthorship graph analytics | Yes (fully mocked) | No | Deep single-feature coverage beyond a dashboard-load smoke check; left untagged |
| `geographic.spec.ts` | Geographic Intelligence panel | Yes (fully mocked) | No | 11 tests of one advanced analytics feature (drag-pan, zoom, D3 internals) — too much surface/flake risk for a smoke gate; unsuitable for the initial blocking gate |
| `network_graph_visual.spec.ts` | Visual regression baselines | No — needs committed `--update-snapshots` baselines that don't exist in the repo | No | Explicitly out of scope per its own doc comment; would fail on first run regardless. Visual/research coverage, stays outside the critical gate |

---

## 4. CI design

- **Job name**: `frontend-e2e-critical` in `.github/workflows/lint.yml`
  (same file as `frontend-test`/`frontend-typecheck`/`frontend-lint`, which
  already trigger on `pull_request: branches: [main]`).
- **Trigger**: pull requests to `main` (and pushes to `main`/`develop`, via
  the workflow's existing top-level trigger).
- **Browser install**: `npx playwright install --with-deps chrome` — only
  the Chrome channel binary the existing `chromium` project (with
  `channel: "chrome"`) actually uses. No Firefox/WebKit.
  No cross-browser matrix — not justified by an observed compatibility need.
- **Server strategy**: `next build && next start` in CI, `next dev --webpack`
  unchanged for local dev. See §5 for the evidence.
- **Artifact strategy**: on every run (`if: always()`), upload
  `frontend/playwright-report/` (HTML report) and `frontend/test-results/`
  (per-test traces + screenshots-on-failure) as separate GitHub Actions
  artifacts, 7-day retention. `trace: "on-first-retry"` + `screenshot:
  "only-on-failure"` in `playwright.config.ts`. Video is off — the suite
  is fully API-mocked with short, deterministic flows, so trace + screenshot
  is enough to diagnose a failure without the extra artifact size/runtime.
- **Measured runtime**: see §5.

---

## 5. Server strategy evidence: `next dev` vs `next build && next start`

`playwright.config.ts`'s `webServer.command` previously ran
`next dev -p 3004 --webpack` unconditionally. During #290's validation, that
command proved unreliable under CPU/I/O-constrained conditions: `next dev`
itself reported "Ready" in ~10s, but the *first* request to any route then
blocked on on-demand webpack compilation and did not return within 60+
seconds, timing out Playwright's `webServer` health check entirely.

For #291, both strategies were measured head-to-head on the same
resource-constrained sandbox used for #290 (a 3-core container — the
conditions that broke `next dev`, not a favorable case for either strategy):

| Strategy | Startup | First route response | Subsequent routes |
| --- | --- | --- | --- |
| `next dev --webpack` | "Ready" in ~10s | Did not complete within 60s (timed out) | N/A — never got past the first route |
| `next build && next start` | Build ~70-90s, then "Ready" in ~10-22s | ~22s (one-time cold-start cost, not per-route) | `/login` 76ms, `/entities` 84ms |

`next start` serves prebuilt pages, so there is no per-route compilation
step — the one-time cost is amortized once, at startup, rather than paid
again on every first visit to every route. This is the reason CI uses
`npm run build && next start` while local development keeps `next dev`
(hot reload matters locally; determinism matters in CI, and `next start`'s
per-request latency is low enough that it does not materially slow the
suite).

---

## 6. Runtime target

**Target: median gate runtime under 10 minutes.**

Measured directly (not estimated) in the same sandbox used throughout: two
consecutive `npx playwright test --grep @critical` runs (6 tests across 5
files, `next build && next start` via the webServer, single worker, Chrome),
each preceded by a fresh `npx playwright install --with-deps chrome`:

| Run | Playwright-reported test duration (includes `next build`+`next start` via webServer) |
| --- | --- |
| 1 | 3.0 min |
| 2 (consecutive) | 2.8 min |

Add `npm ci` (~1-2 min with a warm npm cache, as CI has via
`actions/setup-node`'s `cache: npm`) and Chrome install (~1 min): **total job
runtime ≈ 5-6 min**, well under the 10-minute target with headroom for CI
runner variance. Exact CI numbers are in the `frontend-e2e-critical` job's
Actions run linked from the #291 PR.

---

## 7. Flakiness / ownership policy

- **Retries do not convert a flaky test into a healthy test.** CI retries
  (`retries: 2` under `process.env.CI`) exist to absorb genuine
  infrastructure noise (a slow runner, a transient port race), not to paper
  over a test that fails intermittently for reasons rooted in the test or
  the app.
- **Repeated retry-only passes are tracked as flakiness debt.** If a
  `@critical` test needs a retry to pass more than occasionally, that is a
  signal to fix the test (usually: replace an implicit wait with an explicit
  `expect(...).toBeVisible()` / route-mock ordering fix) or the underlying
  app behavior, not to leave it retrying indefinitely.
- **Deterministic product defects must not be muted with skips.** A
  `@critical` test failing because the app is actually broken is the gate
  doing its job. It gets fixed, not silenced.
- **No `test.skip()` / `test.fixme()` on a `@critical` test merely to turn CI
  green.** If a critical-path test cannot pass, the fix is to fix the
  journey or, if the journey's scope was wrong, to revise this document and
  the test together — not to skip it quietly.
- **Quarantine requires an explicit issue reference and an owner.** If a
  `@critical` test must be temporarily pulled from the blocking gate (remove
  the `@critical` tag, not skip it — the test keeps running locally/manually),
  the PR that does so must link the tracking issue and name an owner in this
  document.
- **Avoid arbitrary `waitForTimeout`.** Every test in this gate synchronizes
  on `expect(...).toBeVisible()`/`toHaveURL()`/route resolution, not fixed
  sleeps, with the sole justified exception already present in the (non-
  critical) visual-regression spec, which waits for a d3-force simulation to
  settle before a pixel-diff snapshot — a case with no meaningful
  visibility-based signal to wait on instead.
- **Ownership**: frontend/platform test owner (same owner as the other
  frontend CI gates in this file and in `docs/operating/SECURITY_GATES.md`).

**Current quarantines: none.**

---

## 8. Sentinel evidence (gate-failure proof)

Before landing, `navigation.spec.ts`'s enrichment-percentage assertion was
temporarily mutated from the correct fixture value to a value the mock never
returns:

```diff
- await expect(page.getByText("66.7%", { exact: true })).toBeVisible();
+ await expect(page.getByText("99.9%", { exact: true })).toBeVisible();
```

Running `npx playwright test --grep @critical` against the mutation: the
mutated test failed on all 3 attempts (initial + 2 CI retries,
`element(s) not found` for `getByText("99.9%")`), the process exited 1, and
the other 5 critical tests still passed — confirming the gate both fails on
a broken critical assertion and isolates that failure to the specific test,
rather than cascading. The mutation was reverted immediately after capturing
this evidence and is not present in the committed diff (`git diff` on
`navigation.spec.ts` at commit time shows only the real journey-4
tightening, not the mutation).

---

## 9. What the baseline audit actually found

Running this suite for the first time (nothing here had ever executed in CI
before #291) surfaced three pre-existing, real defects — not flaky
infrastructure — before the gate could go green:

1. **`login.spec.ts`'s password-field locator could never have matched.**
   `getByPlaceholder(/min\.?\s*8 caracteres/i)` targets the literal ASCII
   `i`, but the actual Spanish placeholder is "Mín. 8 caracteres" — the
   accented í is a distinct Unicode code point that `/i` case-insensitivity
   does not fold to plain `i`. This locator predates #291 and had never been
   exercised in CI. Fixed to `/m[ií]n\.?\s*8\s*caracteres/i`.
2. **The Analytics dashboard crashes when `EnrichmentSourceHealthCard`'s two
   endpoints return the page-wide `[]` catch-all.** The component does
   `for (const entry of stats.entries)` where `stats` comes from
   `/enrichment/sources/stats`; `[]` has no `.entries` property, so the
   whole `/analytics/dashboard` route threw via `analytics/error.tsx`
   ("r.entries is not iterable" in the minified production build). Fixed by
   giving `mockExecutiveDashboard` (in `helpers.ts`, shared by every test
   that uses it) explicit, correctly shaped mocks for
   `/enrichment/sources/health` and `/enrichment/sources/stats`.
3. **The same class of bug on the entity detail page.** `entities.spec.ts`
   (new) hit an identical crash: `attentionData.summary.active_sources`
   where `attentionData` was `[]` from the catch-all. Fixed with explicit
   `/entities/777/quality` and `/entities/777/attention` mocks matching
   the component's actual `EntityQualityData`/`EntityAttentionData` shapes.

These are exactly the class of defect #291 exists to catch: prior contract-
level tests (Vitest, typecheck) stayed green through all of them, because
none of them exercise a full page mount against production-shaped mock data
the way a browser-level test does. All three are fixed in this PR's diff, not
worked around.

---

## 10. Determinism requirements (how the five tests satisfy them)

- No test depends on a public external provider or live third-party API —
  every backend call is intercepted with `page.route()` against the
  `**/api/backend` glob already established by the pre-#291 suite.
- No live backend process is started for this gate. `frontend/e2e/helpers.ts`
  mocks auth, user identity, and every endpoint each journey touches.
- No wall-clock races: assertions synchronize on visibility/URL, not sleeps.
- No production credentials: `injectAuth` writes a mock JWT-shaped token that
  is never validated against a real backend, since the backend is mocked.
- Repeatable on a clean GitHub-hosted runner: the suite was run twice
  consecutively in a fresh container with no persisted state between runs
  (see the #291 PR's validation evidence) with identical results both times.

---

## 11. Related

- `docs/operating/SECURITY_GATES.md` — the security gate register this
  document deliberately mirrors in structure and owner.
- #290 — first documented this missing browser-level gate as a known
  validation gap after discovering it while implementing the Next.js
  security baseline upgrade.
- #291 — added this gate.
