"""收藏夹业务逻辑：用户专属资源 + 商品上架校验 + 幂等/并发安全。"""
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.models import Favorite, Product, Sku
from app.schemas.favorite import FavoriteOut


def _min_price_subquery():
    return (
        select(func.min(Sku.price))
        .where(Sku.product_id == Product.id)
        .correlate(Product)
        .scalar_subquery()
    )


def add_favorite(db: Session, user_id: int, product_id: int) -> FavoriteOut:
    existing = db.scalar(
        select(Favorite).where(Favorite.user_id == user_id, Favorite.product_id == product_id)
    )
    if existing:
        return _to_out(db, existing)

    _assert_on_sale(db, product_id)

    favorite = Favorite(user_id=user_id, product_id=product_id)
    db.add(favorite)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        existing = db.scalar(
            select(Favorite).where(Favorite.user_id == user_id, Favorite.product_id == product_id)
        )
        if existing is None:
            raise AppError("FAVORITE_CONFLICT", "收藏操作冲突，请重试", status_code=409)
        return _to_out(db, existing)
    db.refresh(favorite)
    return _to_out(db, favorite)


def list_favorites(
    db: Session, user_id: int, *, page: int = 1, page_size: int = 20
) -> tuple[list[FavoriteOut], int]:
    page = max(page, 1)
    page_size = min(max(page_size, 1), 100)

    total = (
        db.scalar(
            select(func.count())
            .select_from(Favorite)
            .join(Product, Product.id == Favorite.product_id)
            .where(Favorite.user_id == user_id)
        )
        or 0
    )

    min_price = _min_price_subquery()
    rows = db.execute(
        select(Favorite, Product, min_price.label("min_price"))
        .join(Product, Product.id == Favorite.product_id)
        .where(Favorite.user_id == user_id)
        .order_by(Favorite.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()

    items = [
        FavoriteOut(
            id=fav.id,
            product_id=product.id,
            product_name=product.name,
            cover_image=product.cover_image,
            min_price=price,
            product_status=product.status,
            favorited_at=fav.created_at,
        )
        for fav, product, price in rows
    ]
    return items, total


def remove_favorite(db: Session, user_id: int, product_id: int) -> None:
    favorite = db.scalar(
        select(Favorite).where(Favorite.user_id == user_id, Favorite.product_id == product_id)
    )
    if favorite is None:
        raise AppError("FAVORITE_NOT_FOUND", "收藏不存在", status_code=404)
    db.delete(favorite)
    db.commit()


def _assert_on_sale(db: Session, product_id: int) -> None:
    product = db.scalar(select(Product).where(Product.id == product_id, Product.status == 1))
    if product is None:
        raise AppError("PRODUCT_NOT_FOUND", "商品不存在或已下架", status_code=404)


def _to_out(db: Session, favorite: Favorite) -> FavoriteOut:
    product = db.get(Product, favorite.product_id)
    if product is None:
        raise AppError("PRODUCT_NOT_FOUND", "商品不存在", status_code=404)
    min_price = db.scalar(
        select(func.min(Sku.price)).where(Sku.product_id == favorite.product_id)
    )
    return FavoriteOut(
        id=favorite.id,
        product_id=favorite.product_id,
        product_name=product.name,
        cover_image=product.cover_image,
        min_price=min_price,
        product_status=product.status,
        favorited_at=favorite.created_at,
    )
