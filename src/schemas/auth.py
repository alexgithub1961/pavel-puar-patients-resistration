"""Authentication schemas."""

from pydantic import EmailStr

from src.schemas.base import BaseSchema


class LoginRequest(BaseSchema):
    """Login request payload."""

    email: EmailStr
    password: str


class TokenResponse(BaseSchema):
    """JWT token response."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseSchema):
    """Token refresh request."""

    refresh_token: str


class DemoLoginRequest(BaseSchema):
    """Demo login request payload."""

    role: str  # "new_patient", "regular_patient", or "doctor"
