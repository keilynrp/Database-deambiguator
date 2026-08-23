"""Sentinel/mutation tests for scripts/lint_backend_changed.py (issue #294).

git and ruff interaction are both injected (see the `*_runner` parameters on
scripts/lint_backend_changed.py), so these tests never invoke a real ruff
binary or depend on actual repository history — the same reasoning
test_lint_debt_ratchet.py and test_partition_guard.py use for their injected
runners.

The key sentinel required by the #294 Implementation Contract lives here:
`test_single_new_violation_blocks_independent_of_repo_wide_debt` proves one
newly introduced backend Ruff violation blocks this gate regardless of what
the repo-wide baseline ratchet would say, because this script never reads
the baseline at all.
"""
import json
import subprocess
import sys
from argparse import Namespace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "scripts"))
import lint_backend_changed as changed


def _proc(returncode: int, stdout: str = "", stderr: str = "") -> subprocess.CompletedProcess:
    return subprocess.CompletedProcess(args=["x"], returncode=returncode, stdout=stdout, stderr=stderr)


def _git_runner(files: list[str], returncode: int = 0):
    def runner(*args, **kwargs):
        return _proc(returncode, stdout="\n".join(files))

    return runner


def _ruff_runner(violations: list[dict], returncode: int = 1):
    def runner(*args, **kwargs):
        return _proc(returncode, stdout=json.dumps(violations))

    return runner


def _check_args() -> Namespace:
    return Namespace(base_sha="base-sha")


# ── No changed backend files: trivial pass, ruff never invoked ─────────────

def test_no_changed_backend_files_passes_trivially():
    calls = []

    def ruff_spy(*args, **kwargs):
        calls.append(args)
        return _proc(0, stdout="[]")

    rc = changed.cmd_check(
        _check_args(),
        git_runner=_git_runner(["frontend/app/page.tsx", "README.md"]),
        ruff_runner=ruff_spy,
    )
    assert rc == 0
    assert calls == []


def test_only_backend_py_files_are_selected_for_ruff():
    seen_files = []

    def ruff_spy(cmd, **kwargs):
        seen_files.extend(f for f in cmd if f.endswith(".py"))
        return _proc(0, stdout="[]")

    changed.cmd_check(
        _check_args(),
        git_runner=_git_runner(
            ["frontend/app/page.tsx", "backend/notes.txt", "backend/routers/foo.py", "backend/bar.py"]
        ),
        ruff_runner=ruff_spy,
    )
    assert seen_files == ["backend/routers/foo.py", "backend/bar.py"]


# ── Clean changed file passes ───────────────────────────────────────────────

def test_changed_backend_file_clean_passes():
    rc = changed.cmd_check(
        _check_args(),
        git_runner=_git_runner(["backend/routers/foo.py"]),
        ruff_runner=_ruff_runner([], returncode=0),
    )
    assert rc == 0


# ── The required sentinel: one new violation blocks, independent of baseline ─

def test_single_new_violation_blocks_independent_of_repo_wide_debt():
    """This script has no baseline parameter and no repo-wide count anywhere
    in its call graph — it cannot pass a single new violation through even if
    the caller believes repo-wide debt is comfortably under budget."""
    rc = changed.cmd_check(
        _check_args(),
        git_runner=_git_runner(["backend/routers/foo.py"]),
        ruff_runner=_ruff_runner(
            [{"filename": "backend/routers/foo.py", "code": "F401", "message": "unused import",
              "location": {"row": 3, "column": 1}}]
        ),
    )
    assert rc == 1


def test_multiple_changed_files_all_checked():
    rc = changed.cmd_check(
        _check_args(),
        git_runner=_git_runner(["backend/a.py", "backend/b.py"]),
        ruff_runner=_ruff_runner(
            [{"filename": "backend/b.py", "code": "E501", "message": "line too long",
              "location": {"row": 10, "column": 1}}]
        ),
    )
    assert rc == 1


# ── FAIL CLOSED ──────────────────────────────────────────────────────────

def test_git_diff_nonzero_exit_fails_closed():
    rc = changed.cmd_check(
        _check_args(),
        git_runner=_git_runner([], returncode=128),
        ruff_runner=_ruff_runner([], returncode=0),
    )
    assert rc == 1


def test_git_diff_oserror_fails_closed():
    def raising_runner(*args, **kwargs):
        raise OSError("git not found")

    rc = changed.cmd_check(_check_args(), git_runner=raising_runner, ruff_runner=_ruff_runner([], returncode=0))
    assert rc == 1


def test_ruff_oserror_fails_closed_not_zero():
    def raising_runner(*args, **kwargs):
        raise OSError("ruff not found")

    rc = changed.cmd_check(
        _check_args(), git_runner=_git_runner(["backend/foo.py"]), ruff_runner=raising_runner
    )
    assert rc == 1


def test_ruff_non_json_output_fails_closed_not_zero():
    def runner(*args, **kwargs):
        return _proc(0, stdout="not json")

    rc = changed.cmd_check(_check_args(), git_runner=_git_runner(["backend/foo.py"]), ruff_runner=runner)
    assert rc == 1


def test_ruff_unexpected_returncode_fails_closed():
    def runner(*args, **kwargs):
        return _proc(2, stdout="[]", stderr="internal error")

    rc = changed.cmd_check(_check_args(), git_runner=_git_runner(["backend/foo.py"]), ruff_runner=runner)
    assert rc == 1


def test_ruff_json_not_a_list_fails_closed():
    def runner(*args, **kwargs):
        return _proc(0, stdout=json.dumps({"unexpected": "shape"}))

    rc = changed.cmd_check(_check_args(), git_runner=_git_runner(["backend/foo.py"]), ruff_runner=runner)
    assert rc == 1
