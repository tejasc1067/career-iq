"""Tests for the User model and its API schema."""

import uuid
from datetime import UTC, datetime

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.users.models import User
from app.users.schemas import UserRead

FAKE_HASH = "not-a-real-hash"


async def test_user_is_created_with_generated_id_and_timestamps(
    db_session: AsyncSession,
) -> None:
    """A new user gets a UUID id and server-set timestamps."""
    user = User(email="first@example.com", password_hash=FAKE_HASH)
    db_session.add(user)
    await db_session.flush()

    assert isinstance(user.id, uuid.UUID)
    assert user.created_at is not None
    assert user.updated_at is not None


async def test_user_persists_and_reloads(db_session: AsyncSession) -> None:
    """A flushed user is readable back from the database."""
    user = User(email="persisted@example.com", password_hash=FAKE_HASH)
    db_session.add(user)
    await db_session.flush()
    db_session.expunge_all()

    loaded = await db_session.scalar(
        select(User).where(User.email == "persisted@example.com")
    )

    assert loaded is not None
    assert loaded.id == user.id
    assert loaded.password_hash == FAKE_HASH


async def test_duplicate_email_is_rejected(db_session: AsyncSession) -> None:
    """The unique index on email is enforced by the database."""
    db_session.add(User(email="dupe@example.com", password_hash=FAKE_HASH))
    await db_session.flush()

    db_session.add(User(email="dupe@example.com", password_hash=FAKE_HASH))
    with pytest.raises(IntegrityError):
        await db_session.flush()


def test_read_schema_never_exposes_the_password_hash() -> None:
    """UserRead must drop password_hash even when built from a User object."""
    assert "password_hash" not in UserRead.model_fields

    now = datetime.now(UTC)
    user = User(
        id=uuid.uuid4(),
        email="read@example.com",
        password_hash=FAKE_HASH,
        created_at=now,
        updated_at=now,
    )

    dumped = UserRead.model_validate(user).model_dump()

    assert set(dumped) == {"id", "email", "created_at", "updated_at"}
    assert FAKE_HASH not in str(dumped)
