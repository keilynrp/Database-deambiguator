# Design — embed widget distribution

## Decision 1: two base URLs, from two sources

The snippet needs both:

| Snippet | Target | Source |
|---|---|---|
| iframe | the **frontend** render page | `FRONTEND_URL` |
| JS | the **backend** JSON endpoint | `UKIP_PUBLIC_API_URL` |

`FRONTEND_URL` already exists, is read by `auth_users.py`, and is declared in
`docker-compose.prod.yml:47` and `.env.example:95`. Reusing it costs nothing and
keeps one canonical answer to "where does the app live".

`UKIP_PUBLIC_API_URL` is new on the backend. Rather than making it mandatory,
the resolver falls back to `str(request.base_url)`:

```
api_base = env("UKIP_PUBLIC_API_URL") or str(request.base_url).rstrip("/")
```

**Why a fallback and not just `request.base_url`?** Behind a reverse proxy,
`base_url` reflects what the proxy forwarded, which is correct only when
`--proxy-headers` and `X-Forwarded-*` are configured end to end. We do not want
snippet correctness silently coupled to proxy configuration, so an explicit
override wins when present. **Why not require the env var?** Because the failure
mode of an unset variable should be "probably right" (the origin the request
actually arrived on), not "definitely wrong" (`localhost`). Both are declared in
prod compose regardless — an env var read by code but absent from
`docker-compose.prod.yml` is a dead flag.

Trailing slashes are normalized once, in the resolver, not at each use site.

## Decision 2: the iframe points at the frontend, and `/frame` is deleted

`/embed/{token}/frame` was never implemented. Two ways to fix it:

- **(a) point at `{FRONTEND_URL}/embed/{token}`** — the React page already
  exists, already fetches `/embed/{token}/data`, and already renders all four
  widget types with real styling.
- (b) implement a server-rendered HTML `/frame` route on the backend.

Chosen (a). Option (b) means a second renderer for the same four widget types,
in a different language, that will drift from the first one. The page we already
built is the renderer.

## Decision 3: framing headers become per-path

Today `frontend/next.config.ts` applies to `/(.*)`:

```
X-Frame-Options: DENY
Content-Security-Policy: ... frame-ancestors 'none'
```

`X-Frame-Options` has no origin-list semantics worth using (`ALLOW-FROM` is
dead in every modern browser), so the mechanism is CSP `frame-ancestors`, and
`X-Frame-Options` must be **absent** on embed routes — present-and-`DENY` is
honoured by browsers that would otherwise respect the CSP.

Split the header config into two rules:

| Path | `X-Frame-Options` | `frame-ancestors` |
|---|---|---|
| `/embed/:path*` | *(omitted)* | per-widget (see below) |
| everything else | `DENY` | `'none'` |

Everything else in the CSP (script-src, connect-src, …) stays identical on both
rules; only the framing directives differ.

**Per-widget ancestors.** `next.config.ts` headers are static, so a widget whose
`allowed_origins` is `https://cliente.com` cannot get a tailored static header.
The embed page therefore emits the widget-specific `frame-ancestors` at request
time from its own route handler, using the `allowed_origins` returned by
`/embed/{token}/config`:

- `allowed_origins == "*"` → `frame-ancestors *`
- otherwise → `frame-ancestors <origin list>`

The static rule for `/embed/:path*` is the permissive floor (it must not say
`'none'`, or the dynamic header is moot); the dynamic header narrows it.

Note the honest limitation: `frame-ancestors` restricts *framing*, which
protects against clickjacking and unwanted display. It does not restrict
*reading* `/embed/{token}/data` with curl. See the non-goal in the proposal.

## Decision 4: the JS snippet renders, minimally

Replacing `<pre>{json}</pre>` with a small inline renderer — a heading and a
definition list of the widget's headline numbers — keeps the snippet
dependency-free and under ~25 lines while producing something a customer can
actually put on a page. Anything richer belongs in the iframe path, which is why
the iframe exists.

## What we are explicitly not fixing here

`_get_active_widget` looks up by `public_token` with no rate limiting, so the
token space is enumerable in principle (UUID4 — 122 bits, not realistically
enumerable, but unthrottled). Out of scope; noted for the record.

## Decision 5: `/embed/{token}/*` emits its own CORS header, derived from the widget

Added 2026-07-30, after the task 4.4 live check found the JS snippet blocked on
every third-party origin. The global CORS middleware answers from
`ALLOWED_ORIGINS`, which lists UKIP's own app origins — and a real embedder is
never in it. So the endpoint returns 200 with no `Access-Control-Allow-Origin`
and the browser discards the body: "Widget unavailable", on every customer site,
including one whose widget names that exact origin in `allowed_origins`.

The two public embed endpoints therefore set the header themselves, from the
widget's own `allowed_origins`:

| Widget `allowed_origins` | Response |
|---|---|
| `*` | `Access-Control-Allow-Origin: *` |
| a list, request `Origin` in it | `Access-Control-Allow-Origin: <that origin>` + `Vary: Origin` |
| a list, request `Origin` not in it | 403, as today; no ACAO |

`Vary: Origin` is not decoration. The reflected form varies by request, and
there is a Redis cache and potentially a CDN in front; without it one customer's
`Access-Control-Allow-Origin` can be served to another customer. The literal `*`
case needs no `Vary` because it does not vary.

No `Access-Control-Allow-Credentials`. There is no cookie and no session token
in this exchange, and `*` with credentials is invalid anyway.

**Why this is not a loosening.** CORS governs browser-mediated cross-origin
*reads*. These two endpoints are already unauthenticated and public: `curl`
retrieves them today, from anywhere, with no header at all. Emitting ACAO
therefore grants a browser exactly what every non-browser client already has,
and withholding it protects nothing while breaking the only documented use of
the feature. The credential here is the `public_token` in the path — that was
already the stated contract.

Two facts settle it rather than merely support it:

- The existing origin check is `if origin and origin not in allowed` — a request
  that simply **omits** `Origin` passes. Every non-browser client omits it. So
  the check was never an access boundary; it is a browser-facing policy.
- `API.md`, written in task 4.2 of this same change, already states that
  the token is the credential and that `allowed_origins` does **not** restrict
  data retrieval, and calls the Origin check "a courtesy filter, not a boundary:
  non-browser clients simply omit the header". Decision 5 makes the code agree
  with the contract we published, rather than the reverse.

The alternative of widening the global `ALLOWED_ORIGINS` was rejected: it would
expose the entire API — `/entities`, `/reports`, `/admin/*` — to every customer
origin, not the two public embed routes, and would require a production env
change per customer.

## Decision 6: `/embed` is a public route in the app shell, not only in the headers

The same live check found the iframe form broken for a second, independent
reason: `LayoutContent` allowlists exactly two paths that may render without a
session (`/login`, `/catalogs/*`). `/embed/{token}` is neither, so an anonymous
visitor is redirected to `/login` — which correctly denies framing, so the
customer's iframe shows a broken document.

`/embed/` joins that allowlist. The framing headers were only ever half the
answer: a route may be exempt from `X-Frame-Options` and still be unreachable
without a session. Nothing in the change checked the anonymous case, because the
redirect is client-side — the server serves the embed document with a 200, so
every response-level assertion passes.
