"""Pydantic 请求/响应模型层。"""
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from app.schemas.common import Page
from app.schemas.product import (
    CategoryOut,
    ProductDetail,
    ProductListItem,
    SkuOut,
)
from app.schemas.user import (
    AddressCreateRequest,
    AddressOut,
    UserOut,
    UserUpdateRequest,
)

__all__ = [
    "AddressCreateRequest",
    "AddressOut",
    "CategoryOut",
    "LoginRequest",
    "Page",
    "ProductDetail",
    "ProductListItem",
    "RegisterRequest",
    "SkuOut",
    "TokenResponse",
    "UserOut",
    "UserUpdateRequest",
]
