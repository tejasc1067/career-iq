# CareerIQ

AI-powered career intelligence platform. Local-first, privacy-first, free to run.

This repository currently contains the **project foundation only**. No product
features are implemented yet.

## Specifications

| Document | Owns |
|---|---|
| [CLAUDE.md](CLAUDE.md) | Working agreements and project rules |
| [PRODUCT.md](PRODUCT.md) | What CareerIQ does |
| [DESIGN.md](DESIGN.md) | How CareerIQ looks — design tokens are derived from here |
| [ARCHITECTURE.md](ARCHITECTURE.md) | How CareerIQ is built |

## Layout

```text
frontend/   Next.js frontend (TypeScript, Tailwind CSS, shadcn/ui)
backend/    FastAPI backend (Pydantic, SQLAlchemy, Alembic)
docs/       Design notes, API docs, schema docs, decision records
scripts/    Development scripts
```

## Prerequisites

Node.js 20+, Python 3.12+, Docker.

## 1. Start PostgreSQL + pgvector

```bash
cp .env.example .env
docker compose up -d --wait
docker compose ps
```

Stop it with `docker compose down`, or `docker compose down -v` to also discard
the data volume.

## 2. Run the backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env

alembic upgrade head                  # enables the pgvector extension
uvicorn app.main:app --reload
```

- API: <http://localhost:8000>
- Interactive docs: <http://localhost:8000/docs>
- Liveness: <http://localhost:8000/health>
- Readiness (checks the database): <http://localhost:8000/health/ready>

## 3. Run the frontend

```bash
cd frontend
cp .env.example .env.local
npm install
npm run dev
```

Open <http://localhost:3000>. The page confirms the frontend is running and
reports whether the API is reachable.

## Tests

```bash
cd backend && .venv/bin/pytest     # backend
cd frontend && npm test            # frontend
```

Lint and type-check:

```bash
cd backend && .venv/bin/ruff check .
cd frontend && npm run lint && npx tsc --noEmit
```

## Migrations

Alembic owns the schema (ARCHITECTURE.md section 38). The database URL comes
from the application settings, so `alembic.ini` holds no credentials.

```bash
cd backend
alembic revision --autogenerate -m "add resumes table"
alembic upgrade head
alembic downgrade -1
```

## Conventions

- Never hardcode a colour in a component. Design tokens live in
  `frontend/app/globals.css` and come from `DESIGN.md`.
- Never commit a real secret. Every `.env.example` holds placeholders only.
- The backend owns business logic; the frontend displays results
  (ARCHITECTURE.md section 55).
