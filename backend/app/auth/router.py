"""Authentication endpoints."""

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.auth.password import hash_password
from app.database.session import SessionDep
from app.users.models import User
from app.users.schemas import UserCreate, UserRead

router = APIRouter(prefix="/api/auth", tags=["auth"])

DUPLICATE_EMAIL_DETAIL = "An account with this email address already exists."


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
