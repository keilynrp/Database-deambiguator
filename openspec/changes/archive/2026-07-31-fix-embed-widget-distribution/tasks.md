# Tasks — fix embed widget distribution

TDD throughout. Note that tasks 1–3 each start from a test that fails against
today's code — all three defects are currently unguarded.

## 0. URL resolution

- [x] 0.1 Failing test: generated snippets contain no `localhost` when
      `UKIP_PUBLIC_API_URL` and `FRONTEND_URL` are set. (RED — both are
      hardcoded today.)
- [x] 0.2 `_resolve_bases(request) -> (api_base, app_base)` in `widgets.py`:
      env first, `request.base_url` fallback for the API, single trailing-slash
      normalization.
- [x] 0.3 Tests: env set; env unset → request origin; trailing slash on either
      input produces no doubled separator.

## 1. Iframe target

- [x] 1.1 Failing test: the iframe `src` path resolves to a real application
      route. (RED — `/frame` does not exist.)
- [x] 1.2 Point the iframe at `{app_base}/embed/{token}`; delete `/frame`.
- [x] 1.3 Test: snippet contains no `/frame`.

## 2. Framing headers

- [x] 2.1 Failing test: a response from `/embed/...` does not carry
      `X-Frame-Options: DENY`. (RED — `next.config.ts` applies it to `/(.*)`.)
- [x] 2.2 Split `next.config.ts` headers into `/embed/:path*` and a catch-all;
      omit `X-Frame-Options` on the embed rule and set a permissive
      `frame-ancestors` floor. Every other directive stays identical.
- [x] 2.3 Emit the per-widget `frame-ancestors` at request time from the embed
      route, derived from the widget's `allowed_origins`.
- [x] 2.4 Tests: restricted widget → exactly its origins; `*` widget → any;
      a non-embed route still `DENY` + `'none'` (regression — this must not
      loosen the app).

## 3. Snippet rendering

- [x] 3.1 Replace the `<pre>JSON.stringify(...)</pre>` body with an inline
      labelled renderer per widget type. Dependency-free, no external assets.
- [x] 3.2 Tests: no raw serialization in the emitted snippet; no external
      `src`/`href`.

## 4. Config, docs, verification

- [x] 4.1 Declare `UKIP_PUBLIC_API_URL` in `docker-compose.prod.yml` **and**
      `.env.example`. (`FRONTEND_URL` is already in both — confirm, do not
      duplicate.)
- [x] 4.2 `docs/API.md`: the embed contract, both snippet forms, and an explicit
      statement that the token is the credential and `allowed_origins` governs
      framing, not data retrieval.
- [x] 4.3 Widget settings UI: same clarification next to the `allowed_origins`
      field, so the operator reads it where the decision is made.
- [x] 4.4 Live check — **RAN, AND IT FAILED.** The earlier parts stand (header
      split verified: `/login` keeps DENY + `'none'`; `/embed` drops
      X-Frame-Options; fail-closed `'none'` when config is unreachable;
      per-widget `frame-ancestors` from a mock config API). The part that was
      still open — pasting both snippets into a page served from a *different
      origin*, against a real backend and a real widget — was done on
      2026-07-30 against the docker stack (Postgres, real backend, real
      frontend) plus a static server on `:8899` standing in for the customer
      site, driven by a headless Chrome.

      **Neither snippet works on a third-party page.** Two independent,
      blocking defects. Both are invisible to every check that came before,
      and both are invisible to an operator previewing their own widget while
      logged in — which is how they shipped.

  - **A — the iframe form redirects anonymous visitors to `/login`.**
    `frontend/app/components/LayoutContent.tsx:21,25` allowlists exactly two
    public paths: `pathname === "/login"` and
    `pathname.startsWith("/catalogs/")`. `/embed/{token}` matches neither, so
    for a visitor with no token the guard calls `router.replace("/login")` and
    line 47 returns `null` before the widget renders. `/login` legitimately
    carries `frame-ancestors 'none'`, so the frame is then blocked and the
    customer sees a broken-document placeholder. The server does serve the
    embed document (16.9 KB of HTML, 200) — the redirect is client-side, which
    is why response-level checks pass. **Confirmed in production:**
    `https://ukip.inbounduxd.com/embed/{token}` lands on
    `https://ukip.inbounduxd.com/login`. Task 1.2 pointed the iframe at a route
    that exists; nothing checked that an anonymous visitor may see it.

  - **B — the JS form is blocked by CORS on every third-party origin.** The
    browser reports: *"Access to fetch at `…/embed/{token}/data` from origin
    `http://localhost:8899` has been blocked by CORS policy: No
    'Access-Control-Allow-Origin' header is present"*, and the container renders
    "Widget unavailable". CORS comes from the global `ALLOWED_ORIGINS`
    middleware (`backend/main.py:468`), which lists the UKIP app's own origins —
    a real embedder is never in it. Measured directly: from the customer origin
    the endpoint returns **200 with no ACAO header**; from
    `http://localhost:3004` it returns `ACAO: http://localhost:3004`. The
    endpoint's own per-widget origin check
    (`backend/routers/widgets.py:347-352`) authorises the request server-side
    and the transport layer then refuses to say so — including for the widget
    whose `allowed_origins` names that exact customer origin. The iframe form
    escapes this only because the iframe document is served from the app origin.

      **Also found, not a defect but a real gap:** `BACKEND_INTERNAL_URL` is
      read at `frontend/middleware.ts:17` and declared in **no** compose file
      and not in `.env.example`. Without it `API_BASE` falls back to the
      browser-facing `NEXT_PUBLIC_API_URL`; in prod that is a public URL, so the
      middleware's server-side config fetch leaves the container and comes back
      (works, but undeclared, and fails closed to `frame-ancestors 'none'` if
      egress is ever blocked). Separately, `UKIP_PUBLIC_API_URL` and
      `FRONTEND_URL` are declared in `docker-compose.prod.yml` but **not** in
      the local `docker-compose.yml`, so a local stack emits an iframe snippet
      pointing at the backend port instead of the app. Same rule as the
      authority work: an env var the code reads must be declared wherever the
      code runs.
- [x] 4.5 Full backend suite: 3311 passed / 7 skipped. Frontend: 302 passed, tsc clean. (`rm -rf frontend/.next`
      before pushing if a dev server ran (corrupt generated types break the
      pre-push tsc gate).
- [x] 4.6 PR — **already merged as #167** (`cd4896e7`, 2026-07-22); this task
      was simply never checked off. #165 was the same work on a branch abandoned
      because the ruleset blocks force-push and a GitGuardian finding on test
      UUIDs needed rewriting.

## 5. Blocked — the feature does not work end to end

4.4 shipped the change without its own acceptance check, and the check now says
the feature fails for its only intended audience. These are the tasks that close
it; neither is written yet, because B is a security-relevant policy decision
about a public endpoint and is the user's call.

- [x] 5.1 Allowlist `/embed/` so an anonymous visitor may render it. Done, and it
      took **two** fixes rather than one — the second only became visible because
      the first was applied and the page still bounced.

      The allowlist moved out of `LayoutContent` into `lib/publicRoutes.ts`
      (`isPublicRoute`, 7 tests). Two inline booleans are how `/embed` came to be
      missing; a named predicate is a place where "is this public?" gets answered
      on purpose. Matching is anchored on segment boundaries, so
      `/admin/embed/{token}`, `/loginx` and `/embedded/x` are not public.

  - **A second guard, in the fetch layer, kept redirecting.** `lib/api.ts` did
    `window.location.href = "/login"` on **any** 401. A public page still renders
    inside the app's provider tree, and those providers call `apiFetch` on mount
    (`/branding/settings`, `/enrich/stats`); with no session those answer 401 and
    the assignment is a hard navigation no route guard can veto. `apiFetch` now
    suppresses both the navigation and the token clear on a public route, while
    still returning the 401 to the caller. **`/catalogs/{slug}` had the identical
    hole** — it predates the embed work, so this was never embed-specific.
  - **Also fixed: an embed no longer renders inside the app shell.** A second
    predicate, `isStandaloneRoute`, covers `/login` and `/embed/*` and applies
    *regardless of session*, because the operator previewing their own widget
    would otherwise get the sidebar and header inside a 480x320 frame. The page's
    own docstring already said "no auth, no sidebar"; the shell contradicted it.
- [x] 5.2 CORS policy decided (design decision 5, written before implementing)
      and shipped: the two public embed endpoints emit their own
      `Access-Control-Allow-Origin` from the widget's `allowed_origins` — `*` when
      the widget is `*`, otherwise the requesting origin plus `Vary: Origin`.
      Never `Allow-Credentials`. `/snippet` gets nothing: an operator copies it
      out of the UKIP UI, a customer page never fetches it. 8 tests.

      **The route could not finish the job alone**, and this is the part worth
      remembering. Starlette's `CORSMiddleware` sits outside the route and runs
      `headers.update(self.simple_headers)` unconditionally on every request
      carrying an `Origin`; with `allow_credentials=True` in the global config
      that re-adds `Access-Control-Allow-Credentials: true` after the route has
      returned. Read from the Starlette source once the test failed, not guessed.
      So the route sets the ACAO and marks the response, and a tiny
      `EmbedCorsMiddleware` registered *after* `CORSMiddleware` — which makes it
      the outer of the two — removes the credentials header and the marker.
      Scoped by the marker rather than by path, so it cannot drift out of step
      with the routes it corrects.
- [x] 5.3 Declared `BACKEND_INTERNAL_URL` in `docker-compose.yml`,
      `docker-compose.prod.yml` and `.env.example`, and `UKIP_PUBLIC_API_URL` /
      `FRONTEND_URL` in the local `docker-compose.yml`. `API.md` gained the CORS
      contract beside the "the token is the credential" paragraph it already had.
- [x] 5.4 Live check re-run against the docker stack — **green for the JS form,
      and it is what caught the fetch-layer redirect in 5.1.** Both snippet forms
      now render real data on a page served from `:8899`, an origin absent from
      `ALLOWED_ORIGINS`: no CORS errors, no failed requests, per-widget ACAO
      confirmed (`*` widget → `*`; restricted widget → exactly its origin; the
      app's own origin → itself).

      ⚠️ For the record: the run mounts the working tree over `/app/backend`
      rather than rebuilding the 3 GB backend image, so the container runs local
      code, not a released artefact. The frontend *is* rebuilt, because
      `NEXT_PUBLIC_API_URL` is inlined at build time.
- [x] 5.5 **`frontend/__tests__/apiFetchUnauthorized.test.ts` executed and green —
      18/18 with `publicRoutes.test.ts`, in 39.6s.**

      It had never run at the time this task was written, and the reason is worth
      keeping: local vitest could not start a worker —
      `[vitest-pool-runner]: Timeout waiting for worker to respond`, before any
      test body ran. It was never this file. A three-line probe that only
      imported `lib/api` failed identically, and `publicRoutes.test.ts` passed
      cleanly four times and then began failing too. Cache clear, `wsl
      --shutdown` (0.76 GB → 2.33 GB available), and both `forks` and `threads`
      pools — no change. The plan was to let CI's `frontend-test` job be the
      first real run.

      **It was memory exhaustion, and it resolved when the host recovered.** Two
      things changed: a reboot cleared a non-paged-pool leak that was holding
      ~8 GB in no standard counter, and `.wslconfig` dropped the WSL cap 6GB →
      4GB. Available RAM went from 0.76 GB to 5.49 GB *with the docker stack
      running*, and the same command that used to hang now completes. The
      diagnosis "not the file, the harness" held up.

      Lesson: a test suite that cannot start a worker is a resource symptom, not
      a test defect — measure host memory before rewriting the test. See
      `local-docker-windows-gotchas` in the project memory.
