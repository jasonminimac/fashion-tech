# Fashion Tech API

FastAPI skeleton for the virtual try-on platform.

## Requirements

- Python 3.11+
- PostgreSQL (optional for Sprint 1 stubs)

## Setup

```bash
cd apps/api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run locally

```bash
# Optional: set DB URL
export DATABASE_URL="postgresql://localhost/fashiontech"

uvicorn main:app --reload --port 8000
```

## Endpoints

| Method | Path        | Description                    |
|--------|-------------|--------------------------------|
| GET    | `/health`   | Health check                   |
| POST   | `/scan`     | Submit a body scan (stub)      |
| GET    | `/garments` | List garments (stub)           |

## OpenAPI docs

Visit [http://localhost:8000/docs](http://localhost:8000/docs) after starting the server.

## Notes

- `db/connection.py` is a stub — real async SQLAlchemy wiring comes in Sprint 2.
- All endpoints return fixed stub data for now.
