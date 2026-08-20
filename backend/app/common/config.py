"""Application configuration.

All environment-specific values are read from the environment (or a local
`.env` file) rather than being hardcoded. See ARCHITECTURE.md section 41 and
`.env.example` for the full list.
"""

from functools import lru_cache

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

JWT_SECRET_MIN_LENGTH = 32


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

    database_url: str = "postgresql+psycopg://careeriq:careeriq@localhost:5432/careeriq"
    database_echo: bool = False

    cors_allow_origins: list[str] = ["http://localhost:3000"]

    jwt_secret: SecretStr
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = Field(default=15, gt=0)

    log_level: str = "INFO"

    @field_validator("jwt_secret")
    @classmethod
    def _reject_weak_secret(cls, value: SecretStr) -> SecretStr:
        """Refuse a signing key too short to be safe for HMAC-SHA256."""
        if len(value.get_secret_value()) < JWT_SECRET_MIN_LENGTH:
            raise ValueError(
                f"JWT_SECRET must be at least {JWT_SECRET_MIN_LENGTH} characters"
            )
        return value


@lru_cache
def get_settings() -> Settings:
    """Return the cached settings instance."""
    return Settings()
