"""FastAPI application entrypoint.

Domain routers are mounted here as each domain is implemented. Only the
operational health router exists at this stage.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.common.config import get_settings
from app.common.health import router as health_router
from app.common.logging import configure_logging

settings = get_settings()
configure_logging(settings.log_level)

app = FastAPI(
    title="CareerIQ API",
    version=settings.app_version,
    debug=settings.debug,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
