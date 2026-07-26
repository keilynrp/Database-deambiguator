#!/usr/bin/env bash
# Regenerate the TypeScript and Python SDK clients from sdk/openapi.json.
#
#   bash scripts/generate-sdk-clients.sh
#
# Runs both generators inside pinned official Docker images, so the toolchain is
# identical on every machine and no local Node/Python install is required. This
# is the sanctioned path on Windows, where `npx` fails with
# "ECOMPROMISED — Lock compromised" and adding the generators to
# frontend/package.json would regenerate the lockfile and strip Linux-native
# binaries. Docker gives a clean Linux toolchain without touching either.
#
# Prerequisites: Docker running, and a current sdk/openapi.json
# (regenerate it first with:  node scripts/generate-sdk.mjs).
#
# Generator versions are PINNED here — an unpinned generator produces phantom
# diffs on unrelated PRs, and a drift gate that cries wolf gets ignored.
set -euo pipefail

# --check regenerates and fails if the committed clients are stale (CI drift
# gate). Without it, the clients are regenerated in place.
CHECK_ONLY=0
if [ "${1:-}" = "--check" ]; then
  CHECK_ONLY=1
fi

# ── Pinned generator versions ────────────────────────────────────────────────
HEYAPI_VERSION="0.99.0"          # @hey-api/openapi-ts (TypeScript)
TYPESCRIPT_VERSION="5.7.3"       # peer dep of @hey-api/openapi-ts
OPC_VERSION="0.29.0"             # openapi-python-client (Python)
NODE_IMAGE="node:20-slim"
PYTHON_IMAGE="python:3.12-slim"

# ── Resolve repo root as a host path Docker understands ──────────────────────
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# On Git Bash / MSYS, translate /d/... -> D:/... for the bind mount.
if command -v cygpath >/dev/null 2>&1; then
  HOST_ROOT="$(cygpath -w "$ROOT")"
else
  HOST_ROOT="$ROOT"
fi

if [ ! -f "$ROOT/sdk/openapi.json" ]; then
  echo "ERROR: sdk/openapi.json not found. Run 'node scripts/generate-sdk.mjs' first." >&2
  exit 1
fi

echo "==> Generating TypeScript client (@hey-api/openapi-ts@${HEYAPI_VERSION})"
rm -rf "$ROOT/sdk/typescript"
MSYS_NO_PATHCONV=1 docker run --rm -v "${HOST_ROOT}:/w" -w /w "$NODE_IMAGE" sh -c "
  set -e
  mkdir -p /build && cd /build
  npm init -y >/dev/null 2>&1
  npm i -D @hey-api/openapi-ts@${HEYAPI_VERSION} typescript@${TYPESCRIPT_VERSION} >/dev/null 2>&1
  npx openapi-ts -i /w/sdk/openapi.json -o /w/sdk/typescript
"

echo "==> Generating Python client (openapi-python-client==${OPC_VERSION})"
rm -rf "$ROOT/sdk/python"
MSYS_NO_PATHCONV=1 docker run --rm -v "${HOST_ROOT}:/w" -w /w "$PYTHON_IMAGE" sh -c "
  set -e
  pip install --quiet --root-user-action=ignore openapi-python-client==${OPC_VERSION}
  openapi-python-client generate \
    --path sdk/openapi.json \
    --output-path sdk/python \
    --overwrite \
    --meta setup
"

# The Python generator runs ruff, which leaves a non-deterministic on-disk cache.
# It is not part of the client and must never be committed (it breaks the
# reproducibility check).
find "$ROOT/sdk/python" -name ".ruff_cache" -type d -prune -exec rm -rf {} + 2>/dev/null || true

if [ "$CHECK_ONLY" -eq 1 ]; then
  # Drift gate: the committed clients must match a fresh regeneration from the
  # committed sdk/openapi.json. If they differ, the API surface (or a generator
  # pin) changed without regenerating the SDK.
  if ! git -C "$ROOT" diff --quiet -- sdk/typescript sdk/python; then
    echo "" >&2
    echo "[generate-sdk-clients] DRIFT: sdk/typescript or sdk/python is stale." >&2
    echo "The API surface or a pinned generator changed without regenerating." >&2
    echo "Run:  bash scripts/generate-sdk-clients.sh" >&2
    git -C "$ROOT" --no-pager diff --stat -- sdk/typescript sdk/python >&2 || true
    exit 1
  fi
  echo "==> OK — sdk/typescript and sdk/python match sdk/openapi.json."
  exit 0
fi

echo "==> Done. Regenerated sdk/typescript and sdk/python."
