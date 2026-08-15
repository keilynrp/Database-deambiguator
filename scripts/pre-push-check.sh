#!/usr/bin/env bash
# Pre-push smoke check that mirrors the CI gates against the local changes.
# Goal: catch CI-breaking warnings BEFORE pushing so the loop stops being
# "push → red CI → fix → push".
#
# Usage:
#   bash scripts/pre-push-check.sh            # check vs. origin/main
#   bash scripts/pre-push-check.sh HEAD~3     # check vs. an explicit base
#
# Install as a git hook to run automatically before every push:
#   ln -sf ../../scripts/pre-push-check.sh .git/hooks/pre-push
#   chmod +x scripts/pre-push-check.sh .git/hooks/pre-push
#
# Exit code 0 = safe to push. Non-zero = CI will likely fail.
set -uo pipefail

BASE="${1:-origin/main}"
ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"

# Collect changed files vs. BASE (added + modified, no deletes)
mapfile -t CHANGED < <(git diff --name-only --diff-filter=AM "$BASE"...HEAD)

PYTHON_CHANGED=()
TS_CHANGED=()
BACKEND_TESTS_CHANGED=()
PY_SOURCE_CHANGED=()

for f in "${CHANGED[@]}"; do
  case "$f" in
    *.ts|*.tsx|*.js|*.jsx) TS_CHANGED+=("$f");;
    *.py) PYTHON_CHANGED+=("$f");;
  esac
  case "$f" in
    backend/tests/test_*.py) BACKEND_TESTS_CHANGED+=("$f");;
    *.py)                    PY_SOURCE_CHANGED+=("$f");;
  esac
done

EXIT=0

# ── Gate result cache ────────────────────────────────────────────────────────
# A gate whose inputs are byte-identical to a run that already passed does not
# have to run again. The key is the git tree hash of the paths that decide the
# result, so rebasing a commit onto a new base — which rewrites the sha but not
# the content — is a cache hit rather than another full suite.
#
# Two things keep it from lying:
#   * The suites run against the WORKING TREE while the key describes HEAD. When
#     the deciding paths are dirty or hold untracked files the two disagree, so
#     gate_key prints nothing and the gate runs unconditionally. A cache that is
#     wrong in the "skip it" direction is worse than no cache at all.
#   * Entries live under .git/, so they are per-clone and never reach a commit.
CACHE_DIR="$(git rev-parse --git-dir)/pre-push-cache"
mkdir -p "$CACHE_DIR"

# gate_key <name> <path>… → key on stdout, or nothing when it cannot be trusted
gate_key() {
  local name="$1"; shift
  [ -n "$(git status --porcelain -- "$@" 2>/dev/null)" ] && return 0
  {
    echo "$name"
    for p in "$@"; do git rev-parse "HEAD:$p" 2>/dev/null || echo "absent:$p"; done
  } | git hash-object --stdin
}

gate_hit()    { [ -n "$1" ] && [ -f "$CACHE_DIR/$1" ]; }
gate_record() { [ -n "$1" ] && : > "$CACHE_DIR/$1"; }

echo "── Pre-push check vs. $BASE ──"
echo "Changed files: ${#CHANGED[@]} (TS: ${#TS_CHANGED[@]}, Py: ${#PYTHON_CHANGED[@]})"
echo

# 1. Frontend ESLint (BLOCKING gate in CI: --max-warnings=0 on changed files)
if [ ${#TS_CHANGED[@]} -gt 0 ]; then
  echo "▶ ESLint --max-warnings=0 on changed frontend files…"
  REL=()
  for f in "${TS_CHANGED[@]}"; do
    case "$f" in
      frontend/*) REL+=("${f#frontend/}");;
    esac
  done
  if [ ${#REL[@]} -gt 0 ]; then
    (cd frontend && npx eslint --max-warnings=0 "${REL[@]}") || EXIT=1
  fi
  echo
fi

# 2. Frontend TypeScript check
if [ ${#TS_CHANGED[@]} -gt 0 ]; then
  echo "▶ tsc --noEmit (frontend)…"
  (cd frontend && npx tsc --noEmit --pretty false) || EXIT=1
  echo
fi

# 3. Domain-scope contract lint (BLOCKING in CI when backend touched)
if [ ${#PYTHON_CHANGED[@]} -gt 0 ]; then
  echo "▶ scripts/lint_domain_scope.py…"
  python scripts/lint_domain_scope.py || EXIT=1
  echo
  echo "▶ scripts/lint_entity_query.py…"
  python scripts/lint_entity_query.py || EXIT=1
  echo
fi

# 3b. Lock-file integrity (BLOCKING in CI: `npm ci` exits non-zero on drift)
# Always run — even unrelated edits can desync the lockfile if anyone ran
# `npm install` colaterally. Costs ~2s with cached node_modules.
echo "▶ npm ci --dry-run (frontend lockfile integrity)…"
LOCK_LOG="$(mktemp)"
if ! (cd frontend && npm ci --dry-run --no-audit --no-fund) >"$LOCK_LOG" 2>&1; then
  echo "  ✗ Lockfile drift detected. Last lines:"
  tail -15 "$LOCK_LOG"
  echo ""
  echo "  Hint: this often happens after \`npm install\` on Windows strips"
  echo "  Linux-only optional deps (@emnapi/*). Use scripts/refresh-lockfile.py"
  echo "  to merge platform-specific entries from origin/main."
  EXIT=1
fi
rm -f "$LOCK_LOG"
echo

# 3c. Frontend unit tests (vitest) — runs the same suite as the CI `frontend-test` job.
if [ ${#TS_CHANGED[@]} -gt 0 ]; then
  VITEST_KEY="$(gate_key vitest frontend)"
  if gate_hit "$VITEST_KEY"; then
    echo "▶ vitest --run — SKIPPED (this frontend/ tree already passed)"
  else
    echo "▶ vitest --run (frontend unit tests)…"
    if (cd frontend && npm test -- --run --reporter=dot); then
      gate_record "$VITEST_KEY"
    else
      EXIT=1
    fi
  fi
  echo
fi

# 4. Backend tests.
#
# Which branch runs is decided by whether SOURCE changed, not by whether a test
# file did. It used to be the other way round — an if/elif with the scoped run
# first — so touching one test file REPLACED the full suite instead of adding to
# it. A branch that rewrote report_builder.py and the shared localize.py got its
# local verification cut from 3820 tests to 27 because it also edited two test
# files, and CI then found seven failures the push had reported as green.
#
# Source changed, with or without tests: run everything. The full suite already
# includes whatever test files were touched, so there is no scoped run to add.
if [ ${#PY_SOURCE_CHANGED[@]} -eq 0 ] && [ ${#BACKEND_TESTS_CHANGED[@]} -gt 0 ]; then
  # Only test files changed — nothing else can have broken.
  echo "▶ pytest (scoped: only test files changed): ${BACKEND_TESTS_CHANGED[*]}"
  python -m pytest -x -q "${BACKEND_TESTS_CHANGED[@]}" || EXIT=1
  echo
elif [ ${#PYTHON_CHANGED[@]} -gt 0 ]; then
  # conftest.py sits at the repo root and requirements pin the interpreter's
  # libraries, so both decide the outcome as much as backend/ itself does.
  PYTEST_KEY="$(gate_key backend-full backend conftest.py requirements.txt requirements.lock)"
  if gate_hit "$PYTEST_KEY"; then
    echo "▶ pytest backend/tests — SKIPPED (this backend/ tree already passed the full suite)"
  else
    echo "▶ pytest backend/tests (full suite — backend source changed)…"
    if python -m pytest -x -q backend/tests/; then
      gate_record "$PYTEST_KEY"
    else
      EXIT=1
    fi
  fi
  echo
fi

if [ $EXIT -eq 0 ]; then
  echo "✓ All local gates green — safe to push."
else
  echo "✗ One or more gates failed — fix before pushing."
fi
exit $EXIT
