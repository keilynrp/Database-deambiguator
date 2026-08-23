"""Sentinel/mutation coverage for scripts/generate_repo_metrics.py (issue #295).

`scripts/generate_repo_metrics.py --check` is what CI trusts to prove the
README's badges/tables and docs/generated/repo_metrics.json still match the
repository's actual test collection, API surface, and toolchain versions.
That trust is only worth something if every way the projection could go
stale, or every way a source input could be missing/malformed, actually
fails the check rather than silently rendering a plausible-looking number.

No network, no real pytest/vitest subprocess, no database: every derivation
function takes an injectable collector/runner/path, exactly like
`backend_test_partitions._run_pytest_collect`'s `runner` parameter (see
test_partition_guard.py). Marker-parsing and README-rendering are pure
string functions exercised directly on in-memory fixtures, never the real
committed README.md, so these tests do not depend on repository content
that might legitimately change later.
"""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "scripts"))
import generate_repo_metrics as grm

pytestmark = pytest.mark.unit


# ── fixtures ─────────────────────────────────────────────────────────────

_METRICS = grm.Metrics(
    backend_tests_collected=10,
    backend_test_files=3,
    frontend_vitest_tests=5,
    api_operations=7,
    python_runtime_shipped="3.13",
    nextjs_version="16.3.1",
    react_version="19.2.8",
    typescript_version="6.0.3",
)


def _readme_fixture() -> str:
    """A minimal README carrying every expected marker region once, with
    surrounding prose that must survive rendering byte-for-byte."""
    lines = ["# Fixture Project", "", "Intro prose that must never change.", ""]
    for slug in sorted(grm.EXPECTED_SLUGS):
        lines.append(f"<!-- BEGIN GENERATED REPOSITORY METRICS: {slug} -->")
        lines.append("PLACEHOLDER")
        lines.append(f"<!-- END GENERATED REPOSITORY METRICS: {slug} -->")
    lines += ["", "Trailing prose that must never change.", ""]
    return "\n".join(lines)


class _FakeCompletedProcess:
    def __init__(self, returncode: int, stdout: str = "", stderr: str = ""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def _write_exact(path: Path, text: str) -> None:
    """Write with no newline translation — matches grm._write_text_exact.

    `Path.write_text(newline=...)` only exists from Python 3.13; this repo
    also runs a Python 3.12 compatibility lane, so these README fixtures go
    through the file-handle form instead.
    """
    with path.open("w", encoding="utf-8", newline="") as handle:
        handle.write(text)


# ── backend test collection: fail-closed ────────────────────────────────


def test_derive_backend_tests_counts_ids_and_distinct_files():
    node_ids = [
        "backend/tests/test_a.py::test_one",
        "backend/tests/test_a.py::test_two",
        "backend/tests/test_b.py::test_three",
    ]
    count, files = grm.derive_backend_tests(collector=lambda root: node_ids)
    assert count == 3
    assert files == 2


def test_derive_backend_tests_fails_closed_on_collector_exception():
    def broken_collector(root):
        raise RuntimeError("pytest collection failed closed (exit 2)")

    with pytest.raises(grm.MetricDerivationError, match="failed closed"):
        grm.derive_backend_tests(collector=broken_collector)


def test_derive_backend_tests_fails_closed_on_zero_tests():
    """A collection failure must never look like a legitimate zero count."""
    with pytest.raises(grm.MetricDerivationError, match="zero tests"):
        grm.derive_backend_tests(collector=lambda root: [])


# ── frontend Vitest enumeration: fail-closed ────────────────────────────


def test_derive_frontend_vitest_counts_listed_lines(tmp_path: Path):
    fake_runner = lambda *a, **k: _FakeCompletedProcess(
        returncode=0,
        stdout="a.test.ts > suite > case one\na.test.ts > suite > case two\n",
    )
    count = grm.derive_frontend_vitest(tmp_path, runner=fake_runner)
    assert count == 2


def test_derive_frontend_vitest_fails_closed_on_nonzero_exit(tmp_path: Path):
    fake_runner = lambda *a, **k: _FakeCompletedProcess(
        returncode=1, stderr="Failed to start forks worker"
    )
    with pytest.raises(grm.MetricDerivationError, match="failed closed"):
        grm.derive_frontend_vitest(tmp_path, runner=fake_runner)


def test_derive_frontend_vitest_fails_closed_on_zero_tests(tmp_path: Path):
    fake_runner = lambda *a, **k: _FakeCompletedProcess(returncode=0, stdout="")
    with pytest.raises(grm.MetricDerivationError, match="zero tests"):
        grm.derive_frontend_vitest(tmp_path, runner=fake_runner)


def test_derive_frontend_vitest_fails_closed_on_unparseable_line(tmp_path: Path):
    fake_runner = lambda *a, **k: _FakeCompletedProcess(
        returncode=0, stdout="not a valid vitest list line\n"
    )
    with pytest.raises(grm.MetricDerivationError, match="unexpected"):
        grm.derive_frontend_vitest(tmp_path, runner=fake_runner)


# ── OpenAPI operations: fail-closed ─────────────────────────────────────


def test_derive_api_operations_counts_http_methods_only(tmp_path: Path):
    spec = {
        "paths": {
            "/a": {"get": {}, "post": {}, "parameters": []},
            "/b": {"delete": {}},
        }
    }
    path = tmp_path / "openapi.json"
    path.write_text(json.dumps(spec), encoding="utf-8")
    assert grm.derive_api_operations(path) == 3


def test_derive_api_operations_fails_closed_on_malformed_json(tmp_path: Path):
    path = tmp_path / "openapi.json"
    path.write_text("{not valid json", encoding="utf-8")
    with pytest.raises(grm.MetricDerivationError, match="malformed OpenAPI JSON"):
        grm.derive_api_operations(path)


def test_derive_api_operations_fails_closed_on_missing_paths(tmp_path: Path):
    path = tmp_path / "openapi.json"
    path.write_text(json.dumps({"info": {}}), encoding="utf-8")
    with pytest.raises(grm.MetricDerivationError, match="paths"):
        grm.derive_api_operations(path)


def test_derive_api_operations_fails_closed_on_zero_operations(tmp_path: Path):
    path = tmp_path / "openapi.json"
    path.write_text(json.dumps({"paths": {"/a": {"parameters": []}}}), encoding="utf-8")
    with pytest.raises(grm.MetricDerivationError, match="zero HTTP operations"):
        grm.derive_api_operations(path)


def test_derive_api_operations_fails_closed_on_missing_file(tmp_path: Path):
    with pytest.raises(grm.MetricDerivationError, match="cannot read"):
        grm.derive_api_operations(tmp_path / "does-not-exist.json")


# ── Dockerfile python runtime: fail-closed ──────────────────────────────


def test_derive_python_runtime_reads_from_line(tmp_path: Path):
    path = tmp_path / "Dockerfile.backend"
    path.write_text("FROM python:3.13-slim\n\nWORKDIR /app\n", encoding="utf-8")
    assert grm.derive_python_runtime(path) == "3.13"


def test_derive_python_runtime_fails_closed_on_missing_from_line(tmp_path: Path):
    path = tmp_path / "Dockerfile.backend"
    path.write_text("WORKDIR /app\nRUN echo hi\n", encoding="utf-8")
    with pytest.raises(grm.MetricDerivationError, match="no 'FROM python"):
        grm.derive_python_runtime(path)


def test_derive_python_runtime_fails_closed_on_non_python_base_image(tmp_path: Path):
    path = tmp_path / "Dockerfile.backend"
    path.write_text("FROM node:22-slim\n", encoding="utf-8")
    with pytest.raises(grm.MetricDerivationError, match="no 'FROM python"):
        grm.derive_python_runtime(path)


# ── frontend dependency metadata: fail-closed ───────────────────────────


def test_derive_frontend_versions_reads_resolved_versions(tmp_path: Path):
    lock = {
        "packages": {
            "node_modules/next": {"version": "16.3.1"},
            "node_modules/react": {"version": "19.2.8"},
            "node_modules/typescript": {"version": "6.0.3"},
        }
    }
    path = tmp_path / "package-lock.json"
    path.write_text(json.dumps(lock), encoding="utf-8")
    assert grm.derive_frontend_versions(path) == ("16.3.1", "19.2.8", "6.0.3")


def test_derive_frontend_versions_fails_closed_on_missing_package(tmp_path: Path):
    lock = {"packages": {"node_modules/next": {"version": "16.3.1"}}}
    path = tmp_path / "package-lock.json"
    path.write_text(json.dumps(lock), encoding="utf-8")
    with pytest.raises(grm.MetricDerivationError, match="react"):
        grm.derive_frontend_versions(path)


def test_derive_frontend_versions_fails_closed_on_malformed_version_string(tmp_path: Path):
    lock = {
        "packages": {
            "node_modules/next": {"version": "^16"},
            "node_modules/react": {"version": "19.2.8"},
            "node_modules/typescript": {"version": "6.0.3"},
        }
    }
    path = tmp_path / "package-lock.json"
    path.write_text(json.dumps(lock), encoding="utf-8")
    with pytest.raises(grm.MetricDerivationError, match="next"):
        grm.derive_frontend_versions(path)


def test_derive_frontend_versions_fails_closed_on_malformed_json(tmp_path: Path):
    path = tmp_path / "package-lock.json"
    path.write_text("not json at all", encoding="utf-8")
    with pytest.raises(grm.MetricDerivationError, match="malformed"):
        grm.derive_frontend_versions(path)


# ── marker parsing: fail-closed on missing/duplicated/reversed ─────────


def test_parse_marker_regions_locates_every_expected_slug():
    regions = grm.parse_marker_regions(_readme_fixture())
    assert set(regions) == grm.EXPECTED_SLUGS


def test_parse_marker_regions_fails_closed_on_missing_begin():
    text = _readme_fixture().replace(
        "<!-- BEGIN GENERATED REPOSITORY METRICS: badge-tests -->\n", ""
    )
    with pytest.raises(grm.MarkerError, match="missing BEGIN/END.*badge-tests"):
        grm.parse_marker_regions(text)


def test_parse_marker_regions_fails_closed_on_missing_end():
    text = _readme_fixture().replace(
        "<!-- END GENERATED REPOSITORY METRICS: badge-tests -->\n", ""
    )
    with pytest.raises(grm.MarkerError, match="missing BEGIN/END.*badge-tests"):
        grm.parse_marker_regions(text)


def test_parse_marker_regions_fails_closed_on_duplicated_begin():
    text = _readme_fixture().replace(
        "<!-- BEGIN GENERATED REPOSITORY METRICS: badge-tests -->\nPLACEHOLDER\n",
        (
            "<!-- BEGIN GENERATED REPOSITORY METRICS: badge-tests -->\nPLACEHOLDER\n"
            "<!-- BEGIN GENERATED REPOSITORY METRICS: badge-tests -->\nPLACEHOLDER\n"
        ),
    )
    with pytest.raises(grm.MarkerError, match="duplicated.*badge-tests"):
        grm.parse_marker_regions(text)


def test_parse_marker_regions_fails_closed_on_reversed_marker():
    text = _readme_fixture().replace(
        (
            "<!-- BEGIN GENERATED REPOSITORY METRICS: badge-tests -->\n"
            "PLACEHOLDER\n"
            "<!-- END GENERATED REPOSITORY METRICS: badge-tests -->\n"
        ),
        (
            "<!-- END GENERATED REPOSITORY METRICS: badge-tests -->\n"
            "PLACEHOLDER\n"
            "<!-- BEGIN GENERATED REPOSITORY METRICS: badge-tests -->\n"
        ),
    )
    with pytest.raises(grm.MarkerError, match="reversed"):
        grm.parse_marker_regions(text)


def test_parse_marker_regions_fails_closed_on_unknown_slug():
    text = _readme_fixture() + (
        "<!-- BEGIN GENERATED REPOSITORY METRICS: totally-unknown -->\nx\n"
        "<!-- END GENERATED REPOSITORY METRICS: totally-unknown -->\n"
    )
    with pytest.raises(grm.MarkerError, match="unknown"):
        grm.parse_marker_regions(text)


# ── README rendering: idempotence + prose preservation ──────────────────


def test_render_readme_fills_every_region_from_metrics():
    rendered = grm.render_readme(_readme_fixture(), _METRICS)
    assert "PLACEHOLDER" not in rendered
    assert "3950" not in rendered  # sanity: this fixture's metrics, not the repo's
    assert "10" in rendered  # backend_tests_collected


def test_render_readme_preserves_prose_outside_markers_byte_for_byte():
    original = _readme_fixture()
    rendered = grm.render_readme(original, _METRICS)
    assert rendered.splitlines()[0:4] == original.splitlines()[0:4]
    assert rendered.splitlines()[-3:] == original.splitlines()[-3:]


def test_render_readme_is_idempotent():
    once = grm.render_readme(_readme_fixture(), _METRICS)
    twice = grm.render_readme(once, _METRICS)
    assert once == twice


def test_render_readme_fails_closed_on_malformed_markers():
    broken = _readme_fixture().replace(
        "<!-- END GENERATED REPOSITORY METRICS: badge-tests -->\n", ""
    )
    with pytest.raises(grm.MarkerError):
        grm.render_readme(broken, _METRICS)


# ── end-to-end orchestration: PASS / FAIL against a fully faked repo ────


def _write_fixture_repo(tmp_path: Path) -> grm.Config:
    (tmp_path / "sdk").mkdir()
    (tmp_path / "sdk" / "openapi.json").write_text(
        json.dumps({"paths": {"/a": {"get": {}}}}), encoding="utf-8"
    )
    (tmp_path / "Dockerfile.backend").write_text("FROM python:3.13-slim\n", encoding="utf-8")
    frontend_dir = tmp_path / "frontend"
    frontend_dir.mkdir()
    (frontend_dir / "package-lock.json").write_text(
        json.dumps(
            {
                "packages": {
                    "node_modules/next": {"version": "16.3.1"},
                    "node_modules/react": {"version": "19.2.8"},
                    "node_modules/typescript": {"version": "6.0.3"},
                }
            }
        ),
        encoding="utf-8",
    )
    _write_exact(tmp_path / "README.md", _readme_fixture())

    fake_runner = lambda *a, **k: _FakeCompletedProcess(
        returncode=0, stdout="a.test.ts > suite > only case\n"
    )
    cfg = grm.default_config(tmp_path)
    import dataclasses

    return dataclasses.replace(
        cfg,
        backend_collector=lambda root: ["backend/tests/test_a.py::test_one"],
        vitest_runner=fake_runner,
    )


def test_run_render_then_check_passes_on_a_clean_projection(tmp_path: Path):
    cfg = _write_fixture_repo(tmp_path)
    assert grm.run(cfg, check=False) == 0
    assert grm.run(cfg, check=True) == 0


def test_run_check_fails_on_stale_readme_metric(tmp_path: Path):
    cfg = _write_fixture_repo(tmp_path)
    assert grm.run(cfg, check=False) == 0

    text = cfg.readme_path.read_text(encoding="utf-8")
    mutated = text.replace(
        "![API Operations](https://img.shields.io/badge/API_Operations-1-blue)",
        "![API Operations](https://img.shields.io/badge/API_Operations-999-blue)",
    )
    assert mutated != text
    _write_exact(cfg.readme_path, mutated)

    assert grm.run(cfg, check=True) == 1


def test_run_check_fails_on_stale_json_artifact(tmp_path: Path):
    cfg = _write_fixture_repo(tmp_path)
    assert grm.run(cfg, check=False) == 0

    artifact = json.loads(cfg.artifact_path.read_text(encoding="utf-8"))
    artifact["metrics"]["api_operations"] = 999
    cfg.artifact_path.write_text(json.dumps(artifact, indent=2), encoding="utf-8")

    assert grm.run(cfg, check=True) == 1


def test_run_fails_closed_on_missing_begin_marker(tmp_path: Path):
    cfg = _write_fixture_repo(tmp_path)
    broken = cfg.readme_path.read_text(encoding="utf-8").replace(
        "<!-- BEGIN GENERATED REPOSITORY METRICS: badge-tests -->\n", ""
    )
    _write_exact(cfg.readme_path, broken)

    assert grm.run(cfg, check=True) == 1
    assert grm.run(cfg, check=False) == 1


def test_run_fails_closed_on_pytest_collection_failure(tmp_path: Path):
    cfg = _write_fixture_repo(tmp_path)

    def broken_collector(root):
        raise RuntimeError("pytest collection failed closed (exit 2)")

    import dataclasses

    cfg = dataclasses.replace(cfg, backend_collector=broken_collector)
    assert grm.run(cfg, check=True) == 1


def test_run_fails_closed_on_vitest_enumeration_failure(tmp_path: Path):
    cfg = _write_fixture_repo(tmp_path)

    def broken_runner(*a, **k):
        return _FakeCompletedProcess(returncode=1, stderr="worker timeout")

    import dataclasses

    cfg = dataclasses.replace(cfg, vitest_runner=broken_runner)
    assert grm.run(cfg, check=True) == 1
