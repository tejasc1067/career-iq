# CareerIQ

AI-powered career intelligence platform. Local-first, privacy-first, free to run.

Current state: project foundation plus **authentication** (signup, login, token
refresh, logout). No career, resume, or job features yet.

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

- **Node.js 22+** — `jsdom` declares `>=22.22.2`, and CI runs Node 22
- **Python 3.12+**
- **Docker** — for PostgreSQL

## Running locally

Docker Compose provides **PostgreSQL only**. The frontend and backend run
directly on the host for faster iteration (ARCHITECTURE.md section 42), so a
full local stack means three processes in three terminals.

### 1. Database

```bash
cp .env.example .env
docker compose up -d --wait
```

Starts PostgreSQL 17 with pgvector on port 5432. Stop with `docker compose down`,
or `docker compose down -v` to also discard the data volume.

### 2. Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
```

`JWT_SECRET` is **required and has no default**. The application refuses to start
without it, and rejects any value shorter than 32 characters. Generate one:

```bash
openssl rand -hex 32
```

Then apply the migrations and start the server:

```bash
alembic upgrade head        # pgvector extension, users, refresh_tokens
uvicorn app.main:app --reload
```

| | |
|---|---|
| API | <http://localhost:8000> |
| Interactive docs | <http://localhost:8000/docs> |
| Liveness | <http://localhost:8000/health> |
| Readiness (checks the database) | <http://localhost:8000/health/ready> |

Authentication endpoints:

```text
POST /api/auth/signup     Create an account
POST /api/auth/login      Credentials for an access token + refresh cookie
POST /api/auth/refresh    Rotate the refresh cookie, get a new access token
POST /api/auth/logout     Revoke the refresh token and clear the cookie
```

### 3. Frontend

```bash
cd frontend
cp .env.example .env.local
npm install
npm run dev
```

Open <http://localhost:3000>. The home page reports whether the API is reachable
and whether you have an active session. Sign in at
<http://localhost:3000/login>.

### Try the login flow

There is no signup screen yet, so create an account through the API:

```bash
curl -X POST http://localhost:8000/api/auth/signup \
  -H 'Content-Type: application/json' \
  -d '{"email":"you@example.com","password":"a password of at least 8 characters"}'
```

Then sign in at <http://localhost:3000/login>. On success the home page shows
"Signed in" and offers a sign-out action.

The access token lives in browser memory only and lasts 15 minutes. The refresh
token is an `HttpOnly` cookie that JavaScript cannot read; reloading the page
restores the session from it.

## Tests

```bash
cd backend && .venv/bin/pytest     # requires the database to be running and migrated
cd frontend && npm test
```

Lint and type-check:

```bash
cd backend && .venv/bin/ruff check . && .venv/bin/ruff format --check .
cd frontend && npm run lint && npx tsc --noEmit
```

The backend suite runs against the real migrated database and rolls every test
back, so it leaves no rows behind. Run `alembic upgrade head` first.

## Migrations

Alembic owns the schema (ARCHITECTURE.md section 38). The database URL comes
from the application settings, so `alembic.ini` holds no credentials.

```bash
cd backend
alembic revision --autogenerate -m "add resumes table"
alembic upgrade head
alembic downgrade -1
alembic check               # fails if a model has drifted from the migrations
```

## Conventions

- Never hardcode a colour in a component. Design tokens live in
  `frontend/app/globals.css` and come from `DESIGN.md`.
- Never commit a real secret. Every `.env.example` holds placeholders only.
- The backend owns business logic; the frontend displays results
  (ARCHITECTURE.md section 55).
