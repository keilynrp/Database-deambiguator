#!/usr/bin/env python3
"""Deterministic repo-wide lint-debt ratchet for Ruff and ESLint (issue #294).

Converts the previously non-blocking repo-wide Ruff and ESLint jobs into a
monotonic debt contract: CI fails if either tool's total violation count goes
above the committed baseline, and — deliberately more strict than a plain
ceiling — also fails if it drops below the baseline, so a real cleanup cannot
land without ratcheting the stored budget down in the same PR (issue #294,
acceptance criteria 5/6). This is not a lint-cleanup tool; it only measures
and compares.

Commands
--------
  measure
      Run the authoritative Ruff and ESLint measurements fresh and print the
      counts as JSON. Used to author/update .github/quality/lint_baseline.json
      by hand — this command never reads or writes the baseline file itself.

  check
      Run the same measurements and compare them against the committed
      baseline. Exit 0 only if every governed metric matches exactly. Exit 1
      on any regression, any stale (over-committed) baseline entry, a
      missing/malformed baseline, or a lint tool that could not be measured
      (wrong exit code, non-JSON output, or a JSON payload that is not the
      expected list shape). None of those failure modes are ever interpreted
      as zero debt — see LintToolError / BaselineError below.

Fail-closed by construction
----------------------------
Every path that cannot positively confirm "measured N violations" raises
before any comparison happens, and `check` exits 1. There is no silent
fallback to 0.

Local usage (matches the CI step exactly)
------------------------------------------
  pip install ruff==0.16.4          # pinned — see RUFF_VERSION_PIN below
  (cd frontend && npm ci)           # eslint version is locked by package-lock.json
  python scripts/lint_debt_ratchet.py check
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_BASELINE_PATH = REPO_ROOT / ".github" / "quality" / "lint_baseline.json"
SCHEMA_VERSION = 1

# Ruff is installed unpinned elsewhere in CI (the pre-existing non-blocking
# debt-radar job); a ratchet compared against a moving tool version is not
# deterministic, since Ruff's own default rule set changes across releases.
# This pin is the version this baseline was measured with — bump it (and the
# baseline counts) together, deliberately, when Ruff is intentionally
# upgraded. See docs/operating/LINT_DEBT_RATCHET.md.
RUFF_VERSION_PIN = "0.16.4"

RUFF_TARGET = "backend/"
RUFF_COMMAND = ["ruff", "check", RUFF_TARGET, "--output-format=json"]
# eslint's own version is already deterministic: `npm ci` installs exactly
# what frontend/package-lock.json locks (10.8.1 as of this baseline).
ESLINT_COMMAND = ["npx", "--yes", "eslint", "--format", "json"]

Runner = Callable[..., "subprocess.CompletedProcess[str]"]


class LintToolError(RuntimeError):
    """A lint tool could not be measured — callers must fail closed, never 0."""


class BaselineError(RuntimeError):
    """The committed baseline is missing or malformed — callers must fail closed."""


def run_ruff(runner: Runner = subprocess.run) -> int:
    """Return the total Ruff violation count for RUFF_TARGET, or raise LintToolError."""
    try:
        proc = runner(RUFF_COMMAND, cwd=REPO_ROOT, capture_output=True, text=True)
    except OSError as exc:
        raise LintToolError(f"ruff could not be executed: {exc}") from exc
    # Ruff exits 1 when it finds violations — that is a successful measurement,
    # not a failure. Anything else (2 = usage error, etc.) means the count
    # below cannot be trusted.
    if proc.returncode not in (0, 1):
        raise LintToolError(
            f"ruff exited {proc.returncode} (only 0/1 are valid measurement "
            f"outcomes): {proc.stderr.strip()}"
        )
    try:
        violations = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise LintToolError(f"ruff did not emit valid JSON: {exc}") from exc
    if not isinstance(violations, list):
        raise LintToolError(
            "ruff JSON output was not a list — refusing to trust it as zero debt"
        )
    return len(violations)


def run_eslint(runner: Runner = subprocess.run) -> tuple[int, int]:
    """Return (error_count, warning_count) for the frontend default project scope."""
    try:
        proc = runner(
            ESLINT_COMMAND, cwd=REPO_ROOT / "frontend", capture_output=True, text=True
        )
    except OSError as exc:
        raise LintToolError(f"eslint could not be executed: {exc}") from exc
    # ESLint exits 1 when lint problems are found — a successful measurement.
    if proc.returncode not in (0, 1):
        raise LintToolError(
            f"eslint exited {proc.returncode} (only 0/1 are valid measurement "
            f"outcomes): {proc.stderr.strip()}"
        )
    try:
        results = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise LintToolError(f"eslint did not emit valid JSON: {exc}") from exc
    if not isinstance(results, list):
        raise LintToolError(
            "eslint JSON output was not a list — refusing to trust it as zero debt"
        )
    error_count = sum(int(r.get("errorCount", 0)) for r in results)
    warning_count = sum(int(r.get("warningCount", 0)) for r in results)
    return error_count, warning_count


def load_baseline(path: Path = DEFAULT_BASELINE_PATH) -> dict:
    if not path.exists():
        raise BaselineError(f"baseline file missing: {path}")
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        raise BaselineError(f"baseline file is not valid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise BaselineError("baseline file must contain a JSON object")
    if data.get("schema_version") != SCHEMA_VERSION:
        raise BaselineError(
            f"unsupported baseline schema_version: {data.get('schema_version')!r} "
            f"(expected {SCHEMA_VERSION})"
        )
    try:
        ruff_count = data["ruff"]["violation_count"]
        eslint_errors = data["eslint"]["error_count"]
        eslint_warnings = data["eslint"]["warning_count"]
    except (KeyError, TypeError) as exc:
        raise BaselineError(f"baseline missing a required field: {exc}") from exc
    for name, value in (
        ("ruff.violation_count", ruff_count),
        ("eslint.error_count", eslint_errors),
        ("eslint.warning_count", eslint_warnings),
    ):
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            raise BaselineError(f"baseline field {name} must be a non-negative integer, got {value!r}")
    return data


def compare(current: dict, baseline: dict) -> list[str]:
    """Return human-readable problem descriptions; an empty list means PASS."""
    problems: list[str] = []
    checks = [
        ("ruff.violation_count", current["ruff_count"], baseline["ruff"]["violation_count"]),
        ("eslint.error_count", current["eslint_errors"], baseline["eslint"]["error_count"]),
        ("eslint.warning_count", current["eslint_warnings"], baseline["eslint"]["warning_count"]),
    ]
    for name, cur, base in checks:
        if cur > base:
            problems.append(
                f"REGRESSION {name}: current={cur} > baseline={base} (delta +{cur - base}) "
                f"— new lint debt was introduced"
            )
        elif cur < base:
            problems.append(
                f"STALE {name}: current={cur} < baseline={base} (delta {cur - base}) "
                f"— ratchet .github/quality/lint_baseline.json down in this PR"
            )
    return problems


def cmd_measure(args: argparse.Namespace) -> int:
    ruff_count = run_ruff()
    eslint_errors, eslint_warnings = run_eslint()
    print(
        json.dumps(
            {
                "ruff": {"violation_count": ruff_count},
                "eslint": {"error_count": eslint_errors, "warning_count": eslint_warnings},
            },
            indent=2,
        )
    )
    return 0


def cmd_check(
    args: argparse.Namespace,
    ruff_runner: Runner = subprocess.run,
    eslint_runner: Runner = subprocess.run,
) -> int:
    baseline_path = Path(args.baseline)
    try:
        baseline = load_baseline(baseline_path)
    except BaselineError as exc:
        print(f"FAIL CLOSED — baseline error: {exc}", file=sys.stderr)
        return 1

    try:
        ruff_count = run_ruff(ruff_runner)
        eslint_errors, eslint_warnings = run_eslint(eslint_runner)
    except LintToolError as exc:
        print(f"FAIL CLOSED — lint tool error: {exc}", file=sys.stderr)
        return 1

    current = {
        "ruff_count": ruff_count,
        "eslint_errors": eslint_errors,
        "eslint_warnings": eslint_warnings,
    }
    problems = compare(current, baseline)

    print(
        json.dumps(
            {
                "current": current,
                "baseline": {
                    "ruff_count": baseline["ruff"]["violation_count"],
                    "eslint_errors": baseline["eslint"]["error_count"],
                    "eslint_warnings": baseline["eslint"]["warning_count"],
                },
                "problems": problems,
            },
            indent=2,
        )
    )

    if problems:
        print("FAIL — lint debt ratchet violated:", file=sys.stderr)
        for problem in problems:
            print(f"  {problem}", file=sys.stderr)
        return 1

    print("PASS — measured debt matches the committed baseline exactly.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    subparsers = parser.add_subparsers(dest="command", required=True)

    measure_parser = subparsers.add_parser("measure", help="Print fresh Ruff/ESLint counts as JSON.")
    measure_parser.set_defaults(func=cmd_measure)

    check_parser = subparsers.add_parser("check", help="Compare fresh counts against the committed baseline.")
    check_parser.add_argument(
        "--baseline",
        default=str(DEFAULT_BASELINE_PATH),
        help="Path to the baseline JSON file (default: .github/quality/lint_baseline.json).",
    )
    check_parser.set_defaults(func=cmd_check)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
