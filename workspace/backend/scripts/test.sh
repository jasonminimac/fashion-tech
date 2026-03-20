#!/usr/bin/env bash
# test.sh — Run the full test suite with pytest
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${PROJECT_ROOT}"

# Use test environment
export ENVIRONMENT=test
export DATABASE_URL="${TEST_DATABASE_URL:-postgresql+asyncpg://developer:dev_password_123@localhost:5432/fashion_tech_test}"

echo "→ Running tests…"
python -m pytest \
  tests/ \
  --asyncio-mode=auto \
  --tb=short \
  -v \
  --cov=src/app \
  --cov-report=term-missing \
  --cov-report=xml:coverage.xml \
  "$@"

echo "✓ Tests complete."
