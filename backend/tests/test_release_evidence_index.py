import subprocess
import sys
from pathlib import Path

from backend.enterprise_controls import ENTERPRISE_CONTROLS

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_DIR = ROOT / "docs/product/evidence"


def test_evidence_directory_is_documented_in_governance():
    governance = (ROOT / "docs/DOCUMENTATION_GOVERNANCE.md").read_text(encoding="utf-8")
    product_index = (ROOT / "docs/product/README.md").read_text(encoding="utf-8")
    assert "docs/product/evidence/" in governance
    assert "docs/product/evidence/" in product_index


def test_at_least_one_release_candidate_is_evidenced():
    rc_files = sorted(p for p in EVIDENCE_DIR.glob("RC-*.md"))
    assert rc_files, "expected at least one RC-*.md release evidence file"


def test_every_p0_p1_control_appears_exactly_once_per_rc_file():
    expected_ids = {control.control_id for control in ENTERPRISE_CONTROLS}
    for path in sorted(EVIDENCE_DIR.glob("RC-*.md")):
        content = path.read_text(encoding="utf-8")
        seen: dict[str, int] = {}
        for line in content.splitlines():
            if line.startswith("| `ER-"):
                control_id = line.strip("|").split("|")[0].strip().strip("`")
                seen[control_id] = seen.get(control_id, 0) + 1
        assert seen.keys() == expected_ids, f"{path.name}: control coverage mismatch"
        assert all(count == 1 for count in seen.values()), f"{path.name}: duplicate control row"


def test_release_evidence_lint_passes_repository_state():
    result = subprocess.run(
        [sys.executable, "scripts/lint_release_evidence.py"],
        cwd=ROOT, capture_output=True, text=True, check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
