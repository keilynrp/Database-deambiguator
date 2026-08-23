"""Sentinel/mutation tests for scripts/lint_debt_ratchet.py (issue #294).

All lint-tool interaction is injected (see the `*_runner` parameters on
scripts/lint_debt_ratchet.py), so these tests never invoke a real ruff or
eslint binary — they run in every backend test shard without either tool
installed, the same reasoning backend/tests/test_partition_guard.py uses for
scripts/backend_test_partitions.py's injectable `runner`.
"""
import json
import subprocess
import sys
from argparse import Namespace
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "scripts"))
import lint_debt_ratchet as ratchet


def _proc(returncode: int, stdout: str = "", stderr: str = "") -> subprocess.CompletedProcess:
    return subprocess.CompletedProcess(args=["x"], returncode=returncode, stdout=stdout, stderr=stderr)


def _ruff_runner(count: int, returncode: int = 1):
    violations = [{"code": "F401", "message": "unused import"} for _ in range(count)]

    def runner(*args, **kwargs):
        return _proc(returncode if count else 0, stdout=json.dumps(violations))

    return runner


def _eslint_runner(error_count: int, warning_count: int, returncode: int = 1):
    payload = [{"errorCount": error_count, "warningCount": warning_count}]

    def runner(*args, **kwargs):
        return _proc(returncode, stdout=json.dumps(payload))

    return runner


def _write_baseline(tmp_path: Path, *, ruff: int, eslint_errors: int, eslint_warnings: int) -> Path:
    path = tmp_path / "lint_baseline.json"
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "ruff": {"violation_count": ruff},
                "eslint": {"error_count": eslint_errors, "warning_count": eslint_warnings},
            }
        )
    )
    return path


def _check_args(baseline_path: Path) -> Namespace:
    return Namespace(baseline=str(baseline_path))


# ── PASS: equal debt ────────────────────────────────────────────────────────

def test_equal_debt_passes(tmp_path):
    baseline = _write_baseline(tmp_path, ruff=10, eslint_errors=1, eslint_warnings=2)
    rc = ratchet.cmd_check(
        _check_args(baseline),
        ruff_runner=_ruff_runner(10),
        eslint_runner=_eslint_runner(1, 2),
    )
    assert rc == 0


# ── FAIL: regressions ───────────────────────────────────────────────────────

def test_ruff_plus_one_fails(tmp_path):
    baseline = _write_baseline(tmp_path, ruff=10, eslint_errors=0, eslint_warnings=0)
    rc = ratchet.cmd_check(
        _check_args(baseline),
        ruff_runner=_ruff_runner(11),
        eslint_runner=_eslint_runner(0, 0, returncode=0),
    )
    assert rc == 1


def test_eslint_errors_plus_one_fails(tmp_path):
    baseline = _write_baseline(tmp_path, ruff=10, eslint_errors=0, eslint_warnings=0)
    rc = ratchet.cmd_check(
        _check_args(baseline),
        ruff_runner=_ruff_runner(10),
        eslint_runner=_eslint_runner(1, 0),
    )
    assert rc == 1


def test_eslint_warnings_plus_one_fails(tmp_path):
    baseline = _write_baseline(tmp_path, ruff=10, eslint_errors=0, eslint_warnings=3)
    rc = ratchet.cmd_check(
        _check_args(baseline),
        ruff_runner=_ruff_runner(10),
        eslint_runner=_eslint_runner(0, 4),
    )
    assert rc == 1


def test_regression_message_identifies_offending_metric(tmp_path, capsys):
    baseline = _write_baseline(tmp_path, ruff=10, eslint_errors=0, eslint_warnings=0)
    ratchet.cmd_check(
        _check_args(baseline),
        ruff_runner=_ruff_runner(11),
        eslint_runner=_eslint_runner(0, 0, returncode=0),
    )
    err = capsys.readouterr().err
    assert "REGRESSION ruff.violation_count" in err


# ── FAIL: stale (over-committed) baseline ───────────────────────────────────

def test_stale_baseline_detected_and_fails(tmp_path, capsys):
    baseline = _write_baseline(tmp_path, ruff=10, eslint_errors=0, eslint_warnings=0)
    rc = ratchet.cmd_check(
        _check_args(baseline),
        ruff_runner=_ruff_runner(9),
        eslint_runner=_eslint_runner(0, 0, returncode=0),
    )
    assert rc == 1
    assert "STALE ruff.violation_count" in capsys.readouterr().err


# ── FAIL CLOSED: baseline problems ──────────────────────────────────────────

def test_missing_baseline_fails_closed(tmp_path):
    missing = tmp_path / "does-not-exist.json"
    rc = ratchet.cmd_check(_check_args(missing), ruff_runner=_ruff_runner(0), eslint_runner=_eslint_runner(0, 0))
    assert rc == 1


def test_malformed_json_baseline_fails_closed(tmp_path):
    path = tmp_path / "lint_baseline.json"
    path.write_text("{not valid json")
    rc = ratchet.cmd_check(_check_args(path), ruff_runner=_ruff_runner(0), eslint_runner=_eslint_runner(0, 0))
    assert rc == 1


def test_malformed_baseline_never_invokes_lint_tools(tmp_path):
    """Fail-closed must happen before measurement — a broken baseline can't be masked."""
    path = tmp_path / "lint_baseline.json"
    path.write_text("not json at all")
    calls = []

    def spy(*args, **kwargs):
        calls.append(args)
        return _proc(0, stdout="[]")

    ratchet.cmd_check(_check_args(path), ruff_runner=spy, eslint_runner=spy)
    assert calls == []


def test_baseline_missing_required_field_fails_closed(tmp_path):
    path = tmp_path / "lint_baseline.json"
    path.write_text(json.dumps({"schema_version": 1, "ruff": {"violation_count": 1}}))
    rc = ratchet.cmd_check(_check_args(path), ruff_runner=_ruff_runner(1), eslint_runner=_eslint_runner(0, 0))
    assert rc == 1


def test_baseline_negative_count_fails_closed(tmp_path):
    baseline = _write_baseline(tmp_path, ruff=-1, eslint_errors=0, eslint_warnings=0)
    rc = ratchet.cmd_check(_check_args(baseline), ruff_runner=_ruff_runner(0), eslint_runner=_eslint_runner(0, 0))
    assert rc == 1


def test_baseline_wrong_schema_version_fails_closed(tmp_path):
    path = tmp_path / "lint_baseline.json"
    path.write_text(
        json.dumps(
            {
                "schema_version": 999,
                "ruff": {"violation_count": 0},
                "eslint": {"error_count": 0, "warning_count": 0},
            }
        )
    )
    rc = ratchet.cmd_check(_check_args(path), ruff_runner=_ruff_runner(0), eslint_runner=_eslint_runner(0, 0))
    assert rc == 1


# ── FAIL CLOSED: lint tool failures never read as zero debt ───────────────

def test_ruff_oserror_fails_closed_not_zero(tmp_path):
    baseline = _write_baseline(tmp_path, ruff=0, eslint_errors=0, eslint_warnings=0)

    def raising_runner(*args, **kwargs):
        raise OSError("ruff: command not found")

    rc = ratchet.cmd_check(_check_args(baseline), ruff_runner=raising_runner, eslint_runner=_eslint_runner(0, 0))
    assert rc == 1


def test_ruff_unexpected_returncode_fails_closed(tmp_path):
    baseline = _write_baseline(tmp_path, ruff=0, eslint_errors=0, eslint_warnings=0)

    def runner(*args, **kwargs):
        return _proc(2, stdout="[]", stderr="internal error")

    rc = ratchet.cmd_check(_check_args(baseline), ruff_runner=runner, eslint_runner=_eslint_runner(0, 0))
    assert rc == 1


def test_ruff_non_json_output_fails_closed_not_zero(tmp_path):
    baseline = _write_baseline(tmp_path, ruff=0, eslint_errors=0, eslint_warnings=0)

    def runner(*args, **kwargs):
        return _proc(0, stdout="not json")

    rc = ratchet.cmd_check(_check_args(baseline), ruff_runner=runner, eslint_runner=_eslint_runner(0, 0))
    assert rc == 1


def test_ruff_json_not_a_list_fails_closed(tmp_path):
    baseline = _write_baseline(tmp_path, ruff=0, eslint_errors=0, eslint_warnings=0)

    def runner(*args, **kwargs):
        return _proc(0, stdout=json.dumps({"unexpected": "shape"}))

    rc = ratchet.cmd_check(_check_args(baseline), ruff_runner=runner, eslint_runner=_eslint_runner(0, 0))
    assert rc == 1


def test_eslint_oserror_fails_closed_not_zero(tmp_path):
    baseline = _write_baseline(tmp_path, ruff=0, eslint_errors=0, eslint_warnings=0)

    def raising_runner(*args, **kwargs):
        raise OSError("eslint: command not found")

    rc = ratchet.cmd_check(_check_args(baseline), ruff_runner=_ruff_runner(0, returncode=0), eslint_runner=raising_runner)
    assert rc == 1


def test_eslint_non_json_output_fails_closed_not_zero(tmp_path):
    baseline = _write_baseline(tmp_path, ruff=0, eslint_errors=0, eslint_warnings=0)

    def runner(*args, **kwargs):
        return _proc(0, stdout="<html>not json</html>")

    rc = ratchet.cmd_check(_check_args(baseline), ruff_runner=_ruff_runner(0, returncode=0), eslint_runner=runner)
    assert rc == 1


# ── Direct unit coverage of the pure comparison function ───────────────────

@pytest.mark.parametrize(
    "current,baseline,expect_problem",
    [
        ({"ruff_count": 5, "eslint_errors": 0, "eslint_warnings": 0}, {"ruff_count": 5}, False),
        ({"ruff_count": 6, "eslint_errors": 0, "eslint_warnings": 0}, {"ruff_count": 5}, True),
        ({"ruff_count": 4, "eslint_errors": 0, "eslint_warnings": 0}, {"ruff_count": 5}, True),
    ],
)
def test_compare_ruff_dimension(current, baseline, expect_problem):
    full_baseline = {
        "ruff": {"violation_count": baseline["ruff_count"]},
        "eslint": {"error_count": 0, "warning_count": 0},
    }
    problems = ratchet.compare(current, full_baseline)
    assert bool(problems) == expect_problem
