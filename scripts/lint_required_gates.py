from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS_DIR = ROOT / ".github/workflows"

# Issue #317 / ER-SDLC-001: GitHub rulesets reject a "workflows" rule that
# pins individual job contexts (HTTP 422). Each authoritative workflow below
# instead exposes exactly one stable aggregation job that `needs` every
# blocking job in that file, so `required_status_checks` can target five
# fixed context names instead of every current job/matrix leg.
GATES = {
    "test.yml": "backend-required-gate",
    "lint.yml": "lint-required-gate",
    "security.yml": "security-required-gate",
    "codeql.yml": "codeql-required-gate",
    "docker.yml": "docker-required-gate",
}

JOB_RE = re.compile(r"^  ([A-Za-z0-9_-]+):\s*$")
IF_RE = re.compile(r"^    if:\s*(.*?)\s*$")
NEEDS_RE = re.compile(r"^    needs:\s*\[(.*)\]\s*$")
BLOCK_SCALAR_HEADS = {"", ">-", ">", ">+", "|-", "|", "|+"}


def parse_workflow(path: Path) -> tuple[list[str], dict[str, dict[str, object]]]:
    """Return (job order, {job_id: {"if": str | None, "needs": list[str] | None}})."""
    lines = path.read_text(encoding="utf-8").splitlines()
    jobs: dict[str, dict[str, object]] = {}
    order: list[str] = []
    current: str | None = None
    in_jobs = False
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        if line.startswith("jobs:"):
            in_jobs = True
            i += 1
            continue
        if not in_jobs:
            i += 1
            continue

        job_match = JOB_RE.match(line)
        if job_match:
            current = job_match.group(1)
            order.append(current)
            jobs[current] = {"if": None, "needs": None}
            i += 1
            continue

        if current is not None:
            if_match = IF_RE.match(line)
            if if_match:
                value = if_match.group(1).strip()
                if value in BLOCK_SCALAR_HEADS:
                    # Folded/literal block scalar: consume the indented
                    # continuation lines (e.g. docker.yml's `deploy` job).
                    parts: list[str] = []
                    i += 1
                    while i < n and (lines[i].startswith("      ") or not lines[i].strip()):
                        if lines[i].strip():
                            parts.append(lines[i].strip())
                        i += 1
                    jobs[current]["if"] = " ".join(parts)
                    continue
                jobs[current]["if"] = value
                i += 1
                continue

            needs_match = NEEDS_RE.match(line)
            if needs_match:
                jobs[current]["needs"] = [
                    part.strip() for part in needs_match.group(1).split(",") if part.strip()
                ]
                i += 1
                continue

        i += 1

    return order, jobs


def blocking_jobs(order: list[str], jobs: dict[str, dict[str, object]], gate_name: str) -> set[str]:
    """Every job that must gate a PR: all jobs except the gate itself and any
    job restricted to `refs/heads/main` (e.g. a main-only deploy step)."""
    result = set()
    for job_id in order:
        if job_id == gate_name:
            continue
        job_if = jobs[job_id]["if"] or ""
        if "refs/heads/main" in job_if:
            continue
        result.add(job_id)
    return result


def validate() -> list[str]:
    errors: list[str] = []
    for filename, gate_name in GATES.items():
        path = WORKFLOWS_DIR / filename
        if not path.is_file():
            errors.append(f"{filename}: workflow file not found")
            continue

        order, jobs = parse_workflow(path)
        if gate_name not in jobs:
            errors.append(f"{filename}: expected required-gate job '{gate_name}' not found")
            continue

        gate = jobs[gate_name]
        if gate["if"] != "always()":
            errors.append(
                f"{filename}: {gate_name} must run with 'if: always()', found {gate['if']!r}"
            )

        gate_needs = gate["needs"]
        if gate_needs is None:
            errors.append(f"{filename}: {gate_name} has no inline 'needs: [...]' list")
            gate_needs = []

        expected = blocking_jobs(order, jobs, gate_name)
        missing = expected - set(gate_needs)
        stale = set(gate_needs) - expected
        for job_id in sorted(missing):
            errors.append(
                f"{filename}: {gate_name} is missing blocking job '{job_id}' from its needs list"
            )
        for job_id in sorted(stale):
            errors.append(
                f"{filename}: {gate_name} needs unknown or non-blocking job '{job_id}'"
            )

    return errors


def main() -> int:
    errors = validate()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("Every required-gate aggregation job covers exactly its workflow's blocking jobs.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
