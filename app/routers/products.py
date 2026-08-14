"""商品路由（公开读）：列表（筛选/分页/排序）、详情。"""
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.common import Page
from app.schemas.product import ProductDetail, ProductListItem
from app.services import products as product_service

router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=Page[ProductListItem])
def list_products(
    category_id: Optional[int] = None,
    q: Optional[str] = Query(default=None, max_length=100),
    price_min: Optional[float] = None,
    price_max: Optional[float] = None,
    sort: str = "-sales",
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> Page[ProductListItem]:
    items, total = product_service.list_products(
        db,
        category_id=category_id,
        q=q,
        price_min=price_min,
        price_max=price_max,
        sort=sort,
        page=page,
        page_size=page_size,
    )
    return Page[ProductListItem](items=items, total=total, page=page, page_size=page_size)


@router.get("/{product_id}", response_model=ProductDetail)
def get_product(product_id: int, db: Session = Depends(get_db)) -> ProductDetail:
    return product_service.get_product_detail(db, product_id)
