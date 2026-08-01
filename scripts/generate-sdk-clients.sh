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

# ── Staging ──────────────────────────────────────────────────────────────────
# Both generators need the network (npm i / pip install). Generating straight
# over sdk/ meant a transient outage did not leave the tree unchanged — it left
# the client *gone*: the `rm -rf` had already run, and 735 files were deleted by
# a DNS failure inside the container (issue #231).
#
# So generate into a staging directory and swap only once BOTH generators have
# succeeded. A failure now leaves sdk/ exactly as it was.
#
# The staging directory has to live inside the repo: the container only sees the
# bind mount at /w, so a host `mktemp -d` outside the repo would be invisible to
# it. It is removed on exit, success or failure.
STAGING_NAME=".sdk-staging"
STAGING="$ROOT/$STAGING_NAME"
cleanup_staging() {
  [ -d "$STAGING" ] || return 0
  rm -rf "$STAGING" 2>/dev/null && return 0
  # A generator that failed before the chown below leaves root-owned output the
  # host cannot remove. Without this fallback the promise that a failure leaves
  # the tree unchanged would be broken by the cleanup itself — an undeletable
  # .sdk-staging is exactly the kind of leftover that later reads as drift.
  MSYS_NO_PATHCONV=1 docker run --rm -v "${HOST_ROOT}:/w" "$PYTHON_IMAGE" \
    rm -rf "/w/${STAGING_NAME}" >/dev/null 2>&1 || true
}
trap cleanup_staging EXIT
rm -rf "$STAGING"
mkdir -p "$STAGING"

echo "==> Generating TypeScript client (@hey-api/openapi-ts@${HEYAPI_VERSION})"
MSYS_NO_PATHCONV=1 docker run --rm -v "${HOST_ROOT}:/w" -w /w "$NODE_IMAGE" sh -c "
  set -e
  mkdir -p /build && cd /build
  npm init -y >/dev/null 2>&1
  npm i -D @hey-api/openapi-ts@${HEYAPI_VERSION} typescript@${TYPESCRIPT_VERSION} >/dev/null 2>&1
  npx openapi-ts -i /w/sdk/openapi.json -o /w/${STAGING_NAME}/typescript
"

echo "==> Generating Python client (openapi-python-client==${OPC_VERSION})"
MSYS_NO_PATHCONV=1 docker run --rm -v "${HOST_ROOT}:/w" -w /w "$PYTHON_IMAGE" sh -c "
  set -e
  pip install --quiet --root-user-action=ignore openapi-python-client==${OPC_VERSION}
  openapi-python-client generate \
    --path sdk/openapi.json \
    --output-path ${STAGING_NAME}/python \
    --overwrite \
    --meta setup
"

# ── Hand the staging tree back to the invoking user ──────────────────────────
# Both generators run as root inside their container, so on Linux the staging
# tree comes back owned by root. That matters for the swap below and is easy to
# miss: moving a *directory* into a new parent needs write permission on the
# directory itself, because its `..` entry is rewritten. A root-owned
# `.sdk-staging/typescript` therefore cannot be `mv`d by an unprivileged user,
# and the swap fails with EACCES.
#
# Invisible on Windows — Docker Desktop ignores Unix ownership on bind mounts,
# so a local run succeeds either way. This only shows up on Linux CI.
#
# `chown` has to happen inside a container: the host user cannot chown files it
# does not own. Reuses an image already pulled above, so it costs no download.
MSYS_NO_PATHCONV=1 docker run --rm -v "${HOST_ROOT}:/w" -w /w "$PYTHON_IMAGE" \
  chown -R "$(id -u):$(id -g)" "/w/${STAGING_NAME}"

# The Python generator runs ruff, which leaves a non-deterministic on-disk cache.
# It is not part of the client and must never be committed (it breaks the
# reproducibility check). Stripped in staging, before anything is swapped in.
find "$STAGING/python" -name ".ruff_cache" -type d -prune -exec rm -rf {} + 2>/dev/null || true

# ── Swap ─────────────────────────────────────────────────────────────────────
# Past this line both generators have exited 0, so the destructive part runs
# only against material that already exists on disk. Both halves are swapped
# together: replacing one and not the other would leave the pair describing two
# different API surfaces.
for client in typescript python; do
  if [ ! -d "$STAGING/$client" ]; then
    echo "ERROR: generator reported success but produced no $STAGING_NAME/$client" >&2
    exit 1
  fi
done
for client in typescript python; do
  rm -rf "$ROOT/sdk/$client"
  mv "$STAGING/$client" "$ROOT/sdk/$client"
done

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
