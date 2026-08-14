"""用户与地址请求/响应模型。"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: Optional[str] = None
    nickname: Optional[str] = None
    created_at: datetime


class UserUpdateRequest(BaseModel):
    email: Optional[str] = Field(default=None, max_length=100)
    nickname: Optional[str] = Field(default=None, max_length=50)


class AddressCreateRequest(BaseModel):
    receiver: str = Field(min_length=1, max_length=50)
    phone: str = Field(min_length=5, max_length=20)
    province: str = Field(min_length=1, max_length=50)
    city: str = Field(min_length=1, max_length=50)
    district: str = Field(min_length=1, max_length=50)
    detail: str = Field(min_length=1, max_length=200)
    is_default: bool = False


class AddressOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    receiver: str
    phone: str
    province: str
    city: str
    district: str
    detail: str
    is_default: bool
