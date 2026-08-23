"""FastAPI application entrypoint.

Domain routers are mounted here as each domain is implemented.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.auth.router import router as auth_router
from app.common.config import get_settings
from app.common.errors import register_error_handlers
from app.common.health import router as health_router
from app.common.logging import configure_logging
from app.resumes.router import router as resumes_router
from app.users.router import router as users_router

settings = get_settings()
configure_logging(settings.log_level)

app = FastAPI(
    title="CareerIQ API",
    version=settings.app_version,
    debug=settings.debug,
)

register_error_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(resumes_router)
