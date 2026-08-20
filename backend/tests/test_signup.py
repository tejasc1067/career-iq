"""Tests for the signup endpoint."""

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.password import verify_password
from app.users.models import User

SIGNUP_URL = "/api/auth/signup"
PASSWORD = "correct horse battery staple"


async def _signup(client: AsyncClient, email: str, password: str = PASSWORD):
    return await client.post(SIGNUP_URL, json={"email": email, "password": password})


async def test_signup_creates_the_account(api_client: AsyncClient) -> None:
    """A valid request returns 201 and the safe user representation."""
    response = await _signup(api_client, "new@example.com")

    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "new@example.com"
    assert set(body) == {"id", "email", "created_at", "updated_at"}


async def test_response_never_carries_the_password_or_its_hash(
    api_client: AsyncClient,
) -> None:
    """Neither the plaintext nor the hash may appear anywhere in the response."""
    response = await _signup(api_client, "safe@example.com")
    raw = response.text

    assert "password" not in response.json()
    assert "password_hash" not in response.json()
    assert PASSWORD not in raw
    assert "$argon2id$" not in raw


@pytest.mark.parametrize(
    "submitted",
    ["Tejas@Example.COM", "  Tejas@Example.COM  ", "TEJAS@EXAMPLE.COM"],
)
async def test_email_is_normalized_before_storage(
    api_client: AsyncClient, db_session: AsyncSession, submitted: str
) -> None:
    """Case and surrounding whitespace are stripped before persistence."""
    response = await _signup(api_client, submitted)

    assert response.status_code == 201
    assert response.json()["email"] == "tejas@example.com"
    stored = await db_session.scalar(select(User.email))
    assert stored == "tejas@example.com"


async def test_password_is_stored_only_as_an_argon2id_hash(
    api_client: AsyncClient, db_session: AsyncSession
) -> None:
    """The stored credential is an Argon2id hash, never the plaintext."""
    await _signup(api_client, "hashed@example.com")

    stored = await db_session.scalar(select(User.password_hash))
    assert stored is not None
    assert stored.startswith("$argon2id$")
    assert stored != PASSWORD
    assert PASSWORD not in stored


async def test_stored_hash_verifies_against_the_original_password(
    api_client: AsyncClient, db_session: AsyncSession
) -> None:
    """The existing verification function accepts the password it was given."""
    await _signup(api_client, "verify@example.com")

    stored = await db_session.scalar(select(User.password_hash))
    assert verify_password(PASSWORD, stored) is True
    assert verify_password("wrong password", stored) is False


async def test_duplicate_email_is_rejected(api_client: AsyncClient) -> None:
    """A second signup with the same email returns 409."""
    assert (await _signup(api_client, "dupe@example.com")).status_code == 201

    response = await _signup(api_client, "dupe@example.com")

    assert response.status_code == 409
    assert response.json()["detail"] == (
        "An account with this email address already exists."
    )


async def test_duplicate_detection_ignores_case_and_whitespace(
    api_client: AsyncClient,
) -> None:
    """Normalization makes duplicate detection case-insensitive."""
    assert (await _signup(api_client, "person@example.com")).status_code == 201

    response = await _signup(api_client, "  Person@Example.COM  ")

    assert response.status_code == 409


@pytest.mark.parametrize(
    "email",
    ["", "not-an-email", "@example.com", "person@", "person@example", "a b@c.com"],
)
async def test_invalid_email_is_rejected(api_client: AsyncClient, email: str) -> None:
    """Malformed addresses fail validation with 422."""
    assert (await _signup(api_client, email)).status_code == 422


@pytest.mark.parametrize("password", ["", "short", "1234567", "x" * 129])
async def test_invalid_password_is_rejected(
    api_client: AsyncClient, password: str
) -> None:
    """Passwords outside the length policy fail validation with 422."""
    response = await _signup(api_client, "policy@example.com", password)

    assert response.status_code == 422
    assert PASSWORD not in response.text


async def test_validation_error_does_not_echo_the_password(
    api_client: AsyncClient,
) -> None:
    """A rejected password must not be reflected back to the caller."""
    secret = "hunter2"
    response = await _signup(api_client, "echo@example.com", secret)

    assert response.status_code == 422
    assert secret not in response.text


async def test_database_unique_constraint_is_still_enforced(
    db_session: AsyncSession,
) -> None:
    """The unique index remains authoritative, independent of the endpoint."""
    db_session.add(User(email="direct@example.com", password_hash="x"))
    await db_session.flush()

    db_session.add(User(email="direct@example.com", password_hash="x"))
    with pytest.raises(IntegrityError):
        await db_session.flush()
