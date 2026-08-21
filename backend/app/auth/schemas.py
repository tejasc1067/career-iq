"""Authentication API schemas."""

from pydantic import BaseModel, EmailStr, field_validator

from app.users.schemas import normalize_email


class LoginRequest(BaseModel):
    """Login credentials."""

    email: EmailStr
    password: str

    @field_validator("email", mode="before")
    @classmethod
    def _normalize_email(cls, value: object) -> object:
        return normalize_email(value) if isinstance(value, str) else value


class AccessTokenResponse(BaseModel):
    """A newly issued access token. The refresh token travels only as a cookie."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int
