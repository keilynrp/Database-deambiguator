#!/usr/bin/env python3
"""Deterministic repository capability/test/version metrics (issue #295).

README.md used to carry hand-maintained claims — backend test counts, a
Vitest count, an API route count, Python/Next.js/React/TypeScript versions —
that drift from the repository the moment anyone adds a test or bumps a
dependency, because nothing regenerates them. This script is the single
projection all of those numbers come from, so there is exactly one place to
fix when the repository changes instead of four or five README spots that
quietly disagree with each other and with reality.

Commands
--------
  python scripts/generate_repo_metrics.py            # render: rewrite the
      generated README region(s) and docs/generated/repo_metrics.json.
  python scripts/generate_repo_metrics.py --check     # fail (exit 1) if the
      committed README/artifact would change.

Authoritative sources (see docs/DOCUMENTATION_GOVERNANCE.md for the policy
this implements):

  backend tests collected / test files
      pytest --collect-only over backend/tests/, via the exact collection
      primitive scripts/backend_test_partitions.py uses for CI sharding
      (issue #293) — not a decorator/string/file heuristic. "Test files" is
      the count of distinct files that appear in the collected node IDs, not
      every *.py under backend/tests/ (helpers, __init__.py, conftest.py are
      not "test files").

  frontend Vitest tests
      `vitest list` — Vitest's own enumeration primitive, run against the
      pinned project config. Not a regex over `it(`/`test(` source, and not a
      scrape of colorized run output.

  API operations
      sdk/openapi.json: documented HTTP operations (get/post/put/patch/
      delete/options/head/trace) across `paths`. The committed spec is
      already proven current by the blocking openapi-drift CI gate.

  Python runtime (shipped)
      the `FROM python:X.Y...` line in Dockerfile.backend — the production
      container's actual runtime, not a developer compatibility range.

  Next.js / React / TypeScript
      resolved versions from frontend/package-lock.json.

Every derivation fails closed: a missing file, a malformed source, a
collection/tool failure, or a zero count is an error, never a silently
empty/zero measurement (see MetricDerivationError below).
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections.abc import Callable
from dataclasses import dataclass, field, fields
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

sys.path.insert(0, str(REPO_ROOT / "scripts"))
import backend_test_partitions as btp

DEFAULT_BACKEND_TEST_ROOT = "backend/tests"
HTTP_METHODS = {"get", "post", "put", "patch", "delete", "options", "head", "trace"}
FROM_PYTHON_RE = re.compile(r"^FROM\s+python:(\d+\.\d+)", re.IGNORECASE)

MARKER_BEGIN_RE = re.compile(r"^<!-- BEGIN GENERATED REPOSITORY METRICS: (?P<slug>[a-z0-9-]+) -->$")
MARKER_END_RE = re.compile(r"^<!-- END GENERATED REPOSITORY METRICS: (?P<slug>[a-z0-9-]+) -->$")


class MetricDerivationError(RuntimeError):
    """A metric could not be derived. Always fail closed — never a zero."""


class MarkerError(RuntimeError):
    """The README's generated marker boundaries are missing/duplicated/reversed."""


def _read_text_exact(path: Path) -> str:
    """Read a file with no newline translation.

    `Path.read_text(newline=...)` only exists from Python 3.13; this repo's
    CI also runs a Python 3.12 compatibility lane, so newline control goes
    through the file-handle form instead (`open(newline=...)` has always
    accepted it).
    """
    with path.open("r", encoding="utf-8", newline="") as handle:
        return handle.read()


def _write_text_exact(path: Path, text: str) -> None:
    """Write exactly the given text — no newline translation.

    Same 3.12-compatibility reason as `_read_text_exact`: without this, the
    write_text() default (universal-newline translation) would turn every
    "\\n" this module renders into os.linesep, silently rewriting the whole
    file's line endings on Windows.
    """
    with path.open("w", encoding="utf-8", newline="") as handle:
        handle.write(text)


# ── Metrics ──────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class Metrics:
    backend_tests_collected: int
    backend_test_files: int
    frontend_vitest_tests: int
    api_operations: int
    python_runtime_shipped: str
    nextjs_version: str
    react_version: str
    typescript_version: str

    @property
    def nextjs_major(self) -> str:
        return self.nextjs_version.split(".", 1)[0]

    @property
    def react_major(self) -> str:
        return self.react_version.split(".", 1)[0]

    @property
    def typescript_major(self) -> str:
        return self.typescript_version.split(".", 1)[0]


# ── Derivations (each independently injectable for tests) ──────────────────


def derive_backend_tests(
    test_root: str = DEFAULT_BACKEND_TEST_ROOT,
    collector: Callable[[str], list[str]] = btp.collect_exhaustive,
) -> tuple[int, int]:
    """Collected test count + distinct test-file count.

    `collector` defaults to the real #293 pytest-collection primitive, which
    already fails closed on any pytest exit code other than 0/5 (see
    backend_test_partitions._run_pytest_collect). Injected here so sentinel
    tests can simulate a collection failure or an empty collection without a
    real pytest subprocess.
    """
    try:
        node_ids = collector(test_root)
    except Exception as exc:
        raise MetricDerivationError(f"backend test collection failed closed: {exc}") from exc

    if not node_ids:
        raise MetricDerivationError(
            "pytest collection returned zero tests; refusing to treat that as a "
            "valid measurement (a collection failure must not look like zero tests)"
        )

    files = {node_id.split("::", 1)[0] for node_id in node_ids}
    return len(node_ids), len(files)


def derive_frontend_vitest(
    frontend_dir: Path,
    runner: Callable[..., subprocess.CompletedProcess] = subprocess.run,
) -> int:
    """Count of Vitest tests via `vitest list` — Vitest's own enumeration.

    `runner` is injectable so sentinel tests can simulate a non-zero exit,
    empty output, or unparseable output without installing/running the real
    frontend toolchain.
    """
    vitest_bin = frontend_dir / "node_modules" / ".bin" / "vitest"
    proc = runner(
        [str(vitest_bin), "list"],
        cwd=str(frontend_dir),
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise MetricDerivationError(
            f"vitest list failed closed (exit {proc.returncode}): {proc.stderr.strip()[:500]}"
        )

    lines = [line for line in proc.stdout.splitlines() if line.strip()]
    if not lines:
        raise MetricDerivationError(
            "vitest list produced zero tests; refusing to treat that as a valid "
            "measurement (an enumeration failure must not look like zero tests)"
        )
    for line in lines:
        if " > " not in line:
            raise MetricDerivationError(
                f"unexpected `vitest list` output line (no ' > ' separator): {line!r}"
            )
    return len(lines)


def derive_api_operations(openapi_path: Path) -> int:
    try:
        text = openapi_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise MetricDerivationError(f"cannot read {openapi_path}: {exc}") from exc

    try:
        spec = json.loads(text)
    except json.JSONDecodeError as exc:
        raise MetricDerivationError(f"malformed OpenAPI JSON at {openapi_path}: {exc}") from exc

    paths = spec.get("paths") if isinstance(spec, dict) else None
    if not isinstance(paths, dict) or not paths:
        raise MetricDerivationError(f"{openapi_path} has no usable 'paths' object")

    count = 0
    for operations in paths.values():
        if not isinstance(operations, dict):
            continue
        for method in operations:
            if method.lower() in HTTP_METHODS:
                count += 1

    if count == 0:
        raise MetricDerivationError(
            f"{openapi_path} declares zero HTTP operations; refusing to treat "
            "that as a valid measurement"
        )
    return count


def derive_python_runtime(dockerfile_path: Path) -> str:
    try:
        lines = dockerfile_path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise MetricDerivationError(f"cannot read {dockerfile_path}: {exc}") from exc

    for line in lines:
        match = FROM_PYTHON_RE.match(line.strip())
        if match:
            return match.group(1)

    raise MetricDerivationError(
        f"no 'FROM python:X.Y...' line found in {dockerfile_path}; refusing to "
        "guess the shipped runtime"
    )


_RESOLVED_VERSION_RE = re.compile(r"^\d+\.\d+\.\d+")


def derive_frontend_versions(package_lock_path: Path) -> tuple[str, str, str]:
    try:
        text = package_lock_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise MetricDerivationError(f"cannot read {package_lock_path}: {exc}") from exc

    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise MetricDerivationError(f"malformed {package_lock_path}: {exc}") from exc

    packages = data.get("packages") if isinstance(data, dict) else None
    if not isinstance(packages, dict):
        raise MetricDerivationError(f"{package_lock_path} has no usable 'packages' object")

    resolved: dict[str, str] = {}
    for name, key in (
        ("next", "node_modules/next"),
        ("react", "node_modules/react"),
        ("typescript", "node_modules/typescript"),
    ):
        entry = packages.get(key)
        version = entry.get("version") if isinstance(entry, dict) else None
        if not isinstance(version, str) or not _RESOLVED_VERSION_RE.match(version):
            raise MetricDerivationError(
                f"missing/malformed resolved version for '{name}' ({key}) in {package_lock_path}"
            )
        resolved[name] = version

    return resolved["next"], resolved["react"], resolved["typescript"]


# ── Config: bundles paths + injectable collaborators ────────────────────────


@dataclass(frozen=True)
class Config:
    repo_root: Path
    readme_path: Path
    artifact_path: Path
    openapi_path: Path
    dockerfile_path: Path
    package_lock_path: Path
    frontend_dir: Path
    backend_test_root: str = DEFAULT_BACKEND_TEST_ROOT
    backend_collector: Callable[[str], list[str]] = field(default=btp.collect_exhaustive)
    vitest_runner: Callable[..., subprocess.CompletedProcess] = field(default=subprocess.run)


def default_config(repo_root: Path = REPO_ROOT) -> Config:
    return Config(
        repo_root=repo_root,
        readme_path=repo_root / "README.md",
        artifact_path=repo_root / "docs" / "generated" / "repo_metrics.json",
        openapi_path=repo_root / "sdk" / "openapi.json",
        dockerfile_path=repo_root / "Dockerfile.backend",
        package_lock_path=repo_root / "frontend" / "package-lock.json",
        frontend_dir=repo_root / "frontend",
    )


def compute_metrics(cfg: Config) -> Metrics:
    backend_tests_collected, backend_test_files = derive_backend_tests(
        cfg.backend_test_root, cfg.backend_collector
    )
    frontend_vitest_tests = derive_frontend_vitest(cfg.frontend_dir, cfg.vitest_runner)
    api_operations = derive_api_operations(cfg.openapi_path)
    python_runtime_shipped = derive_python_runtime(cfg.dockerfile_path)
    nextjs_version, react_version, typescript_version = derive_frontend_versions(
        cfg.package_lock_path
    )
    return Metrics(
        backend_tests_collected=backend_tests_collected,
        backend_test_files=backend_test_files,
        frontend_vitest_tests=frontend_vitest_tests,
        api_operations=api_operations,
        python_runtime_shipped=python_runtime_shipped,
        nextjs_version=nextjs_version,
        react_version=react_version,
        typescript_version=typescript_version,
    )


# ── Generated artifact (JSON projection) ────────────────────────────────────

ARTIFACT_SCHEMA_VERSION = 1

_DERIVATION_DEFINITIONS = {
    "backend_tests_collected": (
        "Count of pytest node IDs collected from backend/tests/ via "
        "scripts/backend_test_partitions.py's collect_exhaustive() "
        "(pytest --collect-only, fail-closed on any exit code other than 0/5)."
    ),
    "backend_test_files": (
        "Count of distinct file paths among those collected node IDs "
        "(not every *.py under backend/tests/)."
    ),
    "frontend_vitest_tests": (
        "Count of tests printed by `vitest list` (frontend/, pinned project config)."
    ),
    "api_operations": (
        "Count of get/post/put/patch/delete/options/head/trace keys across "
        "'paths' in sdk/openapi.json."
    ),
    "python_runtime_shipped": (
        "Major.minor version parsed from the 'FROM python:X.Y...' line in "
        "Dockerfile.backend."
    ),
    "nextjs_version": "Resolved version of 'next' in frontend/package-lock.json.",
    "react_version": "Resolved version of 'react' in frontend/package-lock.json.",
    "typescript_version": "Resolved version of 'typescript' in frontend/package-lock.json.",
}


def render_artifact(metrics: Metrics, cfg: Config) -> str:
    payload = {
        "schema_version": ARTIFACT_SCHEMA_VERSION,
        "metrics": {f.name: getattr(metrics, f.name) for f in fields(Metrics)},
        "derivations": _DERIVATION_DEFINITIONS,
        "sources": {
            "backend_tests": f"{cfg.backend_test_root}/ (pytest collection)",
            "frontend_vitest": "frontend/ (`vitest list`)",
            "openapi_spec": str(cfg.openapi_path.relative_to(cfg.repo_root)).replace("\\", "/"),
            "dockerfile": str(cfg.dockerfile_path.relative_to(cfg.repo_root)).replace("\\", "/"),
            "frontend_lockfile": str(cfg.package_lock_path.relative_to(cfg.repo_root)).replace(
                "\\", "/"
            ),
        },
    }
    return json.dumps(payload, indent=2, sort_keys=False) + "\n"


# ── README generated regions ────────────────────────────────────────────────


def _render_badge_python(m: Metrics) -> str:
    return (
        f"![Python](https://img.shields.io/badge/Python-{m.python_runtime_shipped}-3776AB"
        "?logo=python&logoColor=white)"
    )


def _render_badge_nextjs(m: Metrics) -> str:
    return (
        f"![Next.js](https://img.shields.io/badge/Next.js-{m.nextjs_major}-000000"
        "?logo=nextdotjs&logoColor=white)"
    )


def _render_badge_react(m: Metrics) -> str:
    return f"![React](https://img.shields.io/badge/React-{m.react_major}-61DAFB?logo=react&logoColor=111111)"


def _render_badge_typescript(m: Metrics) -> str:
    return (
        f"![TypeScript](https://img.shields.io/badge/TypeScript-{m.typescript_major}-3178C6"
        "?logo=typescript&logoColor=white)"
    )


def _render_badge_tests(m: Metrics) -> str:
    return (
        f"![Tests](https://img.shields.io/badge/Tests-{m.backend_tests_collected}_collected"
        "-28A745?logo=pytest&logoColor=white)"
    )


def _render_badge_api_operations(m: Metrics) -> str:
    return f"![API Operations](https://img.shields.io/badge/API_Operations-{m.api_operations}-blue)"


def _render_tree_backend_tests(m: Metrics) -> str:
    return f"  tests/                 {m.backend_test_files} test files, {m.backend_tests_collected} tests"


def _render_techstack_backend_runtime(m: Metrics) -> str:
    return f"| Backend API | Python {m.python_runtime_shipped}, FastAPI, Pydantic v2, SQLAlchemy |"


def _render_techstack_frontend(m: Metrics) -> str:
    return (
        f"| Frontend | Next.js {m.nextjs_major}, React {m.react_major}, "
        f"TypeScript {m.typescript_major}, Tailwind CSS 4, Recharts, D3 |"
    )


def _render_techstack_testing(m: Metrics) -> str:
    return (
        f"| Testing | pytest ({m.backend_tests_collected} tests collected), "
        f"Vitest ({m.frontend_vitest_tests} tests), Playwright |"
    )


def _render_summary_test_stats(m: Metrics) -> str:
    return (
        f"**Current test stats:** {m.backend_tests_collected} backend tests collected "
        f"across {m.backend_test_files} test files. Frontend: {m.frontend_vitest_tests} Vitest tests."
    )


REGION_RENDERERS: dict[str, Callable[[Metrics], str]] = {
    "badge-python-runtime": _render_badge_python,
    "badge-nextjs": _render_badge_nextjs,
    "badge-react": _render_badge_react,
    "badge-typescript": _render_badge_typescript,
    "badge-tests": _render_badge_tests,
    "badge-api-operations": _render_badge_api_operations,
    "tree-backend-tests": _render_tree_backend_tests,
    "techstack-backend-runtime": _render_techstack_backend_runtime,
    "techstack-frontend": _render_techstack_frontend,
    "techstack-testing": _render_techstack_testing,
    "summary-test-stats": _render_summary_test_stats,
}

EXPECTED_SLUGS = frozenset(REGION_RENDERERS)


def _find_markers(lines: list[str]) -> tuple[dict[str, list[int]], dict[str, list[int]]]:
    begins: dict[str, list[int]] = {}
    ends: dict[str, list[int]] = {}
    for idx, line in enumerate(lines):
        begin_match = MARKER_BEGIN_RE.match(line)
        if begin_match:
            begins.setdefault(begin_match.group("slug"), []).append(idx)
            continue
        end_match = MARKER_END_RE.match(line)
        if end_match:
            ends.setdefault(end_match.group("slug"), []).append(idx)
    return begins, ends


def parse_marker_regions(text: str) -> dict[str, tuple[int, int]]:
    """Validate and locate every expected generated region.

    Fails closed (raises MarkerError) on: a marker slug this generator does
    not know how to render, a missing BEGIN or END, more than one BEGIN or
    END for a slug, or a BEGIN that does not precede its END.

    Returns {slug: (begin_line_index, end_line_index)}, both 0-based indices
    of the marker comment lines themselves (the generated content is the
    lines strictly between them).
    """
    lines = text.split("\n")
    begins, ends = _find_markers(lines)

    unknown = (set(begins) | set(ends)) - EXPECTED_SLUGS
    if unknown:
        raise MarkerError(
            f"unknown generated-metrics marker slug(s), not recognized by this "
            f"generator: {sorted(unknown)}"
        )

    regions: dict[str, tuple[int, int]] = {}
    for slug in sorted(EXPECTED_SLUGS):
        slug_begins = begins.get(slug, [])
        slug_ends = ends.get(slug, [])
        if not slug_begins or not slug_ends:
            raise MarkerError(f"missing BEGIN/END marker for generated region '{slug}'")
        if len(slug_begins) > 1 or len(slug_ends) > 1:
            raise MarkerError(f"duplicated BEGIN/END marker for generated region '{slug}'")
        begin_idx, end_idx = slug_begins[0], slug_ends[0]
        if begin_idx >= end_idx:
            raise MarkerError(f"reversed or empty marker pair for generated region '{slug}'")
        regions[slug] = (begin_idx, end_idx)

    return regions


def render_readme(text: str, metrics: Metrics) -> str:
    """Replace only the content strictly between each marker pair.

    Every other byte of the input — prose, headings, other tables — passes
    through unchanged, including the trailing-newline shape of the file.
    """
    lines = text.split("\n")
    regions = parse_marker_regions(text)

    # Apply replacements back-to-front so earlier indices stay valid.
    for slug, (begin_idx, end_idx) in sorted(regions.items(), key=lambda kv: kv[1][0], reverse=True):
        rendered_line = REGION_RENDERERS[slug](metrics)
        lines[begin_idx + 1 : end_idx] = [rendered_line]

    return "\n".join(lines)


# ── Orchestration ────────────────────────────────────────────────────────


def run(cfg: Config, check: bool) -> int:
    try:
        metrics = compute_metrics(cfg)
    except MetricDerivationError as exc:
        print(f"[repo-metrics] DERIVATION FAILED: {exc}", file=sys.stderr)
        return 1

    try:
        current_readme = _read_text_exact(cfg.readme_path)
    except OSError as exc:
        print(f"[repo-metrics] cannot read {cfg.readme_path}: {exc}", file=sys.stderr)
        return 1

    try:
        rendered_readme = render_readme(current_readme, metrics)
    except MarkerError as exc:
        print(f"[repo-metrics] MARKER GUARD FAILED: {exc}", file=sys.stderr)
        return 1

    # Idempotence proof: rendering the already-rendered output must be a no-op.
    twice = render_readme(rendered_readme, metrics)
    if twice != rendered_readme:
        print(
            "[repo-metrics] generator is not idempotent — refusing to write "
            "(render(render(x)) != render(x))",
            file=sys.stderr,
        )
        return 1

    rendered_artifact = render_artifact(metrics, cfg)
    current_artifact = (
        _read_text_exact(cfg.artifact_path) if cfg.artifact_path.exists() else None
    )

    readme_stale = rendered_readme != current_readme
    artifact_stale = rendered_artifact != current_artifact

    if check:
        if readme_stale or artifact_stale:
            print("[repo-metrics] DRIFT: generated repository metrics are stale.", file=sys.stderr)
            if readme_stale:
                print(f"  - {cfg.readme_path} generated region(s) do not match derived metrics", file=sys.stderr)
            if artifact_stale:
                print(f"  - {cfg.artifact_path} does not match derived metrics", file=sys.stderr)
            print("Run:  python scripts/generate_repo_metrics.py", file=sys.stderr)
            return 1
        print(f"[repo-metrics] OK — README and {cfg.artifact_path.name} match derived metrics.")
        return 0

    if readme_stale:
        _write_text_exact(cfg.readme_path, rendered_readme)
    cfg.artifact_path.parent.mkdir(parents=True, exist_ok=True)
    if artifact_stale:
        _write_text_exact(cfg.artifact_path, rendered_artifact)

    print(
        "[repo-metrics] updated"
        f" backend_tests_collected={metrics.backend_tests_collected}"
        f" backend_test_files={metrics.backend_test_files}"
        f" frontend_vitest_tests={metrics.frontend_vitest_tests}"
        f" api_operations={metrics.api_operations}"
        f" python_runtime_shipped={metrics.python_runtime_shipped}"
        f" nextjs={metrics.nextjs_version} react={metrics.react_version} typescript={metrics.typescript_version}"
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true", help="Fail if generated output would change.")
    args = parser.parse_args(argv)
    return run(default_config(), check=args.check)


if __name__ == "__main__":
    raise SystemExit(main())
