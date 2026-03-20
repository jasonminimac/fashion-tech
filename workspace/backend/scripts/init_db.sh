#!/usr/bin/env bash
# init_db.sh — Run Alembic migrations and seed test data.
#
# Usage:
#   ./scripts/init_db.sh
#
# Reads DATABASE_URL from environment or .env.local.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_ROOT="$(dirname "$SCRIPT_DIR")"

# ---------------------------------------------------------------------------
# Load .env.local if present
# ---------------------------------------------------------------------------
ENV_FILE="$BACKEND_ROOT/.env.local"
if [[ -f "$ENV_FILE" ]]; then
  echo "📄 Loading environment from .env.local"
  # Export each line that is a valid KEY=VALUE pair (ignore comments)
  set -o allexport
  # shellcheck source=/dev/null
  source "$ENV_FILE"
  set +o allexport
fi

: "${DATABASE_URL:?DATABASE_URL is not set. Copy .env.example to .env.local and fill it in.}"

echo ""
echo "🛠  Fashion Tech — Database Init"
echo "   DB: ${DATABASE_URL##*@}"  # hide credentials

# ---------------------------------------------------------------------------
# Ensure we're running from the backend root so alembic.ini is found
# ---------------------------------------------------------------------------
cd "$BACKEND_ROOT"

# ---------------------------------------------------------------------------
# Check alembic is available
# ---------------------------------------------------------------------------
if ! command -v alembic &>/dev/null; then
  if command -v poetry &>/dev/null; then
    ALEMBIC="poetry run alembic"
  else
    echo "❌ alembic not found. Run: pip install alembic  (or: poetry install)"
    exit 1
  fi
else
  ALEMBIC="alembic"
fi

SEED_CMD="python scripts/seed_garments.py"
if command -v poetry &>/dev/null; then
  SEED_CMD="poetry run python scripts/seed_garments.py"
fi

# ---------------------------------------------------------------------------
# Run migrations
# ---------------------------------------------------------------------------
echo ""
echo "▶  Running Alembic migrations…"
$ALEMBIC upgrade head
echo "✅ Migrations complete."

# ---------------------------------------------------------------------------
# Seed data
# ---------------------------------------------------------------------------
echo ""
echo "▶  Seeding test data…"
$SEED_CMD
echo "✅ Seed complete."

echo ""
echo "🎉 Database ready."
