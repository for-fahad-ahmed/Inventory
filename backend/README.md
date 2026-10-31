# Inventory Backend

FastAPI + SQLAlchemy inventory management API.

## Requirements
- Python 3.14 (uv will fetch it automatically)
- [uv](https://docs.astral.sh/uv/)
- A running database (see `DATABASE_URL`)

## Setup
```bash
git clone https://github.com/for-fahad-ahmed/Inventory
cd Inventory/backend
uv sync
cp .env.example .env
```

Edit `.env` and set your values. Generate a secret key with:
```bash
openssl rand -hex 32
```

## Initialise the database
```bash
uv run python -m backend.init_db       # create tables
uv run python -m backend.create_owner  # create the first owner account
```

## Run
```bash
uv run uvicorn backend.main:app --reload
```
API at http://localhost:8000, interactive docs at http://localhost:8000/docs.

## Project layout
- `src/backend/routers/`: API endpoints
- `models.py`, `schemas.py`: DB models and request/response schemas
- `stock.py`: stock movement logic
