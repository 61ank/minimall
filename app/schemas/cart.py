"""购物车请求/响应模型。"""
from decimal import Decimal

from pydantic import BaseModel, Field


class AddCartRequest(BaseModel):
    sku_id: int
    quantity: int = Field(default=1, ge=1, le=99)


class UpdateCartRequest(BaseModel):
    quantity: int = Field(ge=1, le=99)


class CartItemOut(BaseModel):
    sku_id: int
    sku_code: str
    sku_name: str
    product_id: int
    product_name: str
    price: Decimal
    quantity: int
    subtotal: Decimal
    stock_available: int
