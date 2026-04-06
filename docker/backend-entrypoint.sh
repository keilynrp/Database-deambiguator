#!/bin/sh
set -eu

if [ "${RUN_DB_MIGRATIONS_ON_START:-1}" = "1" ]; then
  alembic upgrade head
fi

exec uvicorn backend.main:app --host 0.0.0.0 --port "${PORT:-8000}"
