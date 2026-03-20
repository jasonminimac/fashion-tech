#!/usr/bin/env bash
# migrate.sh — Run Alembic database migrations
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${PROJECT_ROOT}"

# Load .env.local if present
if [ -f ".env.local" ]; then
  export $(grep -v '^#' .env.local | xargs)
fi

echo "→ Running Alembic migrations…"
python -m alembic upgrade head
echo "✓ Migrations complete."
