import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_DIR = ROOT / "docs/product/evidence"

sys.path.insert(0, str(ROOT / "scripts"))
import lint_release_evidence as lint


def test_evidence_directory_is_documented_in_governance():
    governance = (ROOT / "docs/DOCUMENTATION_GOVERNANCE.md").read_text(encoding="utf-8")
    product_index = (ROOT / "docs/product/README.md").read_text(encoding="utf-8")
    assert "docs/product/evidence/" in governance
    assert "docs/product/evidence/" in product_index


def test_at_least_one_release_candidate_is_evidenced():
    rc_files = sorted(p for p in EVIDENCE_DIR.glob("RC-*.md"))
    assert rc_files, "expected at least one RC-*.md release evidence file"


def test_every_p0_p1_control_appears_exactly_once_per_rc_file():
    """Each RC's rows must match its own persisted snapshot, not today's manifest.

    The two coincide for the one RC file in the repo today, but the check is
    written against the persisted snapshot (the actual validation authority)
    rather than the live manifest, so it keeps meaning the right thing once a
    second, older RC file exists.
    """
    for path in sorted(EVIDENCE_DIR.glob("RC-*.md")):
        content = path.read_text(encoding="utf-8")
        persisted = lint.parse_control_set_snapshot(content)
        assert persisted is not None, f"{path.name}: missing persisted control-set snapshot"
        expected_ids = set(persisted)
        seen: dict[str, int] = {}
        for line in content.splitlines():
            if line.startswith("| `ER-"):
                control_id = line.strip("|").split("|")[0].strip().strip("`")
                seen[control_id] = seen.get(control_id, 0) + 1
        assert seen.keys() == expected_ids, f"{path.name}: control coverage mismatch"
        assert all(count == 1 for count in seen.values()), f"{path.name}: duplicate control row"


def test_newest_rc_persisted_snapshot_matches_current_manifest():
    current_ids = lint.current_p0_p1_ids()
    newest = max(EVIDENCE_DIR.glob("RC-*.md"))
    persisted = lint.parse_control_set_snapshot(newest.read_text(encoding="utf-8"))
    assert set(persisted) == current_ids


def test_release_evidence_lint_passes_repository_state():
    result = subprocess.run(
        [sys.executable, "scripts/lint_release_evidence.py"],
        cwd=ROOT, capture_output=True, text=True, check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr


# ── Persisted control-set snapshot: isolated fixture tests ─────────────────
#
# These use a temp evidence directory and an injected fake manifest (via
# monkeypatch on the lint_release_evidence module globals) so they never
# touch the real docs/product/evidence/ files or backend/enterprise_controls.py,
# and never depend on issue #315's eleven real control IDs.

SHA = "a" * 40
VALID_DISPOSITION = "NOT EVIDENCED"


@dataclass(frozen=True)
class FakeControl:
    control_id: str
    priority: str


def _rc_body(rc_id: str, control_ids: list[str], row_ids: list[str] | None = None) -> str:
    row_ids = control_ids if row_ids is None else row_ids
    snapshot_block = "\n".join(control_ids)
    rows = "\n".join(f"| `{cid}` | - | {VALID_DISPOSITION} | - | - | - | - |" for cid in row_ids)
    return f"""# {rc_id} — Release Evidence Index

## 1. Release candidate identity

| Field | Value |
| --- | --- |
| Release candidate ID | `{rc_id}` |
| Exact commit SHA | `{SHA}` |

### 1.1 P0/P1 control-set snapshot (persisted, contemporaneous)

```control-set-snapshot
{snapshot_block}
```

## 2. Environment / topology evidenced

n/a

## 3. Observation window

n/a

## 4. Tenant scope

n/a

## 5. CI / security / runtime evidence references

n/a

## 6. P0/P1 control reconciliation

| Control | Current -> Target | Disposition (this RC) | Evidence references | Missing evidence / next gate | Accountable / Implementation / Operational | Residual risk |
| --- | --- | --- | --- | --- | --- | --- |
{rows}

## 7. Maturity changes proposed

**None.**

## 8. Residual risks and limitations

n/a

## 9. Owner attestation

n/a

## 10. Evidence invalidation rules

n/a

## 11. Reproducible next-RC procedure

n/a
"""


@pytest.fixture
def fake_evidence_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(lint, "EVIDENCE_DIR", tmp_path)
    return tmp_path


def test_historical_rc_remains_valid_after_simulated_later_control_set_change(
    fake_evidence_dir, monkeypatch
):
    """A settled historical RC must not break when the manifest later gains a control."""
    historical = fake_evidence_dir / "RC-2026-01-01-01.md"
    historical.write_text(_rc_body("RC-2026-01-01-01", ["ER-A", "ER-B"]), encoding="utf-8")

    newest = fake_evidence_dir / "RC-2026-02-01-01.md"
    newest.write_text(
        _rc_body("RC-2026-02-01-01", ["ER-A", "ER-B", "ER-C"]), encoding="utf-8"
    )

    # Simulate the manifest as it stood when `historical` was authored: no ER-C yet.
    monkeypatch.setattr(
        lint,
        "ENTERPRISE_CONTROLS",
        (FakeControl("ER-A", "P0"), FakeControl("ER-B", "P1")),
    )
    errors_before = lint.validate()
    assert not any("RC-2026-01-01-01" in e for e in errors_before)

    # Now simulate a control being added later, after `historical` was settled.
    monkeypatch.setattr(
        lint,
        "ENTERPRISE_CONTROLS",
        (FakeControl("ER-A", "P0"), FakeControl("ER-B", "P1"), FakeControl("ER-C", "P1")),
    )
    errors_after = lint.validate()
    historical_errors = [e for e in errors_after if "RC-2026-01-01-01" in e]
    assert historical_errors == [], (
        "historical RC must validate against its own persisted snapshot, "
        f"not the current manifest: {historical_errors}"
    )


def test_newest_rc_fails_when_persisted_snapshot_diverges_from_current_manifest(
    fake_evidence_dir, monkeypatch
):
    """The newest RC must additionally match today's manifest, unlike historical RCs."""
    newest = fake_evidence_dir / "RC-2026-02-01-01.md"
    newest.write_text(_rc_body("RC-2026-02-01-01", ["ER-A", "ER-B"]), encoding="utf-8")

    monkeypatch.setattr(
        lint,
        "ENTERPRISE_CONTROLS",
        (FakeControl("ER-A", "P0"), FakeControl("ER-B", "P1"), FakeControl("ER-C", "P1")),
    )
    errors = lint.validate()
    assert any("ER-C" in e and "RC-2026-02-01-01" in e for e in errors), errors


def test_reconciliation_rows_match_persisted_snapshot_exactly_once(
    fake_evidence_dir, monkeypatch
):
    monkeypatch.setattr(
        lint, "ENTERPRISE_CONTROLS", (FakeControl("ER-A", "P0"), FakeControl("ER-B", "P1"))
    )

    missing_row = fake_evidence_dir / "RC-2026-01-01-01.md"
    missing_row.write_text(
        _rc_body("RC-2026-01-01-01", ["ER-A", "ER-B"], row_ids=["ER-A"]), encoding="utf-8"
    )
    errors = lint.validate()
    assert any(
        "ER-B" in e and "missing from reconciliation table" in e for e in errors
    ), errors
    missing_row.unlink()

    unknown_row = fake_evidence_dir / "RC-2026-01-01-02.md"
    unknown_row.write_text(
        _rc_body("RC-2026-01-01-02", ["ER-A", "ER-B"], row_ids=["ER-A", "ER-B", "ER-Z"]),
        encoding="utf-8",
    )
    errors = lint.validate()
    assert any("ER-Z" in e and "unknown control" in e for e in errors), errors
    unknown_row.unlink()

    duplicate_row = fake_evidence_dir / "RC-2026-01-01-03.md"
    duplicate_row.write_text(
        _rc_body("RC-2026-01-01-03", ["ER-A", "ER-B"], row_ids=["ER-A", "ER-A", "ER-B"]),
        encoding="utf-8",
    )
    errors = lint.validate()
    assert any(
        "ER-A" in e and "listed more than once" in e for e in errors
    ), errors
