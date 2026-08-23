"""User API schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.users.models import (
    CAREER_LEVEL_MAX_LENGTH,
    CURRENT_ROLE_MAX_LENGTH,
    YEARS_OF_EXPERIENCE_MAX,
)

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


class UserProfileUpdate(BaseModel):
    """A full replacement of the signed-in user's profile.

    Extra keys are rejected rather than ignored: a payload carrying `user_id`
    is a client trying to name an owner, and that is an error, not a value to
    quietly drop.
    """

    model_config = ConfigDict(extra="forbid")

    current_role: str | None = Field(default=None, max_length=CURRENT_ROLE_MAX_LENGTH)
    career_level: str | None = Field(default=None, max_length=CAREER_LEVEL_MAX_LENGTH)
    years_of_experience: float | None = Field(
        default=None, ge=0, le=YEARS_OF_EXPERIENCE_MAX
    )

    @field_validator("current_role", "career_level", mode="before")
    @classmethod
    def _blank_to_none(cls, value: object) -> object:
        """Store a cleared text field as absent rather than as an empty string."""
        if isinstance(value, str):
            return value.strip() or None
        return value


class UserProfileRead(BaseModel):
    """A user's stated career details. Every field is empty until first saved."""

    model_config = ConfigDict(from_attributes=True)

    current_role: str | None = None
    career_level: str | None = None
    years_of_experience: float | None = None
    updated_at: datetime | None = None


class CurrentUserRead(UserRead):
    """The signed-in account together with its profile."""

    profile: UserProfileRead
