# UKIP Engineering Stabilization Plan — 2026 Q3

Status: Proposed execution baseline  
Date: 2026-08-20  
Scope: stabilization, production confidence, maintainability, and delivery speed  
Rule: no broad feature expansion should outrank unresolved P0 items in this plan.

## 1. Why this plan exists

UKIP has moved beyond a conventional MVP. The current repository already carries a broad production-oriented surface: FastAPI, PostgreSQL, Redis, Next.js/React, a Rust/gRPC engine, generated SDKs, analytics, authority resolution, enrichment, reporting, durable jobs, retrospective intelligence, security gates, and several thousand backend tests.

The dominant engineering risk is therefore no longer missing functionality. It is complexity: multiple execution paths can bypass contracts even when component-level tests are strong. Recent reporting/i18n defects, the corrected pre-push suite-selection bug, PostgreSQL-vs-SQLite production escapes, and documentation/security baseline drift are evidence of that transition.

This plan converts those findings into a bounded stabilization program. It reuses existing epics and issues rather than creating a parallel roadmap.

## 2. Governing principles

1. **Close systemic classes of failure, not only individual symptoms.**
2. **Preserve existing test/security guarantees while shortening feedback loops.**
3. **Prefer bounded-module hardening over premature microservice extraction.**
4. **Make production dialect and user-visible journeys first-class validation targets.**
5. **Treat documentation and security exceptions as executable contracts, not prose.**
6. **Use existing delivery governance:** `PROGRAM_BACKLOG`, issues, PRs, ADR/OpenSpec where architecture or contracts change.

## 3. Priority model

| Priority | Meaning | Release posture |
| --- | --- | --- |
| P0 | Current security or production-confidence risk | Must be addressed before broad feature expansion |
| P1 | Structural reliability / developer-velocity debt | Next stabilization tranche after P0 |
| P2 | Sustainable architecture and governance | Schedule after P0/P1 are controlled |

## 4. P0 — immediate stabilization

### P0-A — Framework security baseline

Issue: #290 — Reassess Next.js security baseline and upgrade to stable 16.3.x  
Epic: EPIC-018  
Primary outcome: remove stale security exceptions whose declared exit condition is now actionable.

Exit criteria:
- Linux `npm ci`, tests, typecheck, lint, build, container build and Trivy are green.
- `npm audit` exception register contains only currently justified entries.
- `docs/operating/SECURITY_GATES.md` matches the shipped dependency state.

### P0-B — Browser critical-path gate

Issue: #291 — Add Playwright critical-path gate to CI  
Epics: EPIC-011 / EPIC-014  
Primary outcome: detect user-visible regressions that contract/unit tests can miss.

Initial journeys:
1. login -> authenticated workspace;
2. ingest/import -> entity explorer;
3. entity search -> detail;
4. analytics/dashboard load;
5. report generation EN/ES.

Exit criteria:
- at least five deterministic Playwright journeys;
- blocking PR gate for affected user journeys;
- trace/screenshot failure evidence;
- normal target runtime under 10 minutes.

### P0-C — Finish current Spanish reporting correction

Existing issue: #268  
Current PR: #289  
Epic: EPIC-008

Exit criteria:
- PR #289 passes the repository's full relevant validation before merge;
- Spanish report output is verified at rendered-output level, not key-presence level only;
- remaining #268 scope is explicitly enumerated from real output/contract evidence.

## 5. P1 — structural hardening

### P1-A — Single report localization/render boundary

Issue: #292  
Epic: EPIC-008

Target architecture:

```text
Collector
  -> semantic ReportDomainModel
  -> LocalizedReportDocument
  -> HTML / PDF / XLSX / PPTX adapters
```

Invariant: no renderer/exporter may consume unresolved user-facing catalog keys or bypass the localized document boundary.

Exit criteria:
- all four artifact paths consume one localized boundary;
- bespoke writers do not read raw collector copy;
- populated + empty EN/ES regression coverage exists;
- a structural/property test rejects future bypass paths.

### P1-B — Persist translation references, not rendered language

Existing issue: #269  
Related domains: enrichment / demo persistence

Target stored shape:

```json
{
  "key": "validation.example",
  "params": {"provider": "OpenAlex"}
}
```

with backward-compatible reads for legacy rows containing rendered Spanish text.

Exit criteria:
- new writes persist key + parameters where UKIP owns the copy;
- reads support legacy and structured representations;
- language choice happens on read/render, not at persistence time;
- migration/backfill posture is documented and tested.

### P1-C — Test partitioning and CI parallelization

Issue: #293  
Epic: EPIC-011

Goal: preserve current test confidence while improving feedback latency.

Minimum taxonomy (subject to implementation evidence): unit, contract, integration, postgres, slow, reporting, security.

Exit criteria:
- deterministic marker policy;
- no accidental omissions between partitions and full suite;
- production-dialect PostgreSQL lane remains blocking;
- coverage threshold is not lowered for speed;
- PR fast-feedback target <10 minutes under normal conditions;
- full validation target <20 minutes where infrastructure permits.

### P1-D — Lint debt ratchet

Issue: #294  
Epics: EPIC-011 / EPIC-014

Exit criteria:
- repo-wide Ruff and ESLint debt is measured in a machine-readable baseline;
- CI blocks any increase;
- changed/new code remains strict;
- cleanup PRs ratchet the baseline downward;
- eventual repo-wide blocking conditions are documented.

## 6. P2 — sustainable evolution

### P2-A — Generated repository metrics

Issue: #295

Goal: eliminate manually maintained capability/test/version claims that drift from the repository.

Exit criteria:
- deterministic metric generator/checker;
- CI drift check;
- README volatile counts are generated or explicitly approximate/date-stamped;
- documentation governance names the source of truth.

### P2-B — Capability support tiers and bounded-module map

Issue: #296  
Related epics: EPIC-001..018 as applicable

Support tiers:
- Tier 1 — core product / release-blocking;
- Tier 2 — production-supported;
- Tier 3 — experimental;
- Tier 4 — research/incubating.

Exit criteria:
- capability inventory and tier assignment;
- Tier 1/2 ownership/boundary map;
- cross-capability dependency map;
- release gates mapped to supported capabilities;
- bounded-module cleanup candidates documented in the canonical architecture artifact;
- no service extraction without measured scaling/ownership justification.

## 7. Recommended execution order

| Order | Item | Priority | Dependency |
| ---: | --- | --- | --- |
| 1 | #290 Next.js security baseline | P0 | none |
| 2 | #289 / #268 Spanish reporting correction | P0 | current branch validation |
| 3 | #291 Playwright critical path | P0 | stable representative seed/fixtures |
| 4 | #292 unified report boundary | P1 | evidence from #268/#289 |
| 5 | #269 persisted translation references | P1 | localization contract understood |
| 6 | #293 test partitioning | P1 | preserve current full-suite semantics |
| 7 | #294 lint ratchet | P1 | capture factual baseline |
| 8 | #295 generated repository metrics | P2 | stable metric definitions |
| 9 | #296 capability support tiers | P2 | stabilized P0/P1 boundaries |

## 8. Stabilization KPIs

| KPI | Target |
| --- | ---: |
| Expired security exceptions | 0 |
| Critical browser journeys | >= 5 |
| Spanish owned-copy leakage in reports | 0 |
| PR fast-feedback target | < 10 min |
| Full CI target | < 20 min where infrastructure permits |
| Backend coverage | never below current 75% gate; raise only with evidence |
| PostgreSQL-specific escaped defects | 0 trend target |
| Ruff / ESLint debt | monotonic decrease |
| OpenAPI / SDK / i18n drift | 0 |
| Generated documentation metric drift | 0 |

## 9. Feature-expansion guardrail

Until P0 is cleared, new broad capabilities should require an explicit justification showing why they outrank a current security or production-confidence risk.

This is not a feature freeze for defects, small UX improvements, dependency maintenance, or work required to close P0/P1. It is a sequencing rule intended to stop UKIP's capability surface from growing faster than its operational contracts.

## 10. Definition of stabilization done

The 2026 Q3 stabilization tranche is complete when:

- all P0 items are closed with evidence;
- #268 and #269 are closed or have a consciously accepted residual scope with owner and exit criteria;
- the report renderer boundary is structurally enforced;
- critical browser journeys are blocking in CI;
- test feedback is partitioned without weakening the full-suite backstop;
- lint debt cannot increase silently;
- security/documentation baselines are factual and executable;
- P2 capability tiers provide a clear basis for deciding what UKIP supports as production product versus experiment.
