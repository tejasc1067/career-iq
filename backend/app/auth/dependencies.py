"""Protected-endpoint dependency.

Resolves the caller's identity from the access token alone, per
ARCHITECTURE.md section 12. No route may take a user identifier from the
request and use it to decide whose data it touches.
"""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.auth.tokens import InvalidAccessTokenError, decode_access_token
from app.database.session import SessionDep
from app.users.models import User

NOT_AUTHENTICATED_DETAIL = "Authentication is required."

bearer_scheme = HTTPBearer(auto_error=False)


def _not_authenticated() -> HTTPException:
    """Build the single rejection used for every authentication failure.

    Missing, malformed, expired, and forged tokens are indistinguishable to a
    caller, so a probe learns nothing about which accounts exist.
    """
    return HTTPException(
        status.HTTP_401_UNAUTHORIZED,
        NOT_AUTHENTICATED_DETAIL,
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    session: SessionDep,
) -> User:
    """Return the user named by the `sub` claim of a valid access token."""
    if credentials is None:
        raise _not_authenticated()

    try:
        user_id = decode_access_token(credentials.credentials)
    except InvalidAccessTokenError:
        raise _not_authenticated() from None

    user = await session.get(User, user_id)
    if user is None:
        raise _not_authenticated()

    return user


CurrentUserDep = Annotated[User, Depends(get_current_user)]
