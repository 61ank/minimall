"""鉴权相关请求/响应模型。"""
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.user import UserOut


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_]+$")
    password: str = Field(min_length=6, max_length=128)
    email: Optional[str] = Field(default=None, max_length=100)
    nickname: Optional[str] = Field(default=None, max_length=50)


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    access_token: str
    token_type: str = "bearer"
    user: UserOut
