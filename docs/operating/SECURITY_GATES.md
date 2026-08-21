# Security Gates

Introduced: 2026-06-10. Owner: platform/security owner.

This document is the authoritative reference for every automated security gate in the UKIP pipeline. It defines what each gate checks, what blocks it, how to suppress findings, and the exception register that every suppression entry must appear in (§7).

---

## 1. Tool inventory

| Gate | Tool | Workflow file | What blocks | Suppression mechanism |
| --- | --- | --- | --- | --- |
| Secret scan | gitleaks (gitleaks/gitleaks-action@v2) | `.github/workflows/security.yml` | Any detected secret in PR commits | `.gitleaks.toml` allowlist |
| Backend deps (SCA) | pip-audit 2.10.1 (pinned) | `.github/workflows/security.yml` | Any non-ignored vulnerability in `requirements.lock` | `--ignore-vuln` flags on the audit command |
| Frontend deps (SCA) | npm audit via `frontend/scripts/check-npm-audit.mjs` wrapper | `.github/workflows/security.yml` | Non-allowlisted HIGH/CRITICAL in production deps | `frontend/.npm-audit-allowlist.json` (entries expire) |
| SAST | CodeQL (security-and-quality queries, python + javascript-typescript) | `.github/workflows/codeql.yml` | New HIGH/CRITICAL alerts once check is required | Dismiss-with-reason in GitHub code-scanning UI |
| Container scan | Trivy v0.36.0 | `.github/workflows/docker.yml` (all 3 images, pre-push) | CRITICAL with available fix (`ignore-unfixed: true`) | `.trivyignore` |
| SBOM | Syft via anchore/sbom-action@v0.24.0 | `.github/workflows/docker.yml` | n/a (evidence artifact, SPDX JSON, one per image per build, 90-day artifact retention) | n/a |
| Dependency updates | Dependabot weekly (pip, npm, github-actions) | `.github/dependabot.yml` | n/a (hygiene) | n/a |

---

## 2. Ratchet policy

New CRITICAL/HIGH findings block PRs. Pre-existing findings at gate introduction are documented in §7 (exceptions table) and targeted for remediation at the next scheduled dependency-upgrade window.

Inline ignores are banned. The suppression files and flags listed in §1 are the only permitted mechanisms for carrying a known finding past a gate. Any other form of suppression (disabling a job, skipping a step, force-pushing past a required check) requires explicit approval from the security/platform owner and a post-merge retroactive §7 entry within 24 hours.

---

## 3. Exception process

Every suppression entry requires all four of the following before the PR that introduces it is merged:

1. **Justification** — why the finding cannot be fixed now (e.g., no fix available, transitive dep awaiting upstream release).
2. **Owner** — the named role accountable for tracking and remediating.
3. **Expiry date** — the date by which the entry must be re-evaluated or removed.
4. **Register row** — a corresponding entry in §7 of this document.

**npm allowlist expiry semantics**: an entry is active through its expiry date and is enforced (i.e., will block if still present) starting the following day. The `check-npm-audit.mjs` wrapper reads the expiry field and enforces this automatically.

**Registry-outage resilience**: `npm audit` depends on the live npmjs.org advisory endpoint, which occasionally returns a transport error (e.g. a malformed/gzip body npm cannot parse) — a registry outage, not a finding. The wrapper retries a few times and, if the endpoint stays broken, fails **open** with a loud `WARNING` rather than blocking every PR org-wide. This applies **only** to transport errors: a real advisory report still fails closed, and a parseable report with an unrecognized schema still exits non-zero. Re-run the job once the registry recovers; the weekly scheduled scan is the backstop.

**Monthly review**: §7 is reviewed monthly. Expired entries that have not been renewed or resolved are escalated to the security/platform owner for immediate action.

---

## 4. Remediation SLA

| Severity | SLA from detection |
| --- | --- |
| CRITICAL | 7 calendar days |
| HIGH | 30 calendar days |

**Baseline entries** (pre-existing at gate introduction, 2026-06-10): target the next scheduled dependency-upgrade window. Each entry is tracked in §7.

---

## 5. Enforcement evidence (2026-06-10)

| Evidence | URL |
| --- | --- |
| gitleaks deliberately triggered with a fake AWS key (FAILED run; note: the canonical `AKIAIOSFODNN7EXAMPLE` is excluded by gitleaks default rules — a modified key was required to trigger) | https://github.com/keilynrp/universal-knowledge-intelligence-platform/actions/runs/27312644725 |
| First fully green Security Gates run (3 jobs: gitleaks, pip-audit, npm-audit) | https://github.com/keilynrp/universal-knowledge-intelligence-platform/actions/runs/27323826219 |
| CodeQL both languages green, 0 alerts baseline | https://github.com/keilynrp/universal-knowledge-intelligence-platform/actions/runs/27324118491 |
| Docker Images with Trivy + SBOM green, 3 SBOM artifacts | https://github.com/keilynrp/universal-knowledge-intelligence-platform/actions/runs/27326675433 |

The PR/evidence branch used to capture the gitleaks failure was deleted after capture (it contained a test secret pattern).

---

## 6. Operator steps (one-time, repo settings — pending)

The following steps must be completed by the security/platform owner in GitHub repository settings. Until they are done, ER-SDLC-001 remains at `implemented` rather than `operated`.

1. **Enable secret scanning + push protection**: Settings → Code security and analysis → enable Secret scanning and Push protection.
2. **Branch protection on `main`**: mark the following as required status checks:
   - `gitleaks`
   - `pip-audit`
   - `npm-audit`
   - `analyze (python)`
   - `analyze (javascript-typescript)`
   - `build-backend`
   - `build-frontend`
   - `build-engine`
3. After these settings are applied and the gates have operated on at least one real PR, ER-SDLC-001 moves from `implemented` to `operated`.

---

## 7. Exceptions table

### 7a. gitleaks allowlist (`.gitleaks.toml`)

EMPTY — no findings at gate introduction (2026-06-10).

### 7b. npm allowlist (`frontend/.npm-audit-allowlist.json`)

EMPTY as of 2026-08-20 — all eleven prior entries resolved by the Next.js
16.3.1 upgrade (#290) and removed. See the 2026-08-20 review note below for
the verification evidence; the pre-upgrade entries are preserved further
down for history.

**Review conducted 2026-08-20** (owner: platform owner). Baseline before this
review: `next` resolved to `16.2.10` per `package.json`'s declared range, but
`frontend/package-lock.json` had *already* drifted to `next@16.3.0` via a
routine Dependabot lockfile regen on 2026-08-14 (#283) — Dependabot runs on
GitHub's Linux infrastructure, so this was a legitimate resolution, just an
undocumented one. `package.json` was bumped to `next: ^16.3.1` /
`eslint-config-next: ^16.3.1` (latest stable 16.3.x at review time) and the
lockfile regenerated in a Linux container (`node:22-alpine`, matching
`frontend/Dockerfile` and `.github/workflows/security.yml`'s
`node-version: 22` — never on the Windows host, per the lockfile-regen
prohibition noted throughout this table). Resolved versions after upgrade:
`next@16.3.1`, `eslint-config-next@16.3.1`, `postcss@8.5.23`, `sharp@0.35.3`
(react/react-dom left untouched at `19.2.8`, not downgraded).

`npm audit --omit=dev --json` against the resulting lockfile reports **zero
vulnerabilities of any severity** (`"total": 0` across critical/high/
moderate/low/info) — not merely zero HIGH/CRITICAL. `npm run audit:gate`
passes cleanly with an empty allowlist. Per-advisory disposition:

| ID | Package | Prior severity | Disposition |
| --- | --- | --- | --- |
| 1124066 (GHSA-f88m-g3jw-g9cj) | sharp (bundled by next 16.x) | HIGH | **Removed — category B.** Fixed by next 16.3.x bundling a newer sharp; resolved sharp is now `0.35.3`. No longer emitted. |
| 1124170 (GHSA-6gpp-xcg3-4w24) | next 16.2.10 | HIGH | **Removed — category A.** Documented exit condition was "stable 16.3.0"; resolved is now `16.3.1`. No longer emitted. |
| 1124171 (GHSA-m99w-x7hq-7vfj) | next 16.2.10 | HIGH | **Removed — category A/E.** No longer emitted at 16.3.1. (Exposure was already assessed not-exposed: zero `use server` directives, re-verified 2026-08-20 — still zero.) |
| 1124184 (GHSA-89xv-2m56-2m9x) | next 16.2.10 | HIGH | **Removed — category A/E.** No longer emitted at 16.3.1. (Re-verified not exposed: no Server Actions, app still runs on `next start`.) |
| 1124186 (GHSA-68g3-v927-f742) | next 16.2.10 | MODERATE | **Removed — category A.** No longer emitted at 16.3.1. |
| 1124188 (GHSA-4633-3j49-mh5q) | next 16.2.10 | MODERATE | **Removed — category A.** No longer emitted at 16.3.1. |
| 1124190 (GHSA-4c39-4ccg-62r3) | next 16.2.10 | MODERATE | **Removed — category A/E.** No longer emitted at 16.3.1. (Re-verified not exposed: no Server Actions.) |
| 1124192 (GHSA-p9j2-gv94-2wf4) | next 16.2.10 | HIGH | **Removed — category A/E.** No longer emitted at 16.3.1. (Re-verified not exposed: `next.config.ts`'s only rewrite, `/api/backend/:path*` → `${BACKEND_INTERNAL}/:path*`, still has a fixed, env-derived destination hostname; only the path is caller-supplied.) |
| 1124194 (GHSA-q8wf-6r8g-63ch) | next 16.2.10 | MODERATE | **Removed — category A.** No longer emitted at 16.3.1. (`next/image` surface unchanged: still the single usage in `app/components/UserAvatar.tsx`.) |
| 1124196 (GHSA-955p-x3mx-jcvp) | next 16.2.10 | MODERATE | **Removed — category A/E.** No longer emitted at 16.3.1. (Re-verified not exposed: no Server Functions or Server Actions.) |
| 1124288 (GHSA-r28c-9q8g-f849) | postcss 8.5.13 | HIGH | **Removed — category A.** Exit condition was "postcss ≥ 8.5.18"; resolved is now `8.5.23`. No longer emitted, and `next`'s transitive-via-postcss propagation trigger is gone with it. |

`frontend/middleware.ts` was re-read in full as part of this review: it still
only sets response headers (CSP, `X-Content-Type-Options`, `Referrer-Policy`)
and always returns `NextResponse.next()` — it still performs no
authorization, and `/embed/:token` still relies on the backend validating the
widget token. No `"use server"` directives exist anywhere in `frontend/`
(checked 2026-08-20). No new Server Actions, Server Functions, or custom
servers were introduced. These conclusions do not change the disposition
above (the advisories are gone at the dependency level regardless), but they
are recorded because several rows above previously leaned on them for
"not exposed."

The prior entries (pre-2026-08-20, describing the `next 16.2.10` /
`postcss 8.5.13` baseline) are preserved below for history and are no longer
in force:

| ID | Package | Severity | Reason | Owner | Expires |
| --- | --- | --- | --- | --- | --- |
| 1124066 (GHSA-f88m-g3jw-g9cj) | sharp (bundled by next 16.x) | HIGH | npm's only "fix" is a semver-major *downgrade* to next 14. Real fix arrives when next bumps its bundled sharp. An npm `override` would force a lockfile regen, prohibited on Windows dev machines (strips linux native binaries — sharp is exactly such a module). | platform owner | 2026-08-21 |
| 1124170 (GHSA-6gpp-xcg3-4w24) | next 16.2.10 | HIGH | **APPLIES — priority item.** Middleware/proxy bypass. Precondition confirmed present: prod build logs `Next.js 16.2.10 (Turbopack)` and there is no i18n config. Bounded impact: `frontend/middleware.ts` only sets response headers and always returns `NextResponse.next()` — it performs no authorization. A bypass serves `/embed/:token` without its per-widget CSP `frame-ancestors` (defence-in-depth from PR #167); it grants no data access, since the widget token is the access control and is validated backend-side. | platform owner | 2026-08-21 |
| 1124171 (GHSA-m99w-x7hq-7vfj) | next 16.2.10 | HIGH | **Not exposed.** DoS in App Router Server Actions; the repo contains zero `use server` directives. | platform owner | 2026-08-21 |
| 1124184 (GHSA-89xv-2m56-2m9x) | next 16.2.10 | HIGH | **Not exposed.** SSRF in Server Actions on custom servers; no Server Actions exist and the app runs on `next start`. | platform owner | 2026-08-21 |
| 1124186 (GHSA-68g3-v927-f742) | next 16.2.10 | MODERATE | **Applies.** Cache confusion of response bodies for requests with bodies. Generic to the framework; no stable fixed release exists. | platform owner | 2026-08-21 |
| 1124188 (GHSA-4633-3j49-mh5q) | next 16.2.10 | MODERATE | **Applies.** Cache confusion variant for bodies with invalid UTF-8 sequences. Same posture as 1124186. | platform owner | 2026-08-21 |
| 1124190 (GHSA-4c39-4ccg-62r3) | next 16.2.10 | MODERATE | **Not exposed.** Unbounded Server Action payload in the Edge runtime; no Server Actions exist. | platform owner | 2026-08-21 |
| 1124192 (GHSA-p9j2-gv94-2wf4) | next 16.2.10 | HIGH | **Not exposed.** SSRF in rewrites via an attacker-controlled *destination hostname*. The only rewrite is `/api/backend/:path*` → `${BACKEND_INTERNAL}/:path*`; the hostname is fixed from env and only the path segment is caller-supplied. | platform owner | 2026-08-21 |
| 1124194 (GHSA-q8wf-6r8g-63ch) | next 16.2.10 | MODERATE | **Applies.** DoS in the Image Optimization API via SVGs. Minimal surface: one `next/image` usage (`app/components/UserAvatar.tsx`). | platform owner | 2026-08-21 |
| 1124196 (GHSA-955p-x3mx-jcvp) | next 16.2.10 | MODERATE | **Not exposed.** Unauthenticated disclosure of internal Server Function endpoints; no Server Functions or Server Actions exist. | platform owner | 2026-08-21 |
| 1124288 (GHSA-r28c-9q8g-f849) | postcss 8.5.13 | HIGH | **Not exposed.** Path traversal in previous-source-map auto-loading (`sourceMappingURL` → arbitrary `.map` disclosure). postcss runs at build time over first-party Tailwind/app CSS, never at runtime over untrusted CSS. Also unblocks `next`, which is flagged only transitively *via* postcss (propagation) even though its own nine advisories are already keyed. Real fix is postcss >8.5.17, deferred to Dependabot/CI (a Windows lockfile regen strips linux/native deps). Exit condition: postcss ≥ 8.5.18. | platform owner | 2026-08-21 |

Note (2026-07-23): the nine `next` entries above were added together because
the wrapper requires *every* advisory on a flagged package to be keyed before
that package clears — allowlisting only the ones that apply would not unblock
the gate. Five of the nine were assessed as not exposed and are keyed for that
mechanical reason, not because risk was accepted; the assessment for each is in
its Reason cell and in `frontend/.npm-audit-allowlist.json`.

There is **no stable release to upgrade to**: the vulnerable range is
`14.3.0-canary.0 - 16.3.0-preview.7`, so `16.2.11` (current latest stable) is
still inside it and only `16.3.0-preview.8+` carries the fix. Shipping a
preview build of the framework to production was judged the larger risk. **Exit
condition: stable 16.3.0.** Check for it on the expiry re-check; 1124170 is the
one to clear first.

Note (2026-07-22): the gate wrapper now propagates allowlist status through
purely-transitive findings (a package flagged only *via* another package is
allowed exactly when every such package is itself fully allowlisted). Without
this, `next`-via-`sharp` was impossible to allowlist at all: it exposes no
advisory id of its own to key an entry on. Propagation remains fail-closed —
it only flows from explicit entries.

Note (2026-07-24): advisory `1124288` (postcss, GHSA-r28c-9q8g-f849) was newly
published and blocked the gate on two packages at once — postcss directly, and
`next` transitively (its `via` chain includes `postcss`), even though all nine
of `next`'s own advisories were already keyed. The propagation rule above is why
one postcss entry clears both. The real fix is a postcss bump (>8.5.17); it is
left to Dependabot/CI rather than a Windows-local lockfile regen (which strips
linux/native optional deps). Exit condition: postcss ≥ 8.5.18.

Note (2026-08-20): both exit conditions above are now satisfied. Stable
Next.js 16.3.0 released 2026-08-03; a routine Dependabot lockfile regen on
2026-08-14 (#283) had already picked it up transparently under the existing
`^16.2.10` range (Dependabot runs on GitHub's Linux infra, so this was a
sound resolution, just undocumented — `package.json` itself was not bumped
until this review). `package.json` now declares `next: ^16.3.1` /
`eslint-config-next: ^16.3.1` (latest stable 16.3.x), and the lockfile
resolves `next@16.3.1`, `postcss@8.5.23` (clears the ≥8.5.18 exit condition),
and a bundled `sharp@0.35.3`. `npm audit --omit=dev --json` reports zero
vulnerabilities of any severity; all eleven entries in this section were
removed. See the 2026-08-20 review note above the entries table for the full
per-advisory disposition.

### 7c. Trivy ignore file (`.trivyignore`)

| CVE | Where | Severity | Reason | Owner | Review by |
| --- | --- | --- | --- | --- | --- |
| CVE-2026-59873 | node-tar inside the npm CLI of the node base image (frontend image) | CRITICAL | Not an app dependency: `usr/local/lib/node_modules/npm/...`. The standalone runtime (`node server.js`) never invokes npm or tar, so the gzip-bomb DoS vector is not reachable. Clears when the node base image ships npm with tar ≥7.5.19. | platform owner | 2026-08-21 |

### 7d. CodeQL baseline

0 alerts at gate introduction (2026-06-10).

### 7e. pip-audit baseline (`--ignore-vuln` flags in `.github/workflows/security.yml`)

**2 vulnerability IDs ignored** (down from 33). Owner: platform owner. SLA: next
dependency-upgrade window (review by 2026-09-30).

The previous baseline deferred most entries to "the upgrade sprint", noting in
particular that the starlette CVEs needed a major 0.52 -> 1.x bump. That bump
landed with #202, which aligned `requirements.lock` to the versions the backend
image actually resolves. The upgrade reached or passed every fix version this
table had recorded — starlette 0.52.1 -> 1.3.1, cryptography 46.0.5 -> 49.0.0,
python-multipart 0.0.22 -> 0.0.32, weasyprint 68.1 -> 69.0 — so 31 entries were
suppressing advisories that no longer apply and have been removed rather than
carried forward.

Verified empirically, not by reading the table: `pip-audit -r requirements.lock
--disable-pip --no-deps` with **no** ignore flags reports exactly the two rows
below, and with only these two it reports `No known vulnerabilities found, 2
ignored`.

Both remaining entries are recorded under the canonical IDs pip-audit emits.
The old list used CVE aliases, which is why a 34-flag list could still be doing
only two flags' worth of work — an alias that stops matching fails silently.

| ID | Package (pinned) | Fix version if known | Review date |
| --- | --- | --- | --- |
| PYSEC-2026-311 | chromadb==1.5.2 | none published | 2026-09-30 |
| PYSEC-2026-1325 | ecdsa==0.19.2 | none published | 2026-09-30 |

Note that `chromadb` is a lock-only entry: it constrains dev installs but is not
among the 97 packages the backend image installs, so its advisory does not apply
to the shipped artifact.

---

## 8. Known follow-ups (from gate reviews, non-blocking)

- Cache the Trivy vulnerability DB (`actions/cache` on `~/.cache/trivy`) to reduce network flakiness; a Trivy CDN outage currently blocks deploys (accepted trade-off for a hard gate).
- Consider registry layer cache (`cache-from`/`cache-to`) to avoid the double image build per job (scan build + push build).
- `gitleaks-action` requires a `GITLEAKS_LICENSE` secret if the repo ever moves to a GitHub organization; free for personal accounts.
- Dependency upgrades to burn down the 32-entry pip-audit baseline (§7e) need their own test pass before landing; plan as a dedicated upgrade sprint. Priority targets: starlette 0.52→1.x (4 CVEs; major bump, verify FastAPI compat), python-multipart →0.0.31 (3 CVEs), cryptography →48.0.1.
