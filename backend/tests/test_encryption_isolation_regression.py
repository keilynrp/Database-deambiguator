# backend/tests/test_encryption_isolation_regression.py
"""Regression for the CI shard 0/1 failure on PR #307 (issue #293).

Root cause: test_encryption.py exercises backend.encryption's import-time
key-loading logic by mutating os.environ["ENCRYPTION_KEY"] directly (not via
monkeypatch — monkeypatch restores os.environ but can't undo a module
reload) and calling importlib.reload() on backend.encryption. Without a
restore afterward, backend.encryption._primary_fernet was left None for the
rest of the pytest process. Because CI shards run a fixed list of node IDs
in one process (see scripts/backend_test_partitions.py), any test later in
the same shard that reads backend.encryption.has_primary_key() — via
ops_checks._secrets_check() — silently inherited that contaminated state:

  - shard 0: test_sprint104_ops_checks.py expected "degraded", got "critical"
  - shard 1: test_epic017_secrets_check.py expected "warning", got "critical"

Both are downstream of test_encryption.py in shard collection order. This
file proves the fix (an autouse restore fixture in test_encryption.py, plus
a defensive pre/post reload in test_epic017_secrets_check.py) by literally
running the contaminating test immediately before each victim test in a
single pytest process — the same mechanism CI uses — so a regression in
either fixture fails here rather than resurfacing as a shard-order flake.
"""
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

CONTAMINATING_TEST = "backend/tests/test_encryption.py::test_no_key_encrypt_returns_plaintext"
SPRINT104_VICTIM = (
    "backend/tests/test_sprint104_ops_checks.py::test_ops_checks_returns_repeatable_summary"
)
EPIC017_VICTIM = (
    "backend/tests/test_epic017_secrets_check.py::test_warning_when_retiring_keys_present"
)


def _run_pytest(*node_ids: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "pytest", "-q", *node_ids],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )


def test_sprint104_ops_checks_passes_after_encryption_module_reload_test():
    proc = _run_pytest(CONTAMINATING_TEST, SPRINT104_VICTIM)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "2 passed" in proc.stdout


def test_epic017_secrets_check_passes_after_encryption_module_reload_test():
    proc = _run_pytest(CONTAMINATING_TEST, EPIC017_VICTIM)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "2 passed" in proc.stdout


def test_sprint104_ops_checks_passes_independently():
    proc = _run_pytest(SPRINT104_VICTIM)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "1 passed" in proc.stdout


def test_epic017_secrets_check_passes_independently():
    proc = _run_pytest(EPIC017_VICTIM)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "1 passed" in proc.stdout
