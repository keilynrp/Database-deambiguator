# ER-SDLC-001 — Ruleset Activation Evidence (2026-08-27)

Prepared under: Issue #317 (`ER-SDLC-001` — operate blocking security/release
gates on `main`), following the compatibility-layer implementation in PR #318.

This file is evidence for one specific event — the live activation of a
`required_status_checks` rule on the `UKIP_System` repository ruleset — and
the formal start of the 30-day observation window that
`docs/product/ENTERPRISE_CONTROL_REGISTER.md` requires before `ER-SDLC-001`
may be considered for promotion from `implemented` to `operated`. It is not a
full P0/P1 control-reconciliation cycle; that lifecycle
(`docs/product/evidence/RC-*.md`, governed by
`docs/product/evidence/README.md`) is separate and unaffected by this file.

**This file does not change, and does not claim to change, `ER-SDLC-001`'s
maturity.** It remains `implemented` in both
`docs/product/ENTERPRISE_CONTROL_REGISTER.md` and
`backend/enterprise_controls.py`. See §7.

## 1. Activation identity

| Field | Value |
| --- | --- |
| Issue | #317 |
| Implementation PR | #318 (compatibility layer — five stable `*-required-gate` aggregation jobs; did not itself mutate the live ruleset) |
| PR #318 merge commit (= `main` tip at activation) | `4979555cd42960622c60092c2812c973eb21fe7e` |
| Ruleset | `UKIP_System`, id `18524885` |
| Ruleset target | `branch`, `conditions.ref_name.include: ["~DEFAULT_BRANCH"]`, `exclude: []` |
| Activation timestamp | `2026-08-27T02:58:08.760-06:00` |

Independently re-verified in this evidence cycle by a direct, read-only
`gh api repos/keilynrp/universal-knowledge-intelligence-platform/rulesets/18524885`
call: the live ruleset's `updated_at` field returns exactly
`2026-08-27T02:58:08.760-06:00`, matching the activation timestamp above. No
value in this file was taken on trust without this independent re-check.

## 2. Before-state (pre-activation, as recorded in `docs/operating/SECURITY_GATES.md` §6.1 at PR #318)

- `enforcement`: `active`
- `bypass_actors`: `[]`
- Rules present: `deletion`, `non_fast_forward`
- `required_status_checks` rule: **absent**

## 3. After-state (live, independently observed 2026-08-27)

- `enforcement`: `active`
- `target`: `branch`
- `conditions.ref_name.include`: `["~DEFAULT_BRANCH"]`, `exclude`: `[]`
- `bypass_actors`: `[]`
- `current_user_can_bypass`: `never`
- Rules present: `deletion`, `non_fast_forward`, `required_status_checks`
- `required_status_checks.strict_required_status_checks_policy`: `false`
- `required_status_checks.do_not_enforce_on_create`: `false`

### 3.1 The five required contexts (live, exact)

| Context | `integration_id` |
| --- | --- |
| `backend-required-gate` | 15368 |
| `lint-required-gate` | 15368 |
| `security-required-gate` | 15368 |
| `codeql-required-gate` | 15368 |
| `docker-required-gate` | 15368 |

`integration_id: 15368` on all five pins each required check to the GitHub
Actions App specifically (not an arbitrary same-named external status), per
GitHub's ruleset `required_status_checks` context-binding model. These are
exactly the five aggregation jobs added by PR #318 — no hand-enumerated
per-shard/per-matrix job name is required, by design (see
`docs/operating/SECURITY_GATES.md` §6.1 and `scripts/lint_required_gates.py`).

This is the only ruleset on the repository (`gh api .../rulesets` returns a
single entry: id `18524885`, `UKIP_System`, `enforcement: active`) — there is
no second, conflicting, or shadow ruleset.

## 4. Workflow-run evidence that the five contexts are real and green at the activation SHA

All run/job IDs below were fetched from the GitHub Actions API on 2026-08-27
and are exact, not reconstructed from memory or chat.

### 4.1 Pre-merge PR validation (`pull_request` event, PR #318 final head `83bfc467f49e65c7fd558b25c724dfaaccc2f64a`)

| Workflow | Run ID | Conclusion |
| --- | --- | --- |
| Backend Tests | `33053480569` | success |
| Lint | `33053480530` | success |
| Security Gates | `33053480603` | success |
| CodeQL | `33053480548` | success |
| Docker Images | `33053480574` | success |

Each run above was independently re-verified (2026-08-27, via
`gh api repos/keilynrp/universal-knowledge-intelligence-platform/actions/runs/<id>`)
to have `head_sha: 83bfc467f49e65c7fd558b25c724dfaaccc2f64a`, `event:
pull_request`, and `conclusion: success` — this is PR #318's final commit
(the commit immediately preceding its merge into `4979555c...`, per
`gh pr view 318`), not an intermediate PR head.

### 4.2 Post-merge push-to-main validation (`push` event, exact activation SHA `4979555cd42960622c60092c2812c973eb21fe7e`)

| Workflow | Run ID | Required-gate job | Job ID | Job conclusion |
| --- | --- | --- | --- | --- |
| Backend Tests | `33055363306` | `backend-required-gate` | `98464733864` | success |
| Lint | `33055363223` | `lint-required-gate` | `98461220445` | success |
| Security Gates | `33055363349` | `security-required-gate` | `98460829131` | success |
| CodeQL | `33055363290` | `codeql-required-gate` | `98461267159` | success |
| Docker Images | `33055363330` | `docker-required-gate` | `98461499070` | success |

Both the final pre-merge PR validation on
`83bfc467f49e65c7fd558b25c724dfaaccc2f64a` and the independent post-merge
push-to-main validation on activation SHA
`4979555cd42960622c60092c2812c973eb21fe7e` are clean — unlike the flake
recorded in `docs/product/evidence/RC-2026-08-26-01.md` §5.2–§5.3 for a prior
SHA, there is no discrepancy between the two runs here.

### 4.3 Supply-chain / SBOM evidence (Docker Images run `33055363330`)

Confirmed via the run's artifact list (fetched 2026-08-27, all `expired: false`,
`expires_at: 2026-11-25T08:44:24Z`):

- `sbom-backend-4979555cd42960622c60092c2812c973eb21fe7e.spdx.json` (artifact `9639418651`)
- `sbom-frontend-4979555cd42960622c60092c2812c973eb21fe7e.spdx.json` (artifact `9639407644`)
- `sbom-engine-4979555cd42960622c60092c2812c973eb21fe7e.spdx.json` (artifact `9639430073`)

## 5. Secret scanning / push protection (independently observed, read-only, 2026-08-27)

`gh api repos/keilynrp/universal-knowledge-intelligence-platform` →
`security_and_analysis`:

| Feature | Status |
| --- | --- |
| `secret_scanning` | `enabled` |
| `secret_scanning_push_protection` | `enabled` |
| `secret_scanning_validity_checks` | `disabled` |
| `secret_scanning_non_provider_patterns` | `disabled` |
| `dependabot_security_updates` | `disabled` |

Open secret-scanning alerts at time of observation: `0`
(`gh api .../secret-scanning/alerts?state=open` → empty list).

This corrects the residual-risk note in
`docs/product/evidence/RC-2026-08-26-01.md` §5.5, which recorded (as of
2026-08-26, before this activation) that push protection and required checks
were not enabled — that finding is now superseded for both items as of the
timestamp in §1.

## 6. The 30-day observation window (`ER-SDLC-001`)

| Field | Value |
| --- | --- |
| Window start | `2026-08-27T02:58:08.760-06:00` |
| Window target end | `2026-09-26T02:58:08.760-06:00` |

### 6.1 Evidence to retain for the duration of the window

- Authoritative workflow run IDs (`test.yml`, `lint.yml`, `security.yml`,
  `codeql.yml`, `docker.yml`) for every push to `main` during the window.
- The five `*-required-gate` aggregate job run/job IDs for each of those runs.
- SBOM artifacts (`sbom-{backend,frontend,engine}-<sha>.spdx.json`) for every
  `docker.yml` run during the window, noted before their retention window
  (currently 90 days per GitHub default; `docker.yml` does not override
  `retention-days`) expires.
- Any other security artifacts produced by `security.yml` / `codeql.yml`
  during the window.
- Any gate failure on `main` (push event), whether infra-flake or real, with
  the same non-smoothed-over treatment as
  `docs/product/evidence/RC-2026-08-26-01.md` §5.2–§5.3.
- Any exception filed under `docs/operating/SECURITY_GATES.md` §7 during the
  window.
- Any bypass attempt (there are zero `bypass_actors` and
  `current_user_can_bypass: never` as of §3, so any successful bypass would
  itself be an invalidation event per §6.2).
- Any configuration drift on the `UKIP_System` ruleset (re-checked, not
  assumed unchanged, at window end).
- Any invalidation event per §6.2, and the remediation or restart decision
  made in response.

### 6.2 Invalidation conditions

The window is invalidated (requiring an explicit remediation/restart decision
by the accountable owner, §8) if, before the target end date, any of the
following occurs:

1. One of the five required contexts (`backend-required-gate`,
   `lint-required-gate`, `security-required-gate`, `codeql-required-gate`,
   `docker-required-gate`) is removed or renamed in the ruleset or in the
   workflow that emits it.
2. The `integration_id: 15368` binding on any of the five contexts is
   removed or changed.
3. `bypass_actors` becomes non-empty, or `current_user_can_bypass` becomes
   anything other than `never`.
4. `enforcement` on `UKIP_System` is set to anything other than `active`.
5. `conditions.ref_name` stops covering `main` (e.g. the `~DEFAULT_BRANCH`
   include is narrowed, excluded, or the target changes away from `branch`).
6. A required workflow (`test.yml`, `lint.yml`, `security.yml`,
   `codeql.yml`, `docker.yml`) ceases to execute on pull requests targeting
   `main`, or its `*-required-gate` job is removed.
7. Required evidence retention (per §6.1) becomes unavailable — e.g. a run
   or artifact needed to reconstruct the window's history is deleted or
   expires before being archived.
8. The ruleset is materially changed (any rule added, removed, or
   reconfigured beyond the five required contexts above) without equivalent
   evidence of the change being produced in the same style as this file.

A configuration-drift check equivalent to §3 (a fresh
`gh api .../rulesets/18524885` read) must be performed no later than the
target end date to confirm none of the above occurred undetected.

## 7. Maturity: unchanged

**`ER-SDLC-001` remains `implemented`.** This file records that the gate
described in `docs/product/ENTERPRISE_CONTROL_REGISTER.md`'s next-gate column
("Enable required checks and push protection") is now live, and that the
30-day observation-window clock required by the same register row ("30 days
of blocking gate operation and retained SBOM/security artifacts") has started
— it does not itself advance `current_maturity` in either
`docs/product/ENTERPRISE_CONTROL_REGISTER.md` or
`backend/enterprise_controls.py`. Per §8, promotion to `operated` requires a
full window, a retained-evidence review, and an accountable-owner
attestation — not the activation event alone.

## 8. Accountable roles

| Role | Responsibility for this window |
| --- | --- |
| Security/platform owner | Accountable owner for `ER-SDLC-001`; owns the go/no-go decision on any invalidation event (§6.2) and the final attestation (§9) at window end. |
| Product Owner / governance approver | Authorizes any further live ruleset mutation (there is none planned during this window) and reviews this evidence file and the eventual attestation before `ER-SDLC-001` is put forward for promotion. |
| Implementation engineer (PR #318) | Maintains `scripts/lint_required_gates.py` and the five workflow files so the required contexts keep matching their workflows' actual blocking jobs for the duration of the window; flags drift immediately rather than at window end. |

## 9. Final attestation requirements (at window end, 2026-09-26 or later)

`ER-SDLC-001` may be evaluated for promotion from `implemented` to `operated`
only after **all** of the following are true:

- [ ] The full 30-day duration (§6) has elapsed without an unresolved
      invalidation event (§6.2).
- [ ] The evidence retained per §6.1 has been reviewed in full by the
      accountable owner (not sampled, not assumed).
- [ ] Any invalidation event that did occur during the window has been
      resolved, with its remediation/restart decision documented.
- [ ] Any exception filed during the window (`docs/operating/SECURITY_GATES.md`
      §7) has been reconciled — closed, extended with justification, or
      escalated.
- [ ] The accountable owner (Security/platform owner) has recorded a signed
      attestation, following the same non-self-attestation spirit as
      `docs/product/evidence/RC-2026-08-26-01.md` §9 and
      `docs/product/ENTERPRISE_READINESS_PROGRAM.md` §8.
- [ ] Only then is `ER-SDLC-001` put forward for promotion — as a change to
      `docs/product/ENTERPRISE_CONTROL_REGISTER.md` and
      `backend/enterprise_controls.py` reviewed on its own terms, never as a
      side effect of this file or of window expiry alone.

| Role | Name | Date | Signature/reference |
| --- | --- | --- | --- |
| Accountable (Security/platform owner) | _pending — window not yet complete_ | _pending_ | _pending_ |

## 10. Residual risks and limitations

- This file evidences activation and defines the window; it does not and
  cannot evidence 30 days of sustained operation in advance. §6.1's ongoing
  retention is a forward-looking commitment, not a completed fact as of this
  file's date.
- `secret_scanning_validity_checks` and `secret_scanning_non_provider_patterns`
  remain `disabled` (§5). These are not required by `ER-SDLC-001`'s stated
  scope (secret scanning + push protection), but are noted here as an
  observed platform-configuration fact, not silently omitted.
- `dependabot_security_updates` is `disabled` (§5); this is a separate,
  pre-existing control question (Dependabot version-update PRs already run
  per `.github/dependabot.yml`, per `docs/operating/SECURITY_GATES.md` §1)
  and is out of scope for this activation-evidence file.
- SBOM artifacts cited in §4.3 are subject to their stated GitHub Actions
  retention window and are not guaranteed indefinitely inspectable; this file
  records their IDs and non-expired state as of 2026-08-27, not a live link.
- As recorded in `docs/operating/SECURITY_GATES.md` §6.1, the ruleset
  `workflows` rule type is unavailable at this repository/ruleset scope; the
  `required_status_checks` primitive activated here is the correct
  repository-level substitute, not a lesser workaround, but it is a
  genuinely different rule type than an org/enterprise-level ruleset would
  expose.

## 11. Cross-references

- `docs/operating/SECURITY_GATES.md` §6 — operator steps, now updated to
  reflect this activation.
- `docs/product/ENTERPRISE_CONTROL_REGISTER.md` — authority on `ER-SDLC-001`
  status; unchanged by this file (§7).
- `backend/enterprise_controls.py` — machine-readable control manifest;
  unchanged by this file (§7).
- `docs/product/evidence/RC-2026-08-26-01.md` — the release-evidence cycle
  that most recently reconciled `ER-SDLC-001` (as `PARTIALLY EVIDENCED`,
  pre-activation) and independently confirmed the pre-activation gap this
  file closes.
- Issue #317, PR #318.

**ARCHITECTURE_DECISION_REQUIRED: None.** No governance ambiguity was found
while preparing this evidence file.
