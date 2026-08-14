"""收藏夹请求/响应模型。"""
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class FavoriteCreateRequest(BaseModel):
    product_id: int = Field(ge=1)


class FavoriteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    product_name: str
    cover_image: Optional[str] = None
    min_price: Optional[Decimal] = None
    product_status: int
    favorited_at: datetime  # Favorite.created_at
