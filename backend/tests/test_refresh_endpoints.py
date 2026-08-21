"""Tests for the refresh and logout endpoints."""

import uuid
from datetime import UTC, datetime, timedelta
from http.cookies import SimpleCookie

import jwt
import pytest
from httpx import AsyncClient
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.auth.models import RefreshToken
from app.auth.password import hash_password
from app.auth.refresh import hash_refresh_token, issue_refresh_token
from app.auth.router import REFRESH_COOKIE_NAME
from app.auth.tokens import ACCESS_TOKEN_TYPE, REQUIRED_CLAIMS, decode_access_token
from app.common.config import get_settings
from app.users.models import User

REFRESH_URL = "/api/auth/refresh"
LOGOUT_URL = "/api/auth/logout"
PASSWORD = "correct horse battery staple"


async def _user(session: AsyncSession, email: str = "member@example.com") -> uuid.UUID:
    user = User(email=email, password_hash=hash_password(PASSWORD))
    session.add(user)
    await session.commit()
    return user.id


async def _session_token(
    session: AsyncSession, user_id: uuid.UUID
) -> tuple[str, uuid.UUID]:
    issued = await issue_refresh_token(session, user_id)
    await session.commit()
    return issued.raw_token, issued.record.family_id


def _cookie(response) -> SimpleCookie:
    jar = SimpleCookie()
    for header in response.headers.get_list("set-cookie"):
        jar.load(header)
    return jar


async def test_refresh_returns_a_new_access_token(
    api_client: AsyncClient, db_session: AsyncSession
) -> None:
    """A valid refresh cookie yields 200 and a fresh access token."""
    user_id = await _user(db_session)
    raw_token, _ = await _session_token(db_session, user_id)
    api_client.cookies.set(REFRESH_COOKIE_NAME, raw_token)

    response = await api_client.post(REFRESH_URL)

    assert response.status_code == 200
    body = response.json()
    assert set(body) == {"access_token", "token_type", "expires_in"}
    assert decode_access_token(body["access_token"]) == user_id


async def test_refresh_access_token_lifetime_and_claims(
    api_client: AsyncClient, db_session: AsyncSession
) -> None:
    """The reissued access token keeps the documented claims and 15-minute life."""
    user_id = await _user(db_session)
    raw_token, _ = await _session_token(db_session, user_id)
    api_client.cookies.set(REFRESH_COOKIE_NAME, raw_token)
    settings = get_settings()

    response = await api_client.post(REFRESH_URL)
    claims = jwt.decode(
        response.json()["access_token"],
        settings.jwt_secret.get_secret_value(),
        algorithms=[settings.jwt_algorithm],
    )

    assert set(claims) == set(REQUIRED_CLAIMS)
    assert claims["type"] == ACCESS_TOKEN_TYPE
    assert claims["exp"] - claims["iat"] == settings.access_token_expire_minutes * 60
    assert response.json()["expires_in"] == settings.access_token_expire_minutes * 60


async def test_refresh_sets_a_replacement_cookie(
    api_client: AsyncClient, db_session: AsyncSession
) -> None:
    """The response carries a new refresh cookie with the standard attributes."""
    user_id = await _user(db_session)
    raw_token, _ = await _session_token(db_session, user_id)
    api_client.cookies.set(REFRESH_COOKIE_NAME, raw_token)
    settings = get_settings()

    response = await api_client.post(REFRESH_URL)
    header = next(
        h
        for h in response.headers.get_list("set-cookie")
        if h.startswith(f"{REFRESH_COOKIE_NAME}=")
    )
    morsel = _cookie(response)[REFRESH_COOKIE_NAME]

    assert morsel.value != raw_token
    assert "HttpOnly" in header
    assert "Secure" in header
    assert morsel["samesite"].lower() == "lax"
    assert morsel["path"] == "/api/auth"
    assert int(morsel["max-age"]) == settings.refresh_token_expire_days * 86400


async def test_refresh_rotates_persistently_within_the_same_family(
    api_client: AsyncClient, db_session: AsyncSession
) -> None:
    """The old token is revoked and the replacement is stored in the same family."""
    user_id = await _user(db_session)
    raw_token, family_id = await _session_token(db_session, user_id)
    api_client.cookies.set(REFRESH_COOKIE_NAME, raw_token)

    response = await api_client.post(REFRESH_URL)
    replacement = _cookie(response)[REFRESH_COOKIE_NAME].value

    records = (
        await db_session.scalars(
            select(RefreshToken).where(RefreshToken.family_id == family_id)
        )
    ).all()
    by_hash = {r.token_hash: r for r in records}

    assert len(records) == 2
    assert by_hash[hash_refresh_token(raw_token)].revoked_at is not None
    new_record = by_hash[hash_refresh_token(replacement)]
    assert new_record.revoked_at is None
    assert new_record.user_id == user_id
    assert new_record.family_id == family_id
    expected = get_settings().refresh_token_expire_days
    assert 29 <= (new_record.expires_at - new_record.created_at).days <= expected


async def test_refresh_never_returns_the_token_and_never_stores_it_raw(
    api_client: AsyncClient, db_session: AsyncSession
) -> None:
    """The refresh token appears only in the cookie, and only as a hash in the table."""
    user_id = await _user(db_session)
    raw_token, _ = await _session_token(db_session, user_id)
    api_client.cookies.set(REFRESH_COOKIE_NAME, raw_token)

    response = await api_client.post(REFRESH_URL)
    replacement = _cookie(response)[REFRESH_COOKIE_NAME].value

    assert "refresh" not in response.json()
    assert replacement not in response.text
    assert raw_token not in response.text
    hashes = set((await db_session.scalars(select(RefreshToken.token_hash))).all())
    assert replacement not in hashes
    assert raw_token not in hashes


async def test_refresh_without_a_cookie_is_rejected(api_client: AsyncClient) -> None:
    """A missing cookie is a 401, not a 500."""
    response = await api_client.post(REFRESH_URL)

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Your session is no longer valid. Please sign in again."
    }


async def test_refresh_with_an_unknown_token_is_rejected(
    api_client: AsyncClient,
) -> None:
    """A token matching no stored hash is a 401."""
    api_client.cookies.set(REFRESH_COOKIE_NAME, "not-a-real-refresh-token")

    response = await api_client.post(REFRESH_URL)

    assert response.status_code == 401


async def test_refresh_with_an_expired_token_is_rejected(
    api_client: AsyncClient, db_session: AsyncSession
) -> None:
    """An expired token cannot be exchanged."""
    user_id = await _user(db_session)
    issued = await issue_refresh_token(db_session, user_id)
    issued.record.expires_at = datetime.now(UTC) - timedelta(seconds=1)
    await db_session.commit()
    api_client.cookies.set(REFRESH_COOKIE_NAME, issued.raw_token)

    response = await api_client.post(REFRESH_URL)

    assert response.status_code == 401


async def test_reuse_is_rejected_and_the_family_revocation_persists(
    api_client: AsyncClient, db_session: AsyncSession
) -> None:
    """Replaying a consumed token 401s and leaves the whole family revoked."""
    user_id = await _user(db_session)
    raw_token, family_id = await _session_token(db_session, user_id)
    api_client.cookies.set(REFRESH_COOKIE_NAME, raw_token)
    await api_client.post(REFRESH_URL)

    api_client.cookies.set(REFRESH_COOKIE_NAME, raw_token)
    response = await api_client.post(REFRESH_URL)

    assert response.status_code == 401
    db_session.expunge_all()
    unrevoked = await db_session.scalar(
        select(func.count())
        .select_from(RefreshToken)
        .where(RefreshToken.family_id == family_id, RefreshToken.revoked_at.is_(None))
    )
    assert unrevoked == 0


@pytest.mark.parametrize("detail_leak", ["argon2", "token_hash", "family_id", "sql"])
async def test_refresh_failures_leak_no_internals(
    api_client: AsyncClient, detail_leak: str
) -> None:
    """Rejections carry no implementation detail."""
    api_client.cookies.set(REFRESH_COOKIE_NAME, "bogus")

    response = await api_client.post(REFRESH_URL)

    assert detail_leak not in response.text.lower()


async def test_logout_revokes_the_active_token_and_clears_the_cookie(
    api_client: AsyncClient, db_session: AsyncSession
) -> None:
    """Logout revokes the presented token and expires the cookie."""
    user_id = await _user(db_session)
    raw_token, family_id = await _session_token(db_session, user_id)
    api_client.cookies.set(REFRESH_COOKIE_NAME, raw_token)

    response = await api_client.post(LOGOUT_URL)

    assert response.status_code == 204
    assert response.content == b""
    morsel = _cookie(response)[REFRESH_COOKIE_NAME]
    assert morsel.value == ""
    assert morsel["path"] == "/api/auth"
    header = next(
        h
        for h in response.headers.get_list("set-cookie")
        if h.startswith(f"{REFRESH_COOKIE_NAME}=")
    )
    assert "HttpOnly" in header
    assert "Secure" in header
    assert morsel["samesite"].lower() == "lax"

    db_session.expunge_all()
    unrevoked = await db_session.scalar(
        select(func.count())
        .select_from(RefreshToken)
        .where(RefreshToken.family_id == family_id, RefreshToken.revoked_at.is_(None))
    )
    assert unrevoked == 0


async def test_logout_without_a_cookie_succeeds(api_client: AsyncClient) -> None:
    """Logout is safe to call with no session."""
    response = await api_client.post(LOGOUT_URL)

    assert response.status_code == 204
    assert REFRESH_COOKIE_NAME in response.headers.get("set-cookie", "")


async def test_logout_is_idempotent(
    api_client: AsyncClient, db_session: AsyncSession
) -> None:
    """Calling logout twice with the same token still succeeds."""
    user_id = await _user(db_session)
    raw_token, _ = await _session_token(db_session, user_id)

    for _ in range(2):
        api_client.cookies.set(REFRESH_COOKIE_NAME, raw_token)
        assert (await api_client.post(LOGOUT_URL)).status_code == 204


async def test_logout_with_an_unknown_cookie_succeeds(
    api_client: AsyncClient,
) -> None:
    """An unrecognised cookie value does not turn logout into an error."""
    api_client.cookies.set(REFRESH_COOKIE_NAME, "never-issued")

    assert (await api_client.post(LOGOUT_URL)).status_code == 204


async def test_logout_leaves_other_families_alone(
    api_client: AsyncClient, db_session: AsyncSession
) -> None:
    """Ending one session does not end another."""
    user_id = await _user(db_session)
    other_user_id = await _user(db_session, "other@example.com")
    ending, _ = await _session_token(db_session, user_id)
    keeping_raw, keeping_family = await _session_token(db_session, user_id)
    other_raw, other_family = await _session_token(db_session, other_user_id)
    api_client.cookies.set(REFRESH_COOKIE_NAME, ending)

    await api_client.post(LOGOUT_URL)

    db_session.expunge_all()
    survivors = set(
        (
            await db_session.scalars(
                select(RefreshToken.token_hash).where(RefreshToken.revoked_at.is_(None))
            )
        ).all()
    )
    assert survivors == {
        hash_refresh_token(keeping_raw),
        hash_refresh_token(other_raw),
    }
    assert keeping_family != other_family


async def test_logout_returns_no_token(
    api_client: AsyncClient, db_session: AsyncSession
) -> None:
    """The logout response body is empty."""
    user_id = await _user(db_session)
    raw_token, _ = await _session_token(db_session, user_id)
    api_client.cookies.set(REFRESH_COOKIE_NAME, raw_token)

    response = await api_client.post(LOGOUT_URL)

    assert response.content == b""
    assert raw_token not in response.text


async def test_reuse_revocation_survives_the_request_transaction() -> None:
    """Family revocation must be committed, not rolled back with the failed request.

    Uses a production-shaped session per request so the endpoint's own
    transaction boundary is what decides whether the revocation persists.
    """
    from httpx import ASGITransport

    from app.database.session import get_session
    from app.main import app

    engine = create_async_engine(get_settings().database_url, poolclass=NullPool)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    user_id: uuid.UUID | None = None

    async def _request_session():
        async with factory() as session:
            yield session

    app.dependency_overrides[get_session] = _request_session
    try:
        async with factory() as setup:
            user = User(
                email="reuse-probe@example.com", password_hash=hash_password(PASSWORD)
            )
            setup.add(user)
            await setup.flush()
            user_id = user.id
            issued = await issue_refresh_token(setup, user_id)
            raw_token = issued.raw_token
            family_id = issued.record.family_id
            await setup.commit()

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            client.cookies.set(REFRESH_COOKIE_NAME, raw_token)
            assert (await client.post(REFRESH_URL)).status_code == 200
            client.cookies.set(REFRESH_COOKIE_NAME, raw_token)
            assert (await client.post(REFRESH_URL)).status_code == 401

        async with factory() as check:
            unrevoked = await check.scalar(
                select(func.count())
                .select_from(RefreshToken)
                .where(
                    RefreshToken.family_id == family_id,
                    RefreshToken.revoked_at.is_(None),
                )
            )
        assert unrevoked == 0
    finally:
        app.dependency_overrides.pop(get_session, None)
        if user_id is not None:
            async with factory() as cleanup:
                await cleanup.execute(delete(User).where(User.id == user_id))
                await cleanup.commit()
        await engine.dispose()


async def test_logout_revokes_only_the_presented_token_within_its_family(
    api_client: AsyncClient, db_session: AsyncSession
) -> None:
    """Logout is token-scoped per ARCHITECTURE.md section 11.4, not family-scoped.

    Two live tokens are placed in one family so that token-scoped and
    family-scoped revocation give different outcomes.
    """
    user_id = await _user(db_session)
    presented = await issue_refresh_token(db_session, user_id)
    sibling = await issue_refresh_token(
        db_session, user_id, family_id=presented.record.family_id
    )
    await db_session.commit()
    api_client.cookies.set(REFRESH_COOKIE_NAME, presented.raw_token)

    assert (await api_client.post(LOGOUT_URL)).status_code == 204

    db_session.expunge_all()
    still_live = set(
        (
            await db_session.scalars(
                select(RefreshToken.token_hash).where(
                    RefreshToken.family_id == presented.record.family_id,
                    RefreshToken.revoked_at.is_(None),
                )
            )
        ).all()
    )

    assert still_live == {hash_refresh_token(sibling.raw_token)}
