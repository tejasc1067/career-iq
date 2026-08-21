"""Tests for access-token creation and validation."""

import uuid
from datetime import UTC, datetime, timedelta

import jwt
import pytest
from pydantic import SecretStr

from app.auth.tokens import (
    ACCESS_TOKEN_TYPE,
    REQUIRED_CLAIMS,
    InvalidAccessTokenError,
    create_access_token,
    decode_access_token,
)
from app.common.config import Settings, get_settings

USER_ID = uuid.uuid4()


def _claims(token: str, settings: Settings | None = None) -> dict:
    """Read a token's claims without enforcing expiry, for inspection only."""
    settings = settings or get_settings()
    return jwt.decode(
        token,
        settings.jwt_secret.get_secret_value(),
        algorithms=[settings.jwt_algorithm],
        options={"verify_exp": False},
    )


def _settings(**overrides: object) -> Settings:
    """Settings derived from the live configuration, with fields overridden.

    `model_copy` skips validation, so a plain-string secret is wrapped here to
    match the SecretStr the real settings carry.
    """
    if isinstance(overrides.get("jwt_secret"), str):
        overrides["jwt_secret"] = SecretStr(overrides["jwt_secret"])
    return get_settings().model_copy(update=overrides)


def test_access_token_is_created() -> None:
    """Creating a token yields a three-part JWS string."""
    token = create_access_token(USER_ID)

    assert isinstance(token, str)
    assert token.count(".") == 2


def test_subject_is_the_user_id() -> None:
    """`sub` carries the user UUID as a string."""
    assert _claims(create_access_token(USER_ID))["sub"] == str(USER_ID)


def test_token_type_is_access() -> None:
    """`type` marks the token as an access token."""
    assert _claims(create_access_token(USER_ID))["type"] == ACCESS_TOKEN_TYPE


def test_every_required_claim_is_present() -> None:
    """All claims required by ARCHITECTURE.md section 11.1 are set."""
    claims = _claims(create_access_token(USER_ID))

    for claim in REQUIRED_CLAIMS:
        assert claim in claims, claim


def test_no_personal_information_is_embedded() -> None:
    """The token carries only the documented claims."""
    claims = _claims(create_access_token(USER_ID))

    assert set(claims) == set(REQUIRED_CLAIMS)
    for forbidden in ("email", "password", "password_hash", "name"):
        assert forbidden not in claims


def test_expiry_matches_the_configured_lifetime() -> None:
    """`exp - iat` equals the configured lifetime rather than a hardcoded value."""
    settings = get_settings()
    claims = _claims(create_access_token(USER_ID))

    lifetime = claims["exp"] - claims["iat"]

    assert lifetime == settings.access_token_expire_minutes * 60


def test_configured_lifetime_is_honoured_when_changed() -> None:
    """The lifetime is read from settings, not baked into the implementation."""
    settings = _settings(access_token_expire_minutes=1)
    claims = _claims(create_access_token(USER_ID, settings), settings)

    assert claims["exp"] - claims["iat"] == 60


def test_jti_is_unique_across_tokens() -> None:
    """Each token gets its own identifier."""
    jtis = {_claims(create_access_token(USER_ID))["jti"] for _ in range(25)}

    assert len(jtis) == 25


def test_token_is_signed_with_the_configured_settings() -> None:
    """The token verifies under the configured secret and algorithm."""
    settings = get_settings()
    token = create_access_token(USER_ID)

    header = jwt.get_unverified_header(token)
    assert header["alg"] == settings.jwt_algorithm

    assert _claims(token)["sub"] == str(USER_ID)
    with pytest.raises(jwt.InvalidSignatureError):
        jwt.decode(
            token, "a-completely-different-signing-key", algorithms=[header["alg"]]
        )


def test_valid_token_decodes_to_the_subject() -> None:
    """A freshly issued token validates and returns its subject."""
    assert decode_access_token(create_access_token(USER_ID)) == USER_ID


def test_expired_token_is_rejected() -> None:
    """A token past its expiry fails validation."""
    settings = get_settings()
    past = datetime.now(UTC) - timedelta(minutes=30)
    expired = jwt.encode(
        {
            "sub": str(USER_ID),
            "iat": past,
            "exp": past + timedelta(minutes=15),
            "type": ACCESS_TOKEN_TYPE,
            "jti": uuid.uuid4().hex,
        },
        settings.jwt_secret.get_secret_value(),
        algorithm=settings.jwt_algorithm,
    )

    with pytest.raises(InvalidAccessTokenError):
        decode_access_token(expired)


def test_token_signed_with_another_key_is_rejected() -> None:
    """A forged signature fails validation."""
    forged = create_access_token(USER_ID, _settings(jwt_secret="x" * 48))

    with pytest.raises(InvalidAccessTokenError):
        decode_access_token(forged)


@pytest.mark.parametrize(
    "malformed",
    ["", "not-a-token", "a.b", "a.b.c", "....", "Bearer sometoken"],
)
def test_malformed_token_is_rejected(malformed: str) -> None:
    """Structurally invalid input fails validation without raising a library error."""
    with pytest.raises(InvalidAccessTokenError):
        decode_access_token(malformed)


@pytest.mark.parametrize("omitted", REQUIRED_CLAIMS)
def test_token_missing_a_required_claim_is_rejected(omitted: str) -> None:
    """Dropping any single required claim fails validation."""
    settings = get_settings()
    now = datetime.now(UTC)
    claims = {
        "sub": str(USER_ID),
        "iat": now,
        "exp": now + timedelta(minutes=15),
        "type": ACCESS_TOKEN_TYPE,
        "jti": uuid.uuid4().hex,
    }
    del claims[omitted]
    token = jwt.encode(
        claims, settings.jwt_secret.get_secret_value(), algorithm=settings.jwt_algorithm
    )

    with pytest.raises(InvalidAccessTokenError):
        decode_access_token(token)


@pytest.mark.parametrize("wrong_type", ["refresh", "id", "", "ACCESS", None])
def test_wrong_token_type_is_rejected(wrong_type: object) -> None:
    """Only `type == "access"` is accepted."""
    settings = get_settings()
    now = datetime.now(UTC)
    token = jwt.encode(
        {
            "sub": str(USER_ID),
            "iat": now,
            "exp": now + timedelta(minutes=15),
            "type": wrong_type,
            "jti": uuid.uuid4().hex,
        },
        settings.jwt_secret.get_secret_value(),
        algorithm=settings.jwt_algorithm,
    )

    with pytest.raises(InvalidAccessTokenError):
        decode_access_token(token)


@pytest.mark.parametrize("subject", ["", "not-a-uuid", "12345"])
def test_non_uuid_subject_is_rejected(subject: str) -> None:
    """A subject that is not a UUID fails validation."""
    settings = get_settings()
    now = datetime.now(UTC)
    token = jwt.encode(
        {
            "sub": subject,
            "iat": now,
            "exp": now + timedelta(minutes=15),
            "type": ACCESS_TOKEN_TYPE,
            "jti": uuid.uuid4().hex,
        },
        settings.jwt_secret.get_secret_value(),
        algorithm=settings.jwt_algorithm,
    )

    with pytest.raises(InvalidAccessTokenError):
        decode_access_token(token)


def test_failure_leaks_neither_the_secret_nor_the_token() -> None:
    """The raised error must not carry the token, its claims, or the signing key."""
    secret = get_settings().jwt_secret.get_secret_value()
    token = create_access_token(USER_ID, _settings(jwt_secret="y" * 48))

    with pytest.raises(InvalidAccessTokenError) as caught:
        decode_access_token(token)

    rendered = f"{caught.value!r} {caught.value!s} {caught.value.args}"
    assert secret not in rendered
    assert token not in rendered
    assert str(USER_ID) not in rendered
    assert caught.value.args == ()
    assert caught.value.__cause__ is None


def test_secret_is_masked_in_settings_output() -> None:
    """The signing key must not appear in a repr or a model dump."""
    settings = get_settings()
    secret = settings.jwt_secret.get_secret_value()

    assert secret not in repr(settings)
    assert secret not in str(settings)
    assert secret not in str(settings.model_dump())
