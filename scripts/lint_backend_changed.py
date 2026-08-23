#!/usr/bin/env python3
"""Strict changed/new backend Python lint gate (issue #294).

The repo-wide Ruff ratchet (scripts/lint_debt_ratchet.py) only guarantees
"no worse than the committed baseline" — it would happily pass a PR that adds
five new violations to a touched file as long as some unrelated cleanup
elsewhere in the same PR removed five others. That is a loophole: legacy
debt may remain, but *newly introduced* debt must not be able to hide behind
it.

This script closes that loophole the same way frontend/'s existing changed-
file ESLint gate already does (.github/workflows/lint.yml, frontend-lint
job): every backend/**.py file touched by the diff must be fully Ruff-clean
— the whole file, not just the changed lines, matching the frontend gate's
existing whole-file strictness exactly. It does not consult the repo-wide
baseline at all, by construction: a single new violation in a touched file
blocks this gate regardless of what the repo-wide count is doing.

Usage
-----
  python scripts/lint_backend_changed.py check --base-sha <sha>

`<sha>` is resolved by the caller (see .github/workflows/lint.yml's
backend-lint-changed job, which mirrors frontend-lint's own BASE_SHA
resolution) so this script stays a pure, testable function of "which files
changed" rather than re-implementing PR/push event detection.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

Runner = Callable[..., "subprocess.CompletedProcess[str]"]


class ChangedFileLintError(RuntimeError):
    """Changed files or their lint result could not be determined — fail closed."""


def changed_backend_python_files(base_sha: str, runner: Runner = subprocess.run) -> list[str]:
    """Return backend/**.py files added/changed/renamed between base_sha and HEAD."""
    try:
        proc = runner(
            ["git", "diff", "--name-only", "--diff-filter=ACMR", base_sha, "HEAD"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
    except OSError as exc:
        raise ChangedFileLintError(f"git diff could not be executed: {exc}") from exc
    if proc.returncode != 0:
        raise ChangedFileLintError(f"git diff exited {proc.returncode}: {proc.stderr.strip()}")
    return [
        line.strip()
        for line in proc.stdout.splitlines()
        if line.strip().startswith("backend/") and line.strip().endswith(".py")
    ]


def run_ruff_on_files(files: list[str], runner: Runner = subprocess.run) -> list[dict]:
    """Return the list of Ruff violation objects found in `files`, or raise on tool failure."""
    if not files:
        return []
    try:
        proc = runner(
            ["ruff", "check", *files, "--output-format=json"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
    except OSError as exc:
        raise ChangedFileLintError(f"ruff could not be executed: {exc}") from exc
    if proc.returncode not in (0, 1):
        raise ChangedFileLintError(
            f"ruff exited {proc.returncode} (only 0/1 are valid outcomes): {proc.stderr.strip()}"
        )
    try:
        violations = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise ChangedFileLintError(f"ruff did not emit valid JSON: {exc}") from exc
    if not isinstance(violations, list):
        raise ChangedFileLintError(
            "ruff JSON output was not a list — refusing to trust it as zero violations"
        )
    return violations


def cmd_check(
    args: argparse.Namespace,
    git_runner: Runner = subprocess.run,
    ruff_runner: Runner = subprocess.run,
) -> int:
    try:
        files = changed_backend_python_files(args.base_sha, git_runner)
    except ChangedFileLintError as exc:
        print(f"FAIL CLOSED — {exc}", file=sys.stderr)
        return 1

    if not files:
        print("No changed backend/**.py files; skipping blocking Ruff run.")
        return 0

    try:
        violations = run_ruff_on_files(files, ruff_runner)
    except ChangedFileLintError as exc:
        print(f"FAIL CLOSED — {exc}", file=sys.stderr)
        return 1

    if violations:
        print(
            f"FAIL — {len(violations)} Ruff violation(s) in {len(files)} changed backend "
            f"file(s):",
            file=sys.stderr,
        )
        for v in violations:
            location = v.get("location") or {}
            print(
                f"  {v.get('filename')}:{location.get('row')}:{location.get('column')} "
                f"{v.get('code')} {v.get('message')}",
                file=sys.stderr,
            )
        return 1

    print(f"PASS — {len(files)} changed backend file(s), 0 Ruff violations.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    subparsers = parser.add_subparsers(dest="command", required=True)

    check_parser = subparsers.add_parser("check", help="Fail if any changed backend file has a Ruff violation.")
    check_parser.add_argument("--base-sha", required=True, help="Diff base ref/SHA to compare HEAD against.")
    check_parser.set_defaults(func=cmd_check)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
