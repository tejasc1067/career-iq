"""Endpoints for the signed-in user's own account and profile."""

from fastapi import APIRouter, status
from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert

from app.auth.dependencies import CurrentUserDep
from app.database.session import SessionDep
from app.users.models import UserProfile
from app.users.schemas import CurrentUserRead, UserProfileRead, UserProfileUpdate

router = APIRouter(
    prefix="/api/users",
    tags=["users"],
    responses={status.HTTP_401_UNAUTHORIZED: {"description": "Not authenticated"}},
)


@router.get(
    "/me",
    response_model=CurrentUserRead,
    summary="Read the signed-in account and its profile",
)
async def read_current_user(
    user: CurrentUserDep, session: SessionDep
) -> CurrentUserRead:
    """Return the account the access token belongs to, and its profile if saved.

    A user who has never saved gets an empty profile rather than a 404, so the
    profile form has one shape to render.
    """
    profile = await session.scalar(
        select(UserProfile).where(UserProfile.user_id == user.id)
    )
    return CurrentUserRead(
        id=user.id,
        email=user.email,
        created_at=user.created_at,
        updated_at=user.updated_at,
        profile=(
            UserProfileRead.model_validate(profile)
            if profile is not None
            else UserProfileRead()
        ),
    )


@router.put(
    "/me/profile",
    response_model=UserProfileRead,
    summary="Replace the signed-in user's profile",
)
async def replace_current_user_profile(
    payload: UserProfileUpdate, user: CurrentUserDep, session: SessionDep
) -> UserProfile:
    """Insert or overwrite the profile owned by the token's subject.

    The owning `user_id` comes from the token, so the payload cannot direct the
    write at another account. The upsert is one statement, so a user saving
    twice at once cannot lose the race against their own unique index.
    """
    values = payload.model_dump()
    statement = (
        insert(UserProfile)
        .values(user_id=user.id, **values)
        .on_conflict_do_update(
            index_elements=[UserProfile.user_id],
            set_={**values, "updated_at": func.now()},
        )
        .returning(UserProfile)
    )
    profile = (await session.scalars(statement)).one()
    await session.commit()
    return profile
