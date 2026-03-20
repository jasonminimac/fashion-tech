#!/usr/bin/env bash
# run.sh — Start the FastAPI development/production server
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${PROJECT_ROOT}"

# Load .env.local if present
if [ -f ".env.local" ]; then
  export $(grep -v '^#' .env.local | xargs)
fi

HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8000}"
WORKERS="${WORKERS:-1}"
ENVIRONMENT="${ENVIRONMENT:-development}"

if [ "${ENVIRONMENT}" = "production" ]; then
  echo "→ Starting production server (workers=${WORKERS})…"
  exec python -m uvicorn app.main:app \
    --host "${HOST}" \
    --port "${PORT}" \
    --workers "${WORKERS}" \
    --no-access-log
else
  echo "→ Starting development server with reload…"
  exec python -m uvicorn app.main:app \
    --host "${HOST}" \
    --port "${PORT}" \
    --reload \
    --log-level debug
fi
