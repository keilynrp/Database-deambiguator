# ER-BCP-001 Provider Readiness Evidence Dossier

Use one copy of this dossier for the full evidence gate described in issue
#320: provider configuration, the first two backup cycles, and the first
isolated restore drill. It is the cover sheet for the gate — it does not
replace the per-event
[backup and restore evidence template](BACKUP_RESTORE_EVIDENCE_TEMPLATE.md),
which is still filled in once for each backup cycle and once for the drill,
and linked from here.

Do not include passwords, tokens, credentials, database URLs, connection
strings, bucket keys, or backup contents anywhere in this dossier.

## Identification

- Control ID: `ER-BCP-001`
- Dossier date:
- Environment: production
- Operator (identity that performed or observed each step below):
- Approver:
- Evidence retention target: 12 months from dossier date

## 1. Provider configuration evidence

Record what was actually configured, not what was planned. Each row should
point at a read-only, non-secret verification where one is possible.

| Item | Configured value / description | Verification reference |
| --- | --- | --- |
| Backup destination type | | |
| Storage region | | |
| Encryption at rest | | |
| Encryption in transit (TLS) | | |
| Bucket versioning enabled | | |
| Object lock / immutability | | |
| Backup schedule | | |
| Retention policy (daily/weekly/monthly) | | |
| Backup identity permissions (write scope) | | |
| CI read-only identity permissions | | |
| `ukip_static_data` backup configured | | |

## 2. Backup cycle #1

- Cycle date/time (UTC):
- Filled-in per-event template: link to
  [BACKUP_RESTORE_EVIDENCE_TEMPLATE.md](BACKUP_RESTORE_EVIDENCE_TEMPLATE.md)
  instance for this cycle
- `backup_assurance_events` event ID:
- `GET /ops/backups/status` result at time of observation:
- `GET /ops/checks` `backup_freshness` result at time of observation:
- CI workflow run ID (if `backup-freshness.yml` recorded this cycle):
- Achieved RPO for this cycle (age of the recovery point when observed):

## 3. Backup cycle #2

Must be a **distinct** cycle in time from cycle #1, independently evidenced.

- Cycle date/time (UTC):
- Filled-in per-event template: link to
  [BACKUP_RESTORE_EVIDENCE_TEMPLATE.md](BACKUP_RESTORE_EVIDENCE_TEMPLATE.md)
  instance for this cycle
- `backup_assurance_events` event ID:
- `GET /ops/backups/status` result at time of observation:
- `GET /ops/checks` `backup_freshness` result at time of observation:
- CI workflow run ID (if `backup-freshness.yml` recorded this cycle):
- Achieved RPO for this cycle (age of the recovery point when observed):

## 4. First isolated restore drill

- Filled-in per-event template: link to
  [BACKUP_RESTORE_EVIDENCE_TEMPLATE.md](BACKUP_RESTORE_EVIDENCE_TEMPLATE.md)
  instance for the drill
- Isolated target identity (host/environment/database) and proof of
  non-production status:
- Restore-target safety check result
  (`backend/scripts/validate_restore.py`, no `--allow-production-target`):
- Backup completed timestamp used as the recovery point:
- Restore decision/start timestamp:
- Restore completed/usable timestamp:
- Achieved RPO (recovery-point age at drill start) vs objective (≤ 24h):
- Achieved RTO (elapsed wall-clock time) vs objective (≤ 4h):
- Expected vs actual Alembic revision:
- Required-table checks:
- Tenant-isolation validation result:
- Integrity/data-usability (decrypt probe or equivalent) result:
- Validator report path and checksum:
- Confirmation no production target was mutated:

## 5. Provider reachability / freshness

- `UKIP_BACKUP_PROVIDER_REACHABLE` / `_AT` source and observed freshness at
  dossier time:
- Known gap (see
  [ER-BCP-001-HISTORICAL-RECONCILIATION.md](../ER-BCP-001-HISTORICAL-RECONCILIATION.md)):
  the 15-minute reachability freshness window has no colocated refresher yet.
  Record the actual mechanism in place, if any, or record this as an open
  residual risk below.

## 6. Durable-state review

- `ukip_static_data` volume contents inspected: YES / NO
- Non-regenerable state found outside PostgreSQL: YES / NO
- Finding:
- If non-regenerable state was found: backup boundary was **not** silently
  expanded; follow-up issue or architecture decision opened: YES / NO / link
- Other non-database durable state considered (ChromaDB, DuckDB, Redis) and
  confirmed reconstructible: YES / NO

## 7. Residual risks

- None recorded / describe:

## 8. Maturity statement

- Maturity before this dossier: `specified`
- Maturity this dossier supports (owner's explicit conclusion, not assumed
  from implementation or configuration alone):
- If maturity changes, both
  `docs/product/ENTERPRISE_CONTROL_REGISTER.md` and
  `backend/enterprise_controls.py` were updated in the same change: YES / NO

## Approval

- Final result: Passed / Passed with risk / Failed
- Operator decision and timestamp:
- Approver decision and timestamp:
- Follow-up evidence reference:
