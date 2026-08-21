"""Tests for the login endpoint."""

import uuid
from http.cookies import SimpleCookie

import jwt
import pytest
from httpx import AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import RefreshToken
from app.auth.password import hash_password
from app.auth.refresh import hash_refresh_token
from app.auth.router import REFRESH_COOKIE_NAME
from app.auth.tokens import ACCESS_TOKEN_TYPE, REQUIRED_CLAIMS, decode_access_token
from app.common.config import get_settings
from app.users.models import User

LOGIN_URL = "/api/auth/login"
EMAIL = "member@example.com"
PASSWORD = "correct horse battery staple"


async def _register(session: AsyncSession, email: str = EMAIL) -> User:
    user = User(email=email, password_hash=hash_password(PASSWORD))
    session.add(user)
    await session.commit()
    return user


async def _login(client: AsyncClient, email: str, password: str = PASSWORD):
    return await client.post(LOGIN_URL, json={"email": email, "password": password})


def _refresh_cookie(response) -> SimpleCookie:
    jar = SimpleCookie()
    for header in response.headers.get_list("set-cookie"):
        jar.load(header)
    return jar


async def test_login_returns_an_access_token(
    api_client: AsyncClient, db_session: AsyncSession
) -> None:
    """Valid credentials return 200 with a bearer access token."""
    await _register(db_session)

    response = await _login(api_client, EMAIL)

    assert response.status_code == 200
    body = response.json()
    assert set(body) == {"access_token", "token_type", "expires_in"}
    assert body["token_type"] == "bearer"
    assert body["expires_in"] == get_settings().access_token_expire_minutes * 60


async def test_response_body_carries_no_secret(
    api_client: AsyncClient, db_session: AsyncSession
) -> None:
    """No refresh token, password, or hash may appear in the JSON."""
    await _register(db_session)

    response = await _login(api_client, EMAIL)
    raw = response.text

    assert "refresh" not in response.json()
    assert "password" not in raw
    assert "password_hash" not in raw
    assert PASSWORD not in raw
    assert "$argon2id$" not in raw
    cookie = _refresh_cookie(response)
    assert cookie[REFRESH_COOKIE_NAME].value not in raw


async def test_access_token_claims_and_subject(
    api_client: AsyncClient, db_session: AsyncSession
) -> None:
    """The token decodes to the caller's UUID with exactly the documented claims."""
    user_id = (await _register(db_session)).id

    response = await _login(api_client, EMAIL)
    token = response.json()["access_token"]

    assert decode_access_token(token) == user_id

    settings = get_settings()
    claims = jwt.decode(
        token,
        settings.jwt_secret.get_secret_value(),
        algorithms=[settings.jwt_algorithm],
    )
    assert set(claims) == set(REQUIRED_CLAIMS)
    assert claims["sub"] == str(user_id)
    assert claims["type"] == ACCESS_TOKEN_TYPE
    assert claims["jti"]
    assert claims["exp"] - claims["iat"] == settings.access_token_expire_minutes * 60


async def test_refresh_cookie_attributes(
    api_client: AsyncClient, db_session: AsyncSession
) -> None:
    """The refresh cookie follows ARCHITECTURE.md section 11.2 exactly."""
    await _register(db_session)
    settings = get_settings()

    response = await _login(api_client, EMAIL)
    header = next(
        h
        for h in response.headers.get_list("set-cookie")
        if h.startswith(f"{REFRESH_COOKIE_NAME}=")
    )
    morsel = _refresh_cookie(response)[REFRESH_COOKIE_NAME]

    assert "HttpOnly" in header
    assert "Secure" in header
    assert morsel["samesite"].lower() == "lax"
    assert morsel["path"] == "/api/auth"
    assert int(morsel["max-age"]) == settings.refresh_token_expire_days * 86400
    assert morsel.value


async def test_login_persists_exactly_one_hashed_refresh_token(
    api_client: AsyncClient, db_session: AsyncSession
) -> None:
    """One unrevoked refresh-token row is stored, as a hash, for the right user."""
    user_id = (await _register(db_session)).id

    response = await _login(api_client, EMAIL)
    raw_token = _refresh_cookie(response)[REFRESH_COOKIE_NAME].value

    records = (await db_session.scalars(select(RefreshToken))).all()
    assert len(records) == 1
    record = records[0]
    assert record.user_id == user_id
    assert record.token_hash == hash_refresh_token(raw_token)
    assert record.token_hash != raw_token
    assert record.revoked_at is None
    assert isinstance(record.family_id, uuid.UUID)
    expected = get_settings().refresh_token_expire_days
    assert 29 <= (record.expires_at - record.created_at).days <= expected


async def test_each_login_starts_a_new_family(
    api_client: AsyncClient, db_session: AsyncSession
) -> None:
    """Separate sessions do not share a refresh-token family."""
    await _register(db_session)

    await _login(api_client, EMAIL)
    await _login(api_client, EMAIL)

    families = set((await db_session.scalars(select(RefreshToken.family_id))).all())
    assert len(families) == 2


async def test_raw_refresh_token_is_not_persisted(
    api_client: AsyncClient, db_session: AsyncSession
) -> None:
    """The plaintext refresh token appears in no stored column."""
    await _register(db_session)

    response = await _login(api_client, EMAIL)
    raw_token = _refresh_cookie(response)[REFRESH_COOKIE_NAME].value

    record = (await db_session.scalars(select(RefreshToken))).one()
    stored = " ".join(
        str(getattr(record, column))
        for column in ("id", "user_id", "token_hash", "family_id")
    )
    assert raw_token not in stored


@pytest.mark.parametrize(
    ("email", "password"),
    [
        ("nobody@example.com", PASSWORD),
        (EMAIL, "the wrong password entirely"),
        (EMAIL, ""),
        ("nobody@example.com", "also wrong"),
    ],
)
async def test_bad_credentials_share_one_response(
    api_client: AsyncClient, db_session: AsyncSession, email: str, password: str
) -> None:
    """Unknown email and wrong password are indistinguishable to the caller."""
    await _register(db_session)

    response = await _login(api_client, email, password)

    assert response.status_code == 401
    assert response.json() == {"detail": "Incorrect email address or password."}


async def test_failed_login_leaks_nothing_and_persists_nothing(
    api_client: AsyncClient, db_session: AsyncSession
) -> None:
    """A rejected login stores no refresh token and sets no cookie."""
    await _register(db_session)

    response = await _login(api_client, EMAIL, "wrong password")

    assert response.status_code == 401
    assert PASSWORD not in response.text
    assert "argon2" not in response.text.lower()
    assert REFRESH_COOKIE_NAME not in response.headers.get("set-cookie", "")
    assert await db_session.scalar(select(func.count()).select_from(RefreshToken)) == 0


async def test_login_normalizes_the_submitted_email(
    api_client: AsyncClient, db_session: AsyncSession
) -> None:
    """Case and surrounding whitespace do not prevent a match."""
    await _register(db_session)

    response = await _login(api_client, f"  {EMAIL.upper()}  ")

    assert response.status_code == 200


async def test_login_does_not_enforce_the_signup_password_policy(
    api_client: AsyncClient, db_session: AsyncSession
) -> None:
    """A short guess is rejected as 401, not 422, so it reveals no policy detail."""
    await _register(db_session)

    response = await _login(api_client, EMAIL, "short")

    assert response.status_code == 401
