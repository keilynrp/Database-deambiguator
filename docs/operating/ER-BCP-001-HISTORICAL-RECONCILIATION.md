# ER-BCP-001 — Historical Branch Reconciliation

This is the Phase A audit of the historical branch
`ops/epic018-backup-restore@705b73b37dc1348a1c2494722d4bd65d59dd0b12` against
`main@358f1b84a62246d780ad4d6fdd9d99fab7626ba8`, produced for issue #320.

The historical branch is **282 commits behind** current `main` and has **2
commits unique to it**, touching exactly two files:

- `.github/workflows/backup-freshness.yml`
- `docs/operating/BACKUP_RESTORE_RUNBOOK.md`

It is **not merged or cherry-picked**. Current `main` already carries a more
complete, tested backup-assurance implementation
(`backend/backup_assurance.py`, `backend/backup_assurance_ddl.py`,
`backend/routers/backup_ops.py`, `backend/scripts/validate_restore.py`, the
`backup_assurance_events` migration, and their own
`docs/operating/BACKUP_RESTORE_RUNBOOK.md` and
`docs/operating/templates/BACKUP_RESTORE_EVIDENCE_TEMPLATE.md`) that this
historical branch predates by 282 commits. This document reconciles the two
historical artifacts against that current architecture concept by concept.

## Useful concepts still missing from main (adopted)

| Concept | Disposition |
| --- | --- |
| A scheduled, read-only job that actually queries the S3-compatible provider | Adopted. Current `main` had the receiving/evaluating side (`POST /ops/backups/events`, `GET /ops/backups/status`, the `backup_freshness` entry in `GET /ops/checks`) but nothing that observes the live provider. `.github/workflows/backup-freshness.yml` fills that gap. |
| Daily cadence (~07:00 UTC, four hours after an assumed 03:00 backup window) and a default `pg/` bucket prefix | Adopted as sensible, configurable defaults. |
| Two separate S3 credential sets — write for the provider, read-only for CI | Adopted. The reconciled workflow only ever receives the read-only set. |
| The open `ukip_static_data` checklist item (inspect the volume during the first drill; record whether it holds non-regenerable state) | Already present almost verbatim in current `docs/operating/BACKUP_RESTORE_RUNBOOK.md` §Recovery Scope; carried into the new readiness evidence dossier's durable-state review section so it is filled in per gate, not just described once. |

## Concepts already superseded by current main (not reused as-is)

| Concept | Why it is superseded |
| --- | --- |
| The June runbook's Dokploy/S3 configuration walkthrough (§3) | Current `docs/operating/BACKUP_RESTORE_RUNBOOK.md` §1–3 already covers provider configuration in a way that matches the current provider-neutral model: the application never touches storage credentials (`backend/backup_assurance.py` only persists metadata). |
| The June runbook's manual PostgreSQL drill steps (§5: hand-typed `psql`/`pg_restore`, row-count spot checks, an inline Python decrypt-probe pasted into a Dokploy terminal) | Replaced by `backend/scripts/validate_restore.py`, one auditable, tested, read-only validator invoked by a single documented command (contract-tested in `backend/tests/test_backup_runbook_contract.py`). Reusing the manual steps would be a regression from a tested script back to hand-typed terminal commands. |
| The June runbook's flat drill-report template (§6) | Superseded by `docs/operating/templates/BACKUP_RESTORE_EVIDENCE_TEMPLATE.md`, which is itself contract-tested (`test_backup_restore_evidence_template_captures_required_fields`) and already covers RPO/RTO, a validation table, exceptions/corrective actions, and approval sign-off. |
| Fixed quarterly review cadence language | Current control-register framing ties review to control gates, releases, and incidents rather than a fixed calendar clock; not reused as a hard commitment here. |
| RPO ≤ 24h / RTO ≤ 4h objectives | Unchanged — identical in the historical runbook and current main. No escalation needed. **ARCHITECTURE_DECISION_REQUIRED: none.** |

## Concepts rejected as obsolete or unsafe

| Concept | Why it is rejected |
| --- | --- |
| The June workflow's own bash-computed staleness arithmetic (`MAX_AGE_HOURS=26`, manual epoch subtraction) as the pass/fail authority | Rejected as the decision-maker. It duplicates `backend.backup_assurance.evaluate_backup_freshness`, which is already the single tested, governed evaluator on `main`. Two independent staleness calculators (one in bash, one in Python) risk silent drift if thresholds are ever tuned in one place and not the other. The reconciled workflow observes the provider and records what it saw, then defers the actual pass/fail decision to `GET /ops/backups/status`. |
| Hand-typed `psql`/`pg_restore` terminal commands against a live container, including an inline multi-line Python one-liner pasted into a Dokploy web terminal | Rejected as an operational path now that `validate_restore.py` exists. The script's explicit `--expected-target-host`/`--expected-target-database` guard and fail-closed production-marker check are materially safer than a human retyping commands under terminal paste constraints. |
| The June runbook's static named-approval header ("Approved by: Jose Paul, 2026-06-10") baked into the runbook prose | Not reused verbatim. The current evidence template already carries a per-instance Operator/Approver field, which is the right shape for evidence that must be produced repeatedly and retained for 12 months, rather than a single point-in-time approval embedded in the procedure document itself. |

## Current-main capabilities preserved (not replaced)

Everything listed in the Implementation Contract as the current baseline is
untouched by this PR:

- `backend/backup_assurance.py`, `backend/backup_assurance_ddl.py`
- `backend/routers/backup_ops.py`, `backend/schemas_backup.py`
- `backend/scripts/validate_restore.py`
- the `backup_assurance_events` migration and append-only event model
- RPO/RTO evaluation (`evaluate_backup_freshness`)
- provider reachability evaluation (`evaluate_provider_reachability`)
- restore-target safety guard (`_PRODUCTION_MARKERS`, `--allow-production-target`)
- schema/Alembic validation and tenant-isolation validation in `validate_restore.py`
- existing backup/restore contract tests

## A gap this audit surfaced that neither branch solved

`backend/backup_assurance.evaluate_provider_reachability` treats a reachability
assertion as stale after `PROVIDER_REACHABILITY_MAX_AGE_MINUTES = 15`. Nothing
in the repository — on either branch — refreshes
`UKIP_BACKUP_PROVIDER_REACHABLE` / `UKIP_BACKUP_PROVIDER_REACHABLE_AT` on that
cadence. A daily GitHub Actions run structurally cannot keep a 15-minute-fresh
signal current, so `.github/workflows/backup-freshness.yml` deliberately does
**not** attempt to assert reachability itself — doing so would either leave
the workflow permanently red for an unrelated reason, or turn it into a second
authority for a signal that is supposed to come from something colocated with
production. This is recorded as a residual risk, not as an
`ARCHITECTURE DECISION REQUIRED`, because it changes no RPO/RTO commitment,
backup scope, recovery authority, or supported topology — it is an
unimplemented operational mechanism, not a disputed one. See the PR
description for the recommended follow-up.
