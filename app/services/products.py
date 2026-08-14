"""商品与分类业务逻辑。"""
from typing import Any, Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.core.exceptions import AppError
from app.models import Category, Product, Sku
from app.schemas.product import ProductListItem

# 可直接排序的商品字段（白名单）；price 走 SKU 最低价子查询
SORTABLE = {"sales": Product.sales, "created_at": Product.created_at}


def list_categories(db: Session) -> list[Category]:
    return list(db.scalars(select(Category).order_by(Category.sort_order, Category.id)))


def list_products(
    db: Session,
    *,
    category_id: Optional[int] = None,
    q: Optional[str] = None,
    price_min: Optional[float] = None,
    price_max: Optional[float] = None,
    sort: str = "-sales",
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[ProductListItem], int]:
    page = max(page, 1)
    page_size = min(max(page_size, 1), 100)

    # SKU 最低价标量子查询：用于价格筛选、排序、列表展示
    min_price = (
        select(func.min(Sku.price)).where(Sku.product_id == Product.id).correlate(Product).scalar_subquery()
    )

    conditions = [Product.status == 1]  # 游客只见上架商品
    if category_id is not None:
        conditions.append(Product.category_id == category_id)
    if q:
        conditions.append(Product.name.like(f"%{q}%"))
    if price_min is not None:
        conditions.append(min_price >= price_min)
    if price_max is not None:
        conditions.append(min_price <= price_max)

    total = db.scalar(select(func.count()).select_from(Product).where(*conditions)) or 0

    order_by = _build_order_by(sort, min_price)
    rows = db.execute(
        select(Product, min_price.label("min_price"))
        .where(*conditions)
        .order_by(order_by)
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()

    items = []
    for product, price in rows:
        item = ProductListItem.model_validate(product)
        item.min_price = price
        items.append(item)
    return items, total


def get_product_detail(db: Session, product_id: int) -> Product:
    product = db.scalar(
        select(Product)
        .options(joinedload(Product.skus))
        .where(Product.id == product_id, Product.status == 1)
    )
    if product is None:
        raise AppError("PRODUCT_NOT_FOUND", "商品不存在或已下架", status_code=404)
    return product


def _build_order_by(sort: str, min_price: Any):
    descending = sort.startswith("-")
    key = sort.lstrip("-")
    if key == "price":
        column = min_price
    elif key in SORTABLE:
        column = SORTABLE[key]
    else:
        raise AppError("INVALID_SORT", f"不支持的排序字段: {key}", status_code=400)
    return column.desc() if descending else column.asc()
