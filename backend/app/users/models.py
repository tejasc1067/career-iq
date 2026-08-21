"""User ORM models."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base

CURRENT_ROLE_MAX_LENGTH = 120
CAREER_LEVEL_MAX_LENGTH = 80
YEARS_OF_EXPERIENCE_MAX = 70


class User(Base):
    """An authenticated CareerIQ account.

    Only the password hash is stored; plaintext passwords are never persisted.
    """

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class UserProfile(Base):
    """The career details a user states about themselves.

    One row per user, created the first time the profile is saved. Every value
    is user-supplied and authoritative for later analysis, per PRODUCT.md
    section 28; nothing here is inferred.
    """

    __tablename__ = "user_profiles"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        index=True,
    )
    current_role: Mapped[str | None] = mapped_column(
        String(CURRENT_ROLE_MAX_LENGTH), nullable=True
    )
    career_level: Mapped[str | None] = mapped_column(
        String(CAREER_LEVEL_MAX_LENGTH), nullable=True
    )
    years_of_experience: Mapped[float | None] = mapped_column(
        Numeric(3, 1, asdecimal=False), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
