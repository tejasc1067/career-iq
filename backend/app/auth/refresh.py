"""Refresh token generation, hashing, and rotation."""

import hashlib
import secrets
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import RefreshToken
from app.common.config import Settings, get_settings

REFRESH_TOKEN_BYTES = 32


class RefreshTokenError(Exception):
    """Base class for refresh token failures."""


class RefreshTokenNotFoundError(RefreshTokenError):
    """No stored token matches the presented value."""


class RefreshTokenExpiredError(RefreshTokenError):
    """The presented token is past its expiry."""


class RefreshTokenReuseError(RefreshTokenError):
    """A revoked token was presented and its family has been revoked."""


@dataclass(frozen=True)
class IssuedRefreshToken:
    """A newly issued token and its persisted record."""

    raw_token: str
    record: RefreshToken


def generate_refresh_token() -> str:
    """Return a new opaque refresh token."""
    return secrets.token_urlsafe(REFRESH_TOKEN_BYTES)


def hash_refresh_token(token: str) -> str:
    """Return the stored form of an opaque refresh token."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


async def issue_refresh_token(
    session: AsyncSession,
    user_id: uuid.UUID,
    *,
    family_id: uuid.UUID | None = None,
    settings: Settings | None = None,
) -> IssuedRefreshToken:
    """Persist a new refresh token and return its raw value."""
    settings = settings or get_settings()
    raw_token = generate_refresh_token()
    record = RefreshToken(
        user_id=user_id,
        token_hash=hash_refresh_token(raw_token),
        family_id=family_id or uuid.uuid4(),
        expires_at=datetime.now(UTC)
        + timedelta(days=settings.refresh_token_expire_days),
    )
    session.add(record)
    await session.flush()
    return IssuedRefreshToken(raw_token=raw_token, record=record)


async def revoke_refresh_token_family(
    session: AsyncSession, family_id: uuid.UUID, *, at: datetime | None = None
) -> int:
    """Revoke every unrevoked token in a family and return how many changed."""
    result = await session.execute(
        update(RefreshToken)
        .where(
            RefreshToken.family_id == family_id,
            RefreshToken.revoked_at.is_(None),
        )
        .values(revoked_at=at or datetime.now(UTC))
    )
    return result.rowcount


async def rotate_refresh_token(
    session: AsyncSession, raw_token: str, *, settings: Settings | None = None
) -> IssuedRefreshToken:
    """Consume a refresh token exactly once and return its replacement."""
    record = await session.scalar(
        select(RefreshToken)
        .where(RefreshToken.token_hash == hash_refresh_token(raw_token))
        .with_for_update()
    )
    if record is None:
        raise RefreshTokenNotFoundError

    now = datetime.now(UTC)
    if record.revoked_at is not None:
        await revoke_refresh_token_family(session, record.family_id, at=now)
        raise RefreshTokenReuseError
    if record.expires_at <= now:
        await revoke_refresh_token_family(session, record.family_id, at=now)
        raise RefreshTokenExpiredError

    record.revoked_at = now
    await session.flush()
    return await issue_refresh_token(
        session, record.user_id, family_id=record.family_id, settings=settings
    )
