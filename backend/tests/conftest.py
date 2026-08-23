"""Shared test fixtures."""

from collections.abc import AsyncIterator
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool

from app.common.config import get_settings
from app.database.session import get_session
from app.main import app
from app.users.models import User


@pytest.fixture
async def client() -> AsyncIterator[AsyncClient]:
    """An HTTP client bound to the ASGI app, with no network involved."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest.fixture
async def db_session() -> AsyncIterator[AsyncSession]:
    """A session on the migrated database, rolled back so nothing persists.

    Requires `alembic upgrade head` to have run. Testing against the migrated
    schema rather than metadata.create_all also proves the migration matches
    the model.

    Rows left by local development are removed inside the test transaction so
    every test starts from an empty table; the rollback restores them.
    """
    engine = create_async_engine(get_settings().database_url, poolclass=NullPool)
    async with engine.connect() as connection:
        transaction = await connection.begin()
        await connection.execute(delete(User))
        session = AsyncSession(
            bind=connection,
            expire_on_commit=False,
            join_transaction_mode="create_savepoint",
        )
        try:
            yield session
        finally:
            await session.close()
            if transaction.is_active:
                await transaction.rollback()
    await engine.dispose()


@pytest.fixture
async def api_client(db_session: AsyncSession) -> AsyncIterator[AsyncClient]:
    """An HTTP client whose handlers use the rolled-back test session."""
    app.dependency_overrides[get_session] = lambda: db_session
    transport = ASGITransport(app=app)
    try:
        async with AsyncClient(transport=transport, base_url="http://test") as c:
            yield c
    finally:
        app.dependency_overrides.pop(get_session, None)


@pytest.fixture(autouse=True)
def storage_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Point resume storage at a temporary directory for every test."""
    monkeypatch.setenv("RESUME_STORAGE_DIR", str(tmp_path))
    get_settings.cache_clear()
    yield tmp_path
    get_settings.cache_clear()
