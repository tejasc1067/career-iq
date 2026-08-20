"""Tests for the operational health endpoints."""

from httpx import AsyncClient
from sqlalchemy.exc import OperationalError

from app.common.config import get_settings
from app.database.session import get_session
from app.main import app


async def test_health_reports_service_metadata(client: AsyncClient) -> None:
    """Liveness answers without touching any dependency."""
    response = await client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": get_settings().app_name,
        "version": get_settings().app_version,
    }


async def test_readiness_reports_ok_when_the_database_answers(
    client: AsyncClient,
) -> None:
    """Readiness succeeds when the session executes a statement."""

    class StubSession:
        async def execute(self, _statement: object) -> None:
            return None

    app.dependency_overrides[get_session] = lambda: StubSession()
    try:
        response = await client.get("/health/ready")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "ok"}


async def test_readiness_reports_503_when_the_database_is_unreachable(
    client: AsyncClient,
) -> None:
    """Readiness must fail loudly rather than claim the API is usable."""

    class BrokenSession:
        async def execute(self, _statement: object) -> None:
            raise OperationalError("SELECT 1", None, Exception("refused"))

    app.dependency_overrides[get_session] = lambda: BrokenSession()
    try:
        response = await client.get("/health/ready")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 503
    assert response.json() == {"status": "unavailable", "database": "unreachable"}
