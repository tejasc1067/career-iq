"""Access token creation and validation.

Stateless signed JWTs, per ARCHITECTURE.md section 11.1. Nothing here touches
the database: resolving the subject to a User belongs to the protected-endpoint
dependency.
"""

import uuid
from datetime import UTC, datetime, timedelta

import jwt

from app.common.config import Settings, get_settings

ACCESS_TOKEN_TYPE = "access"
REQUIRED_CLAIMS = ("sub", "iat", "exp", "type", "jti")


class InvalidAccessTokenError(Exception):
    """Raised when an access token cannot be trusted.

    Carries no detail deliberately. Callers translate it into a generic
    authentication failure so that neither the token, the claims, nor the
    signing configuration reaches a client or a log line.
    """


def create_access_token(user_id: uuid.UUID, settings: Settings | None = None) -> str:
    """Return a signed access JWT whose subject is `user_id`."""
    settings = settings or get_settings()
    issued_at = datetime.now(UTC)
    claims = {
        "sub": str(user_id),
        "iat": issued_at,
        "exp": issued_at + timedelta(minutes=settings.access_token_expire_minutes),
        "type": ACCESS_TOKEN_TYPE,
        "jti": uuid.uuid4().hex,
    }
    return jwt.encode(
        claims,
        settings.jwt_secret.get_secret_value(),
        algorithm=settings.jwt_algorithm,
    )


def decode_access_token(token: str, settings: Settings | None = None) -> uuid.UUID:
    """Return the subject of a valid access token.

    Verifies the signature, the expiry, the presence of every required claim,
    and the token type. Any failure raises `InvalidAccessTokenError`.
    """
    settings = settings or get_settings()
    try:
        claims = jwt.decode(
            token,
            settings.jwt_secret.get_secret_value(),
            algorithms=[settings.jwt_algorithm],
            options={"require": list(REQUIRED_CLAIMS)},
        )
    except jwt.PyJWTError:
        raise InvalidAccessTokenError from None

    if claims.get("type") != ACCESS_TOKEN_TYPE:
        raise InvalidAccessTokenError

    try:
        return uuid.UUID(claims["sub"])
    except (KeyError, TypeError, ValueError):
        raise InvalidAccessTokenError from None
