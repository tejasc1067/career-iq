"""Tests for the signed-in user's account and profile endpoints."""

import uuid
from datetime import UTC, datetime, timedelta

import jwt
import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.password import hash_password
from app.auth.tokens import ACCESS_TOKEN_TYPE, create_access_token
from app.common.config import get_settings
from app.users.models import User, UserProfile

ME_URL = "/api/users/me"
PROFILE_URL = "/api/users/me/profile"
PASSWORD = "correct horse battery staple"
PROFILE = {
    "current_role": "Software Engineer",
    "career_level": "Mid-level",
    "years_of_experience": 4.5,
}
OTHER_PROFILE = {
    "current_role": "Data Analyst",
    "career_level": "Senior",
    "years_of_experience": 9.0,
}


async def _user(session: AsyncSession, email: str = "member@example.com") -> User:
    user = User(email=email, password_hash=hash_password(PASSWORD))
    session.add(user)
    await session.commit()
    return user


def _auth(user: User) -> dict[str, str]:
    return {"Authorization": f"Bearer {create_access_token(user.id)}"}


def _signed(claims: dict, secret: str | None = None) -> str:
    settings = get_settings()
    return jwt.encode(
        claims,
        secret or settings.jwt_secret.get_secret_value(),
        algorithm=settings.jwt_algorithm,
    )


def _base_claims(user_id: uuid.UUID, issued_at: datetime) -> dict:
    return {
        "sub": str(user_id),
        "iat": issued_at,
        "exp": issued_at + timedelta(minutes=15),
        "type": ACCESS_TOKEN_TYPE,
        "jti": uuid.uuid4().hex,
    }


async def _stored(session: AsyncSession, user: User) -> UserProfile | None:
    return await session.scalar(
        select(UserProfile).where(UserProfile.user_id == user.id)
    )


async def test_reading_the_account_requires_a_token(api_client: AsyncClient) -> None:
    """No token means no resource lookup."""
    response = await api_client.get(ME_URL)

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


async def test_saving_the_profile_requires_a_token(api_client: AsyncClient) -> None:
    """An unauthenticated save is rejected before anything is written."""
    response = await api_client.put(PROFILE_URL, json=PROFILE)

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


@pytest.mark.parametrize(
    "header",
    [
        {"Authorization": "Bearer not-a-token"},
        {"Authorization": "Bearer "},
        {"Authorization": "Basic bWVtYmVyOnBhc3N3b3Jk"},
        {"Authorization": "not-even-a-scheme"},
    ],
)
async def test_a_malformed_credential_is_rejected(
    api_client: AsyncClient, header: dict[str, str]
) -> None:
    """Garbage in the Authorization header never reaches the database."""
    response = await api_client.get(ME_URL, headers=header)

    assert response.status_code == 401


async def test_an_expired_token_is_rejected(
    api_client: AsyncClient, db_session: AsyncSession
) -> None:
    """A token past its expiry cannot read the account it was issued for."""
    user = await _user(db_session)
    past = datetime.now(UTC) - timedelta(hours=2)
    token = _signed(_base_claims(user.id, past))

    response = await api_client.get(
        ME_URL, headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 401


async def test_a_token_signed_with_another_secret_is_rejected(
    api_client: AsyncClient, db_session: AsyncSession
) -> None:
    """A forged signature is rejected even when every claim looks correct."""
    user = await _user(db_session)
    token = _signed(_base_claims(user.id, datetime.now(UTC)), secret="a" * 48)

    response = await api_client.get(
        ME_URL, headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 401


async def test_a_token_for_an_unknown_user_is_rejected(api_client: AsyncClient) -> None:
    """A validly signed token whose subject no longer exists grants nothing."""
    token = _signed(_base_claims(uuid.uuid4(), datetime.now(UTC)))

    response = await api_client.get(
        ME_URL, headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 401


async def test_me_returns_the_account_with_an_empty_profile(
    api_client: AsyncClient, db_session: AsyncSession
) -> None:
    """Before the first save the profile is present but empty, not a 404."""
    user = await _user(db_session)

    response = await api_client.get(ME_URL, headers=_auth(user))

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == str(user.id)
    assert body["email"] == user.email
    assert body["profile"] == {
        "current_role": None,
        "career_level": None,
        "years_of_experience": None,
        "updated_at": None,
    }


async def test_me_never_exposes_authentication_internals(
    api_client: AsyncClient, db_session: AsyncSession
) -> None:
    """The response carries no password hash and no refresh-token data."""
    user = await _user(db_session)

    response = await api_client.get(ME_URL, headers=_auth(user))

    body = response.json()
    assert set(body) == {"id", "email", "created_at", "updated_at", "profile"}
    serialized = response.text
    assert user.password_hash not in serialized
    assert "password" not in serialized
    assert "refresh" not in serialized


async def test_put_creates_the_profile_and_get_reads_it_back(
    api_client: AsyncClient, db_session: AsyncSession
) -> None:
    """The first save inserts a row owned by the token's subject."""
    user = await _user(db_session)

    saved = await api_client.put(PROFILE_URL, json=PROFILE, headers=_auth(user))

    assert saved.status_code == 200
    body = saved.json()
    assert {key: body[key] for key in PROFILE} == PROFILE
    assert body["updated_at"] is not None

    stored = await _stored(db_session, user)
    assert stored is not None
    assert stored.user_id == user.id

    reread = await api_client.get(ME_URL, headers=_auth(user))
    assert {key: reread.json()["profile"][key] for key in PROFILE} == PROFILE


async def test_put_updates_an_existing_profile_without_adding_a_row(
    api_client: AsyncClient, db_session: AsyncSession
) -> None:
    """A second save overwrites the same row rather than creating another."""
    user = await _user(db_session)
    await api_client.put(PROFILE_URL, json=PROFILE, headers=_auth(user))

    updated = await api_client.put(
        PROFILE_URL,
        json={**PROFILE, "current_role": "Java Developer"},
        headers=_auth(user),
    )

    assert updated.status_code == 200
    assert updated.json()["current_role"] == "Java Developer"
    rows = (
        await db_session.scalars(
            select(UserProfile).where(UserProfile.user_id == user.id)
        )
    ).all()
    assert len(rows) == 1


async def test_put_is_a_full_replacement(
    api_client: AsyncClient, db_session: AsyncSession
) -> None:
    """An omitted field clears the stored value; nothing is silently kept."""
    user = await _user(db_session)
    await api_client.put(PROFILE_URL, json=PROFILE, headers=_auth(user))

    response = await api_client.put(
        PROFILE_URL, json={"current_role": "Java Developer"}, headers=_auth(user)
    )

    assert response.status_code == 200
    assert response.json() == {
        "current_role": "Java Developer",
        "career_level": None,
        "years_of_experience": None,
        "updated_at": response.json()["updated_at"],
    }


async def test_blank_text_is_stored_as_absent(
    api_client: AsyncClient, db_session: AsyncSession
) -> None:
    """A cleared text field becomes null rather than an empty string."""
    user = await _user(db_session)

    response = await api_client.put(
        PROFILE_URL,
        json={"current_role": "   ", "career_level": "  Senior  "},
        headers=_auth(user),
    )

    assert response.status_code == 200
    assert response.json()["current_role"] is None
    assert response.json()["career_level"] == "Senior"


@pytest.mark.parametrize(
    "payload",
    [
        {"current_role": "x" * 121},
        {"career_level": "x" * 81},
        {"years_of_experience": -1},
        {"years_of_experience": 71},
        {"years_of_experience": "four"},
    ],
)
async def test_invalid_profile_values_are_rejected(
    api_client: AsyncClient, db_session: AsyncSession, payload: dict
) -> None:
    """Out-of-range and mistyped values are refused and nothing is written."""
    user = await _user(db_session)

    response = await api_client.put(PROFILE_URL, json=payload, headers=_auth(user))

    assert response.status_code == 422
    assert await _stored(db_session, user) is None


async def test_a_client_supplied_user_id_is_rejected(
    api_client: AsyncClient, db_session: AsyncSession
) -> None:
    """A payload naming an owner is an error, so it can never redirect a write."""
    user = await _user(db_session)
    victim = await _user(db_session, email="victim@example.com")

    response = await api_client.put(
        PROFILE_URL,
        json={**PROFILE, "user_id": str(victim.id)},
        headers=_auth(user),
    )

    assert response.status_code == 422
    assert await _stored(db_session, victim) is None
    assert await _stored(db_session, user) is None


async def test_one_user_cannot_read_another_users_profile(
    api_client: AsyncClient, db_session: AsyncSession
) -> None:
    """Each token sees only the profile of its own subject."""
    first = await _user(db_session, email="first@example.com")
    second = await _user(db_session, email="second@example.com")
    await api_client.put(PROFILE_URL, json=PROFILE, headers=_auth(first))
    await api_client.put(PROFILE_URL, json=OTHER_PROFILE, headers=_auth(second))

    seen_by_first = await api_client.get(ME_URL, headers=_auth(first))
    seen_by_second = await api_client.get(ME_URL, headers=_auth(second))

    assert seen_by_first.json()["email"] == "first@example.com"
    assert seen_by_first.json()["profile"]["current_role"] == PROFILE["current_role"]
    assert seen_by_second.json()["email"] == "second@example.com"
    assert (
        seen_by_second.json()["profile"]["current_role"]
        == OTHER_PROFILE["current_role"]
    )


async def test_one_user_cannot_overwrite_another_users_profile(
    api_client: AsyncClient, db_session: AsyncSession
) -> None:
    """A save touches only the caller's row, leaving other users untouched."""
    first = await _user(db_session, email="first@example.com")
    second = await _user(db_session, email="second@example.com")
    await api_client.put(PROFILE_URL, json=PROFILE, headers=_auth(first))

    await api_client.put(PROFILE_URL, json=OTHER_PROFILE, headers=_auth(second))

    stored_first = await _stored(db_session, first)
    assert stored_first is not None
    assert stored_first.current_role == PROFILE["current_role"]


async def test_a_deleted_user_takes_their_profile_with_them(
    api_client: AsyncClient, db_session: AsyncSession
) -> None:
    """The owning foreign key cascades, so no orphan profile survives."""
    user = await _user(db_session)
    await api_client.put(PROFILE_URL, json=PROFILE, headers=_auth(user))

    await db_session.delete(user)
    await db_session.commit()

    assert await _stored(db_session, user) is None
