# CareerIQ API

FastAPI backend for CareerIQ. See the repository root `README.md` for full
setup instructions.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env

alembic upgrade head                    # requires PostgreSQL to be running
uvicorn app.main:app --reload           # http://localhost:8000
pytest
ruff check .
```

Interactive API docs: <http://localhost:8000/docs>

## Layout

`app/` is organised by domain (`resumes/`, `career/`, `jobs/`, …) per
ARCHITECTURE.md section 7. The domain packages are placeholders; only
`app/common/` and `app/database/` contain code so far.
