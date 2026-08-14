"""商品/分类相关响应模型。"""
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict


class CategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    parent_id: Optional[int] = None
    sort_order: int


class SkuOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sku_code: str
    name: str
    price: Decimal
    status: int


class ProductListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    cover_image: Optional[str] = None
    category_id: int
    sales: int
    min_price: Optional[Decimal] = None


class ProductDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: Optional[str] = None
    cover_image: Optional[str] = None
    category_id: int
    sales: int
    created_at: datetime
    skus: list[SkuOut]
