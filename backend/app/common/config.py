"""Application configuration.

All environment-specific values are read from the environment (or a local
`.env` file) rather than being hardcoded. See ARCHITECTURE.md section 41 and
`.env.example` for the full list.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings for the CareerIQ API."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "careeriq-api"
    app_version: str = "0.1.0"
    app_env: str = "development"
    debug: bool = False

    # postgresql+psycopg://... — the driver must be async-capable.
    database_url: str = "postgresql+psycopg://careeriq:careeriq@localhost:5432/careeriq"
    database_echo: bool = False

    # Browser origins allowed to call the API directly.
    cors_allow_origins: list[str] = ["http://localhost:3000"]

    log_level: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    """Return the cached settings instance."""
    return Settings()
