"""User API schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_LENGTH = 128


def normalize_email(email: str) -> str:
    """Return the canonical stored form of an email address."""
    return email.strip().lower()


class UserCreate(BaseModel):
    """Signup request."""

    email: EmailStr
    password: str = Field(
        min_length=PASSWORD_MIN_LENGTH, max_length=PASSWORD_MAX_LENGTH
    )

    @field_validator("email", mode="before")
    @classmethod
    def _normalize_email(cls, value: object) -> object:
        """Normalize before validation so surrounding whitespace is not an error."""
        return normalize_email(value) if isinstance(value, str) else value


class UserRead(BaseModel):
    """A user as returned by the API. Deliberately excludes password_hash."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    created_at: datetime
    updated_at: datetime
