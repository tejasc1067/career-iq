"""Authentication endpoints."""

from fastapi import APIRouter, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.auth.password import hash_password, verify_password
from app.auth.refresh import issue_refresh_token
from app.auth.schemas import AccessTokenResponse, LoginRequest
from app.auth.tokens import create_access_token
from app.common.config import Settings, get_settings
from app.database.session import SessionDep
from app.users.models import User
from app.users.schemas import UserCreate, UserRead

router = APIRouter(prefix="/api/auth", tags=["auth"])

DUPLICATE_EMAIL_DETAIL = "An account with this email address already exists."
INVALID_CREDENTIALS_DETAIL = "Incorrect email address or password."
REFRESH_COOKIE_NAME = "refresh_token"
REFRESH_COOKIE_PATH = "/api/auth"
SECONDS_PER_DAY = 86400
ABSENT_USER_PASSWORD_HASH = hash_password("credential probe placeholder")


@router.post(
    "/signup",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a CareerIQ account",
    responses={status.HTTP_409_CONFLICT: {"description": "Email already registered"}},
)
async def signup(payload: UserCreate, session: SessionDep) -> User:
    """Create a user from a normalized email and a hashed password.

    The unique index on `users.email` stays authoritative: the pre-check below
    only turns the common case into a clean 409, and a concurrent insert that
    slips past it is caught as an IntegrityError.
    """
    if await session.scalar(select(User.id).where(User.email == payload.email)):
        raise HTTPException(status.HTTP_409_CONFLICT, DUPLICATE_EMAIL_DETAIL)

    user = User(email=payload.email, password_hash=hash_password(payload.password))
    session.add(user)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, DUPLICATE_EMAIL_DETAIL) from None

    return user


@router.post(
    "/login",
    response_model=AccessTokenResponse,
    summary="Exchange credentials for an access token",
    responses={status.HTTP_401_UNAUTHORIZED: {"description": "Invalid credentials"}},
)
async def login(
    payload: LoginRequest, response: Response, session: SessionDep
) -> AccessTokenResponse:
    """Verify credentials, then issue an access token and a refresh cookie.

    An unknown email is verified against a placeholder hash so that both
    failure modes cost the same Argon2 work and cannot be told apart by timing.
    """
    settings = get_settings()
    found = (
        await session.execute(
            select(User.id, User.password_hash).where(User.email == payload.email)
        )
    ).one_or_none()
    await session.rollback()

    user_id, password_hash = found if found else (None, ABSENT_USER_PASSWORD_HASH)
    password_matches = verify_password(payload.password, password_hash)
    if user_id is None or not password_matches:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, INVALID_CREDENTIALS_DETAIL)

    issued = await issue_refresh_token(session, user_id, settings=settings)
    await session.commit()

    _set_refresh_cookie(response, issued.raw_token, settings)
    return AccessTokenResponse(
        access_token=create_access_token(user_id, settings),
        expires_in=settings.access_token_expire_minutes * 60,
    )


def _set_refresh_cookie(response: Response, raw_token: str, settings: Settings) -> None:
    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=raw_token,
        max_age=settings.refresh_token_expire_days * SECONDS_PER_DAY,
        path=REFRESH_COOKIE_PATH,
        httponly=True,
        secure=True,
        samesite="lax",
    )
