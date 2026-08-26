from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.enterprise_controls import ENTERPRISE_CONTROLS  # noqa: E402

EVIDENCE_DIR = ROOT / "docs/product/evidence"
RC_FILENAME_RE = re.compile(r"^RC-\d{4}-\d{2}-\d{2}-\d{2}\.md$")
VALID_DISPOSITIONS = {
    "EVIDENCED",
    "PARTIALLY EVIDENCED",
    "NOT EVIDENCED",
    "OPERATOR ACTION REQUIRED",
    "EXTERNAL ASSURANCE REQUIRED",
}
REQUIRED_SECTIONS = (
    "## 1. Release candidate identity",
    "## 2. Environment / topology evidenced",
    "## 3. Observation window",
    "## 4. Tenant scope",
    "## 5. CI / security / runtime evidence references",
    "## 6. P0/P1 control reconciliation",
    "## 7. Maturity changes proposed",
    "## 8. Residual risks and limitations",
    "## 9. Owner attestation",
    "## 10. Evidence invalidation rules",
    "## 11. Reproducible next-RC procedure",
)
SHA_RE = re.compile(r"`[0-9a-f]{40}`")


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def rc_files() -> list[Path]:
    if not EVIDENCE_DIR.is_dir():
        return []
    return sorted(p for p in EVIDENCE_DIR.glob("*.md") if p.name != "README.md")


def validate_file(path: Path) -> list[str]:
    errors: list[str] = []
    if not RC_FILENAME_RE.match(path.name):
        errors.append(f"{path.name}: filename does not match RC-YYYY-MM-DD-NN.md")

    content = read(path)

    for section in REQUIRED_SECTIONS:
        if section not in content:
            errors.append(f"{path.name}: missing required section '{section}'")

    if not SHA_RE.search(content):
        errors.append(f"{path.name}: no 40-character commit SHA found (backtick-quoted)")

    expected_ids = {control.control_id for control in ENTERPRISE_CONTROLS}
    seen_ids: dict[str, int] = {}
    disposition_by_id: dict[str, str] = {}
    for line in content.splitlines():
        if not line.startswith("| `ER-"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) < 3:
            continue
        control_id = cells[0].strip("`")
        seen_ids[control_id] = seen_ids.get(control_id, 0) + 1
        disposition_by_id[control_id] = cells[2]

    missing = expected_ids - seen_ids.keys()
    unknown = seen_ids.keys() - expected_ids
    duplicated = {cid for cid, count in seen_ids.items() if count > 1}

    for control_id in sorted(missing):
        errors.append(f"{path.name}: control {control_id} missing from reconciliation table")
    for control_id in sorted(unknown):
        errors.append(f"{path.name}: unknown control {control_id} in reconciliation table")
    for control_id in sorted(duplicated):
        errors.append(f"{path.name}: control {control_id} listed more than once")

    for control_id, disposition in disposition_by_id.items():
        if disposition not in VALID_DISPOSITIONS:
            errors.append(
                f"{path.name}: control {control_id} has invalid disposition '{disposition}'"
            )

    if "## 7. Maturity changes proposed" in content:
        section = content.split("## 7. Maturity changes proposed", 1)[1]
        section = section.split("## 8.", 1)[0]
        if "**None.**" not in section and "current_maturity" not in section:
            errors.append(
                f"{path.name}: section 7 must either say 'None.' explicitly or justify "
                "a specific current_maturity change"
            )

    return errors


def validate() -> list[str]:
    errors: list[str] = []
    files = rc_files()
    if not files:
        errors.append("docs/product/evidence/ has no RC-*.md evidence file")
        return errors
    for path in files:
        errors.extend(validate_file(path))
    return errors


def main() -> int:
    errors = validate()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("Release evidence index is structurally sound.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
