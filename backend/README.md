# Inventory Backend

REST API for inventory management, built with FastAPI, SQLAlchemy and PostgreSQL.
Covers products, categories, suppliers, customers, purchases, sales, stock
tracking and role-based users with JWT authentication.

## Requirements

- [uv](https://docs.astral.sh/uv/) (installs the correct Python version automatically)
- A running PostgreSQL database

## Setup

```bash
git clone https://github.com/for-fahad-ahmed/Inventory
cd Inventory/backend
uv sync
cp .env.example .env
```

Edit `.env` and fill in your values:

| Variable | Description |
|---|---|
| `SECRET_KEY` | Secret used to sign JWT tokens. Generate one with `openssl rand -hex 32` |
| `DATABASE_URL` | PostgreSQL connection string, e.g. `postgresql+psycopg://user:password@localhost:5432/inventory` |

Both are required. The app will not start without them.

### Database

Create an empty PostgreSQL database and point `DATABASE_URL` at it.

## Initialise

Create the tables, then create the first owner account (you will be prompted
for username, name, email, phone and password):

```bash
uv run python -m backend.init_db
uv run python -m backend.create_owner
```

Further users are created through the API by the owner.

## Run

```bash
uv run uvicorn backend.main:app --reload
```

- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs

Run all commands from the `backend/` directory.

## Project layout

```
backend/
├── pyproject.toml
├── uv.lock
├── .env.example
└── src/backend/
    ├── main.py          # app entry point, CORS, router registration
    ├── config.py        # JWT settings
    ├── database.py      # engine, session, Base
    ├── models.py        # SQLAlchemy models
    ├── schemas.py       # Pydantic request/response schemas
    ├── security.py      # token creation
    ├── dependencies.py  # auth and role dependencies
    ├── stock.py         # stock movement logic
    ├── init_db.py       # creates tables
    ├── create_owner.py  # creates the first owner account
    └── routers/         # API endpoints
```

## Notes

- CORS currently allows `http://localhost:5173` and `http://localhost:8080`.
  Edit `origins` in `src/backend/main.py` to change this.
- Tables are created with `create_all`, which does not alter existing tables.
  Schema changes need a manual migration or a fresh database for now.
