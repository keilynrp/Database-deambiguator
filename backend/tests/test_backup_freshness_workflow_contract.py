"""Governance checks for the ER-BCP-001 backup-freshness workflow and its
accompanying reconciliation/evidence documents (issue #320, Phase A).

These are plain text/structure contracts, matching the style already used by
test_backup_configuration_contract.py and test_backup_runbook_contract.py —
no live network or provider access is involved.
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github" / "workflows" / "backup-freshness.yml"
RECONCILIATION = ROOT / "docs" / "operating" / "ER-BCP-001-HISTORICAL-RECONCILIATION.md"
READINESS_DOSSIER = (
    ROOT
    / "docs"
    / "operating"
    / "templates"
    / "ER-BCP-001_READINESS_EVIDENCE_TEMPLATE.md"
)
RUNBOOK = ROOT / "docs" / "operating" / "BACKUP_RESTORE_RUNBOOK.md"

REQUIRED_SECRETS = {
    "S3_BACKUP_ENDPOINT",
    "S3_BACKUP_BUCKET",
    "S3_BACKUP_RO_ACCESS_KEY_ID",
    "S3_BACKUP_RO_SECRET_ACCESS_KEY",
    "UKIP_BACKUP_EVIDENCE_API_BASE_URL",
    "UKIP_BACKUP_EVIDENCE_API_KEY",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_workflow_is_valid_yaml_with_expected_triggers_and_permissions():
    doc = yaml.safe_load(_read(WORKFLOW))

    assert "schedule" in doc[True] or "schedule" in doc.get("on", {})
    on = doc.get("on") or doc.get(True)
    assert "schedule" in on
    assert "workflow_dispatch" in on
    assert doc["permissions"] == {"contents": "read"}


def test_workflow_only_references_the_expected_secrets():
    text = _read(WORKFLOW)

    for secret in REQUIRED_SECRETS:
        assert f"secrets.{secret}" in text

    referenced = set(re.findall(r"secrets\.([A-Z0-9_]+)", text))
    assert referenced == REQUIRED_SECRETS


def test_workflow_does_not_reimplement_staleness_math():
    text = _read(WORKFLOW)

    # The historical workflow decided pass/fail with its own bash-computed
    # age threshold. The reconciled workflow must defer to the existing
    # backend.backup_assurance evaluator instead of recomputing it.
    assert "MAX_AGE_HOURS" not in text
    assert "/ops/backups/events" in text
    assert "/ops/backups/status" in text


def test_workflow_never_asserts_reachability_directly():
    text = _read(WORKFLOW)

    assert "UKIP_BACKUP_PROVIDER_REACHABLE" not in text


def test_workflow_guards_on_missing_secrets_before_using_them():
    text = _read(WORKFLOW)
    lines = text.splitlines()

    guard_index = next(
        i
        for i, line in enumerate(lines)
        if "missing repository secrets" in line.lower()
    )
    observe_index = next(
        i for i, line in enumerate(lines) if "aws s3api list-objects-v2" in line
    )
    assert guard_index < observe_index


def test_reconciliation_doc_states_the_audited_numbers():
    text = _read(RECONCILIATION)
    normalized = " ".join(text.split())

    assert "282 commits behind" in normalized
    assert "2 commits unique to it" in normalized
    assert ".github/workflows/backup-freshness.yml" in text
    assert "docs/operating/BACKUP_RESTORE_RUNBOOK.md" in text
    assert "ARCHITECTURE_DECISION_REQUIRED: none" in text


def test_reconciliation_doc_covers_all_three_dispositions():
    lowered = _read(RECONCILIATION).lower()

    assert "still missing from main" in lowered
    assert "superseded" in lowered
    assert "rejected as obsolete or unsafe" in lowered


def test_readiness_dossier_covers_required_evidence_fields():
    text = _read(READINESS_DOSSIER).lower()

    required_fields = (
        "provider configuration evidence",
        "backup cycle #1",
        "backup cycle #2",
        "isolated restore drill",
        "achieved rpo",
        "achieved rto",
        "alembic revision",
        "tenant-isolation",
        "integrity/data-usability",
        "provider reachability",
        "operator",
        "evidence reference",
        "residual risk",
        "durable-state review",
        "ukip_static_data",
    )
    for field in required_fields:
        assert field in text, f"missing required evidence field: {field!r}"


def test_readiness_dossier_does_not_change_control_maturity():
    text = _read(READINESS_DOSSIER)

    assert "Maturity before this dossier: `specified`" in text


def test_runbook_documents_the_automated_observation_workflow():
    text = _read(RUNBOOK)

    assert "backup-freshness.yml" in text
    assert "ER-BCP-001-HISTORICAL-RECONCILIATION.md" in text
    assert "ER-BCP-001_READINESS_EVIDENCE_TEMPLATE.md" in text
    assert "Operator Actions Pending" in text


def test_control_register_and_enterprise_controls_are_untouched_by_phase_a():
    # Phase A must not change ER-BCP-001 maturity. Anchoring on the exact
    # current maturity string keeps this test meaningful (it would fail if
    # someone bumped maturity without updating this guard deliberately).
    register = _read(ROOT / "docs" / "product" / "ENTERPRISE_CONTROL_REGISTER.md")
    controls = _read(ROOT / "backend" / "enterprise_controls.py")

    assert (
        "| ER-BCP-001 | PostgreSQL and required state can be restored within measured objectives | P0 | specified | auditable |"
        in register
    )
    assert '"ER-BCP-001",' in controls
    assert '"specified",\n        "auditable",' in controls
