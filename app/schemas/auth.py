from pydantic import BaseModel, EmailStr
from typing import Optional


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class AdminInfo(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    is_admin: bool

    model_config = {"from_attributes": True}
