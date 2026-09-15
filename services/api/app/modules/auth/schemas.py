import uuid
from typing import Literal

from pydantic import BaseModel, EmailStr, Field

# Field Staff and Admin are provisioned internally (seeded), not self-registered.
SelfRegisterRole = Literal["owner", "tenant"]


class RegisterRequest(BaseModel):
    full_name: str = Field(min_length=1, max_length=255)
    email: EmailStr
    password: str = Field(min_length=8, max_length=255)
    role: SelfRegisterRole


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
    role: str


class UserOut(BaseModel):
    id: uuid.UUID
    email: str | None
    full_name: str | None
    role: str

    model_config = {"from_attributes": True}
