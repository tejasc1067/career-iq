"""Tests for refresh-token persistence and hashing."""

import uuid
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import delete, inspect, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import RefreshToken
from app.auth.refresh import TOKEN_HASH_LENGTH, hash_refresh_token
from app.users.models import User

RAW_TOKEN = "0PJXbQ7kx1n-Zt4WsvGf9aYh2LmR8dEcTuNqAoBpKiU"


async def _user(session: AsyncSession, email: str = "owner@example.com") -> User:
    user = User(email=email, password_hash="not-a-real-hash")
    session.add(user)
    await session.flush()
    return user


def _token(user_id: uuid.UUID, raw: str = RAW_TOKEN, **overrides) -> RefreshToken:
    values = {
        "user_id": user_id,
        "token_hash": hash_refresh_token(raw),
        "family_id": uuid.uuid4(),
        "expires_at": datetime.now(UTC) + timedelta(days=30),
    }
    values.update(overrides)
    return RefreshToken(**values)


async def test_refresh_token_persists(db_session: AsyncSession) -> None:
    """A refresh token round-trips through the database."""
    user = await _user(db_session)
    token = _token(user.id)
    db_session.add(token)
    await db_session.flush()
    db_session.expunge_all()

    loaded = await db_session.scalar(
        select(RefreshToken).where(
            RefreshToken.token_hash == hash_refresh_token(RAW_TOKEN)
        )
    )

    assert loaded is not None
    assert isinstance(loaded.id, uuid.UUID)
    assert loaded.created_at is not None


async def test_user_id_references_a_user(db_session: AsyncSession) -> None:
    """user_id resolves to the owning User row."""
    user = await _user(db_session)
    db_session.add(_token(user.id))
    await db_session.flush()

    owner_id = await db_session.scalar(select(RefreshToken.user_id))

    assert owner_id == user.id


async def test_expiry_and_family_are_persisted(db_session: AsyncSession) -> None:
    """expires_at and family_id survive a round trip."""
    user = await _user(db_session)
    family = uuid.uuid4()
    expires = datetime.now(UTC) + timedelta(days=30)
    db_session.add(_token(user.id, family_id=family, expires_at=expires))
    await db_session.flush()
    db_session.expunge_all()

    loaded = await db_session.scalar(select(RefreshToken))

    assert loaded.family_id == family
    assert loaded.expires_at == expires


async def test_revoked_at_is_nullable_and_settable(db_session: AsyncSession) -> None:
    """revoked_at starts null and can be set."""
    user = await _user(db_session)
    token = _token(user.id)
    db_session.add(token)
    await db_session.flush()
    assert token.revoked_at is None

    token.revoked_at = datetime.now(UTC)
    await db_session.flush()
    db_session.expunge_all()

    assert await db_session.scalar(select(RefreshToken.revoked_at)) is not None


@pytest.mark.parametrize(
    "missing", ["user_id", "token_hash", "family_id", "expires_at"]
)
async def test_required_fields_are_enforced(
    db_session: AsyncSession, missing: str
) -> None:
    """Omitting any NOT NULL column is rejected by the database."""
    user = await _user(db_session)
    token = _token(user.id)
    setattr(token, missing, None)
    db_session.add(token)

    with pytest.raises(IntegrityError):
        await db_session.flush()


async def test_token_hash_is_unique(db_session: AsyncSession) -> None:
    """The same token hash cannot be stored twice."""
    user = await _user(db_session)
    db_session.add(_token(user.id))
    await db_session.flush()

    db_session.add(_token(user.id, family_id=uuid.uuid4()))
    with pytest.raises(IntegrityError):
        await db_session.flush()


async def test_unknown_user_is_rejected_by_the_foreign_key(
    db_session: AsyncSession,
) -> None:
    """A token cannot reference a user that does not exist."""
    db_session.add(_token(uuid.uuid4()))

    with pytest.raises(IntegrityError):
        await db_session.flush()


async def test_deleting_the_user_cascades_to_its_tokens(
    db_session: AsyncSession,
) -> None:
    """ON DELETE CASCADE removes a user's refresh tokens."""
    user = await _user(db_session)
    db_session.add(_token(user.id))
    await db_session.flush()
    assert await db_session.scalar(select(RefreshToken.id)) is not None

    await db_session.execute(delete(User).where(User.id == user.id))
    await db_session.flush()

    assert await db_session.scalar(select(RefreshToken.id)) is None


def test_hashing_is_deterministic() -> None:
    """The same token always hashes to the same value, enabling lookup."""
    assert hash_refresh_token(RAW_TOKEN) == hash_refresh_token(RAW_TOKEN)


def test_different_tokens_hash_differently() -> None:
    """Distinct tokens produce distinct hashes."""
    hashes = {hash_refresh_token(f"{RAW_TOKEN}-{i}") for i in range(50)}

    assert len(hashes) == 50


def test_hash_is_not_the_raw_token() -> None:
    """The stored value neither equals nor contains the raw token."""
    hashed = hash_refresh_token(RAW_TOKEN)

    assert hashed != RAW_TOKEN
    assert RAW_TOKEN not in hashed
    assert len(hashed) == TOKEN_HASH_LENGTH


async def test_raw_token_is_absent_from_every_column(
    db_session: AsyncSession,
) -> None:
    """No column of the stored row contains the plaintext token."""
    user = await _user(db_session)
    db_session.add(_token(user.id))
    await db_session.flush()

    row = (
        (await db_session.execute(text("SELECT * FROM refresh_tokens")))
        .mappings()
        .one()
    )

    assert RAW_TOKEN not in " ".join(str(v) for v in row.values())
    assert row["token_hash"] == hash_refresh_token(RAW_TOKEN)


async def test_table_has_the_expected_indexes_and_constraints(
    db_session: AsyncSession,
) -> None:
    """The migrated table carries the indexes the architecture requires."""
    connection = await db_session.connection()

    def _reflect(sync_conn):
        inspector = inspect(sync_conn)
        return (
            {
                i["name"]: (tuple(i["column_names"]), i["unique"])
                for i in inspector.get_indexes("refresh_tokens")
            },
            inspector.get_foreign_keys("refresh_tokens"),
            {c["name"] for c in inspector.get_columns("refresh_tokens")},
        )

    indexes, foreign_keys, columns = await connection.run_sync(_reflect)

    assert columns == {
        "id",
        "user_id",
        "token_hash",
        "family_id",
        "expires_at",
        "revoked_at",
        "created_at",
    }
    assert indexes["ix_refresh_tokens_token_hash"] == (("token_hash",), True)
    assert indexes["ix_refresh_tokens_user_id"] == (("user_id",), False)
    assert indexes["ix_refresh_tokens_family_id"] == (("family_id",), False)
    assert foreign_keys[0]["referred_table"] == "users"
    assert foreign_keys[0]["options"]["ondelete"] == "CASCADE"
