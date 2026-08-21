"""Tests for the refresh-token lifecycle."""

import asyncio
import uuid
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import delete, func, select, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.auth.models import RefreshToken
from app.auth.refresh import (
    REFRESH_TOKEN_BYTES,
    RefreshTokenExpiredError,
    RefreshTokenNotFoundError,
    RefreshTokenReuseError,
    generate_refresh_token,
    hash_refresh_token,
    issue_refresh_token,
    revoke_refresh_token_family,
    rotate_refresh_token,
)
from app.common.config import get_settings
from app.users.models import User


async def _user(session: AsyncSession, email: str = "owner@example.com") -> User:
    user = User(email=email, password_hash="not-a-real-hash")
    session.add(user)
    await session.flush()
    return user


def test_generated_token_carries_the_expected_entropy() -> None:
    """token_urlsafe(32) yields 256 bits, encoded as at least 43 characters."""
    token = generate_refresh_token()

    assert REFRESH_TOKEN_BYTES == 32
    assert len(token) >= 43
    assert token.strip() == token


def test_generated_tokens_are_unique() -> None:
    """A CSPRNG source produces no repeats across many draws."""
    tokens = {generate_refresh_token() for _ in range(1000)}

    assert len(tokens) == 1000


def test_token_is_not_a_bare_uuid() -> None:
    """The raw token must not be a UUID4 string."""
    token = generate_refresh_token()

    with pytest.raises(ValueError):
        uuid.UUID(token)


def test_hash_is_deterministic_and_differs_from_the_raw_token() -> None:
    """Hashing is repeatable, and the digest is not the token."""
    token = generate_refresh_token()

    assert hash_refresh_token(token) == hash_refresh_token(token)
    assert hash_refresh_token(token) != token
    assert token not in hash_refresh_token(token)


async def test_issue_persists_only_the_hash(db_session: AsyncSession) -> None:
    """Creation stores the digest of the raw token, never the token."""
    user = await _user(db_session)

    issued = await issue_refresh_token(db_session, user.id)

    assert issued.record.token_hash == hash_refresh_token(issued.raw_token)
    assert issued.record.token_hash != issued.raw_token
    row = (
        (await db_session.execute(text("SELECT * FROM refresh_tokens")))
        .mappings()
        .one()
    )
    assert issued.raw_token not in " ".join(str(v) for v in row.values())


async def test_issue_sets_user_family_expiry_and_leaves_revoked_null(
    db_session: AsyncSession,
) -> None:
    """A new token starts a new family with a 30-day expiry and no revocation."""
    user = await _user(db_session)
    before = datetime.now(UTC)

    issued = await issue_refresh_token(db_session, user.id)

    expected = timedelta(days=get_settings().refresh_token_expire_days)
    assert issued.record.user_id == user.id
    assert issued.record.revoked_at is None
    assert isinstance(issued.record.family_id, uuid.UUID)
    assert (
        expected
        <= issued.record.expires_at - before
        <= expected + timedelta(seconds=10)
    )


async def test_each_new_session_starts_its_own_family(
    db_session: AsyncSession,
) -> None:
    """Two independently issued tokens do not share a family."""
    user = await _user(db_session)

    first = await issue_refresh_token(db_session, user.id)
    second = await issue_refresh_token(db_session, user.id)

    assert first.record.family_id != second.record.family_id


async def test_raw_token_locates_its_record(db_session: AsyncSession) -> None:
    """The raw value can be hashed to find the stored row."""
    user = await _user(db_session)
    issued = await issue_refresh_token(db_session, user.id)

    found = await db_session.scalar(
        select(RefreshToken).where(
            RefreshToken.token_hash == hash_refresh_token(issued.raw_token)
        )
    )

    assert found is not None
    assert found.id == issued.record.id


async def test_rotation_replaces_the_token_and_preserves_identity(
    db_session: AsyncSession,
) -> None:
    """Rotation consumes the old token and issues a same-family replacement."""
    user = await _user(db_session)
    original = await issue_refresh_token(db_session, user.id)
    before = datetime.now(UTC)

    replacement = await rotate_refresh_token(db_session, original.raw_token)

    assert replacement.raw_token != original.raw_token
    assert replacement.record.token_hash != original.record.token_hash
    assert replacement.record.user_id == original.record.user_id
    assert replacement.record.family_id == original.record.family_id
    assert replacement.record.revoked_at is None
    assert original.record.revoked_at is not None

    expected = timedelta(days=get_settings().refresh_token_expire_days)
    assert (
        expected
        <= replacement.record.expires_at - before
        <= expected + timedelta(seconds=10)
    )
    assert replacement.record.expires_at > original.record.expires_at - timedelta(
        seconds=1
    )


async def test_rotated_token_cannot_be_rotated_again(
    db_session: AsyncSession,
) -> None:
    """One-time use: the consumed token is rejected as reuse."""
    user = await _user(db_session)
    original = await issue_refresh_token(db_session, user.id)
    await rotate_refresh_token(db_session, original.raw_token)

    with pytest.raises(RefreshTokenReuseError):
        await rotate_refresh_token(db_session, original.raw_token)


async def test_unknown_token_is_rejected(db_session: AsyncSession) -> None:
    """A token with no stored hash cannot rotate."""
    with pytest.raises(RefreshTokenNotFoundError):
        await rotate_refresh_token(db_session, generate_refresh_token())


async def test_expired_token_cannot_rotate(db_session: AsyncSession) -> None:
    """An expired token is rejected rather than silently accepted."""
    user = await _user(db_session)
    issued = await issue_refresh_token(db_session, user.id)
    issued.record.expires_at = datetime.now(UTC) - timedelta(seconds=1)
    await db_session.flush()

    with pytest.raises(RefreshTokenExpiredError):
        await rotate_refresh_token(db_session, issued.raw_token)

    assert await db_session.scalar(select(func.count()).select_from(RefreshToken)) == 1


async def test_reuse_revokes_the_whole_family(db_session: AsyncSession) -> None:
    """Replaying a consumed token revokes every token in its family."""
    user = await _user(db_session)
    first = await issue_refresh_token(db_session, user.id)
    second = await rotate_refresh_token(db_session, first.raw_token)
    third = await rotate_refresh_token(db_session, second.raw_token)
    family = first.record.family_id

    with pytest.raises(RefreshTokenReuseError):
        await rotate_refresh_token(db_session, first.raw_token)

    unrevoked = await db_session.scalar(
        select(func.count())
        .select_from(RefreshToken)
        .where(RefreshToken.family_id == family, RefreshToken.revoked_at.is_(None))
    )
    assert unrevoked == 0
    assert third.record.family_id == family


async def test_reuse_leaves_other_families_and_users_untouched(
    db_session: AsyncSession,
) -> None:
    """Family revocation is scoped to the compromised family only."""
    user = await _user(db_session)
    other_user = await _user(db_session, "other@example.com")
    compromised = await issue_refresh_token(db_session, user.id)
    await rotate_refresh_token(db_session, compromised.raw_token)
    same_user_other_family = await issue_refresh_token(db_session, user.id)
    other_user_token = await issue_refresh_token(db_session, other_user.id)

    with pytest.raises(RefreshTokenReuseError):
        await rotate_refresh_token(db_session, compromised.raw_token)

    db_session.expunge_all()
    survivors = (
        await db_session.scalars(
            select(RefreshToken.id).where(RefreshToken.revoked_at.is_(None))
        )
    ).all()

    assert set(survivors) == {
        same_user_other_family.record.id,
        other_user_token.record.id,
    }


async def test_revoke_family_reports_how_many_it_changed(
    db_session: AsyncSession,
) -> None:
    """Revoking a family is idempotent and counts only unrevoked rows."""
    user = await _user(db_session)
    issued = await issue_refresh_token(db_session, user.id)

    assert await revoke_refresh_token_family(db_session, issued.record.family_id) == 1
    assert await revoke_refresh_token_family(db_session, issued.record.family_id) == 0


def test_exceptions_carry_no_sensitive_detail() -> None:
    """Lifecycle exceptions must not embed token, hash, user, or family data."""
    for error in (
        RefreshTokenNotFoundError(),
        RefreshTokenExpiredError(),
        RefreshTokenReuseError(),
    ):
        assert error.args == ()
        assert str(error) == ""


async def test_concurrent_rotation_allows_exactly_one_winner() -> None:
    """Two transactions racing on the same token: one rotates, one is rejected.

    Uses two independent connections so `SELECT ... FOR UPDATE` genuinely
    serialises them, which the shared rollback fixture cannot express.
    """
    engine = create_async_engine(get_settings().database_url, poolclass=NullPool)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    user_id: uuid.UUID | None = None
    try:
        async with factory() as setup:
            user = User(email="racer@example.com", password_hash="not-a-real-hash")
            setup.add(user)
            await setup.flush()
            user_id = user.id
            issued = await issue_refresh_token(setup, user.id)
            raw_token = issued.raw_token
            family_id = issued.record.family_id
            await setup.commit()

        async def attempt() -> object:
            async with factory() as session:
                try:
                    result = await rotate_refresh_token(session, raw_token)
                    await session.commit()
                    return result
                except Exception as exc:
                    await session.commit()
                    return exc

        outcomes = await asyncio.gather(attempt(), attempt())

        successes = [o for o in outcomes if not isinstance(o, Exception)]
        failures = [o for o in outcomes if isinstance(o, Exception)]

        assert len(successes) == 1, outcomes
        assert len(failures) == 1
        assert isinstance(failures[0], RefreshTokenReuseError)

        async with factory() as check:
            consumed = await check.scalar(
                select(func.count())
                .select_from(RefreshToken)
                .where(
                    RefreshToken.token_hash == hash_refresh_token(raw_token),
                    RefreshToken.revoked_at.is_not(None),
                )
            )
            total = await check.scalar(
                select(func.count())
                .select_from(RefreshToken)
                .where(RefreshToken.family_id == family_id)
            )
        assert consumed == 1
        assert total == 2
    finally:
        if user_id is not None:
            async with factory() as cleanup:
                await cleanup.execute(delete(User).where(User.id == user_id))
                await cleanup.commit()
        await engine.dispose()
