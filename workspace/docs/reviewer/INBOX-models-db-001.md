# INBOX-models-db-001

**Task ID:** models-db-001  
**Agent Role:** Backend Models & Database Agent  
**Status:** ✅ Complete

---

## Files Produced

### New files created:
- `backend/src/app/models/retailer.py` — RetailerAPIAccess model (B2B consent + readable_fields)
- `backend/src/app/models/__init__.py` — Exports all 12 models + Base
- `backend/src/app/database/__init__.py` — Re-exports engine, SessionLocal, get_db
- `backend/alembic.ini` — Alembic config (DATABASE_URL from env)
- `backend/alembic/env.py` — Alembic env with proper sys.path bootstrap
- `backend/alembic/script.py.mako` — Migration template
- `backend/alembic/versions/001_initial_schema.py` — Creates all 12 tables
- `backend/alembic/versions/002_create_indices.py` — Performance indexes (composite, partial)
- `backend/alembic/versions/003_add_constraints.py` — CHECK constraints on enums + ranges
- `backend/scripts/seed_garments.py` — Seeds 10 garments (3 structured, 4 draped, 3 stretch) + 2 users
- `backend/scripts/init_db.sh` — Runs alembic upgrade head then seed script
- `backend/tests/test_models.py` — 24 tests, all passing

### Fixed in existing files:
- `backend/src/app/models/garment.py` — Fixed self-referential `GarmentCategory.children` relationship (was using Python built-in `id` instead of column `id`)

---

## Summary

All 5 ORM models + base model are implemented. 12 tables total registered with SQLAlchemy metadata. Alembic migration chain (001 → 002 → 003) is ready to run against PostgreSQL. Seed script inserts idempotently (skips if SKU/email already exists).

**Test results:** 24/24 passing (SQLite in-memory, bypasses the global conftest mock of `create_engine`).

---

## Uncertainties / Notes for Reviewer

1. **GarmentCategory self-referential fix:** The existing `garment.py` had `remote_side=[id]` referencing Python's built-in `id()`. Fixed to use string-based `remote_side="GarmentCategory.id"` with explicit `foreign_keys=[parent_id]`. This is a bug in the pre-existing code.

2. **Alembic not yet run against live DB:** Migrations are written and syntactically correct but haven't been applied to a running PostgreSQL instance (no DB was running in this environment). The `init_db.sh` script handles this.

3. **RetailPartner is defined in garment.py:** The spec lists it separately, but it was pre-existing in `garment.py`. The new `retailer.py` adds only `RetailerAPIAccess`. Both are exported from `__init__.py`.

4. **Server defaults vs Python defaults:** Some model columns use `server_default` only (applied at INSERT, not on Python instantiation). Tests accommodate this by using `in (value, None)` assertions for instantiation-only tests.
