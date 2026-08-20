"""Operational health endpoints.

`/health` is a liveness probe: it answers as long as the process is serving
requests and deliberately touches no dependencies.

`/health/ready` is a readiness probe: it verifies the database is reachable and
returns 503 when it is not, so a caller can distinguish "the API is up" from
"the API can do useful work".
"""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.config import Settings, get_settings
from app.database.session import get_session

logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])

# Annotated dependencies rather than call-in-default, so the signatures stay
# lint-clean and match current FastAPI guidance.
SettingsDep = Annotated[Settings, Depends(get_settings)]
SessionDep = Annotated[AsyncSession, Depends(get_session)]


class Health(BaseModel):
    """Liveness response."""

    status: str
    service: str
    version: str


class Readiness(BaseModel):
    """Readiness response, including the state of each checked dependency."""

    status: str
    database: str


@router.get("/health", response_model=Health)
async def health(settings: SettingsDep) -> Health:
    """Report that the API process is serving requests."""
    return Health(
        status="ok",
        service=settings.app_name,
        version=settings.app_version,
    )


@router.get("/health/ready", response_model=Readiness)
async def readiness(response: Response, session: SessionDep) -> Readiness:
    """Report whether the API's dependencies are usable."""
    try:
        await session.execute(text("SELECT 1"))
    except SQLAlchemyError:
        # Log the failure without echoing connection details to the caller.
        logger.warning("Readiness check failed: database unreachable")
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return Readiness(status="unavailable", database="unreachable")

    return Readiness(status="ok", database="ok")
