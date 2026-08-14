"""购物车业务逻辑：用户专属资源 + 库存校验。"""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.models import CartItem, Inventory, Product, Sku
from app.schemas.cart import AddCartRequest, CartItemOut

MAX_QUANTITY = 99


def add_to_cart(db: Session, user_id: int, data: AddCartRequest) -> CartItemOut:
    _assert_purchasable(db, data.sku_id)
    stock = _get_stock(db, data.sku_id)

    existing = db.scalar(
        select(CartItem).where(CartItem.user_id == user_id, CartItem.sku_id == data.sku_id)
    )
    if existing:
        new_quantity = existing.quantity + data.quantity
        if new_quantity > MAX_QUANTITY:
            raise AppError("QUANTITY_EXCEEDS", f"单个商品数量不能超过 {MAX_QUANTITY}", status_code=400)
        if new_quantity > stock:
            raise AppError("INSUFFICIENT_STOCK", "库存不足", status_code=409)
        existing.quantity = new_quantity
        db.add(existing)
        db.commit()
        db.refresh(existing)
        item = existing
    else:
        if data.quantity > stock:
            raise AppError("INSUFFICIENT_STOCK", "库存不足", status_code=409)
        item = CartItem(user_id=user_id, sku_id=data.sku_id, quantity=data.quantity)
        db.add(item)
        db.commit()
        db.refresh(item)
    return _to_out(db, item)


def update_cart_quantity(db: Session, user_id: int, sku_id: int, quantity: int) -> CartItemOut:
    _assert_purchasable(db, sku_id)
    item = _get_owned_item(db, user_id, sku_id)
    if quantity > _get_stock(db, sku_id):
        raise AppError("INSUFFICIENT_STOCK", "库存不足", status_code=409)
    item.quantity = quantity
    db.add(item)
    db.commit()
    db.refresh(item)
    return _to_out(db, item)


def remove_cart_item(db: Session, user_id: int, sku_id: int) -> None:
    item = _get_owned_item(db, user_id, sku_id)
    db.delete(item)
    db.commit()


def clear_cart(db: Session, user_id: int) -> None:
    items = db.scalars(select(CartItem).where(CartItem.user_id == user_id)).all()
    for item in items:
        db.delete(item)
    db.commit()


def list_cart(db: Session, user_id: int) -> list[CartItemOut]:
    rows = db.execute(
        select(CartItem, Sku, Product, Inventory)
        .join(Sku, Sku.id == CartItem.sku_id)
        .join(Product, Product.id == Sku.product_id)
        .outerjoin(Inventory, Inventory.sku_id == Sku.id)
        .where(CartItem.user_id == user_id)
        .order_by(CartItem.id)
    ).all()
    return [
        CartItemOut(
            sku_id=item.sku_id,
            sku_code=sku.sku_code,
            sku_name=sku.name,
            product_id=product.id,
            product_name=product.name,
            price=sku.price,
            quantity=item.quantity,
            subtotal=sku.price * item.quantity,
            stock_available=inv.available if inv else 0,
        )
        for item, sku, product, inv in rows
    ]


def _assert_purchasable(db: Session, sku_id: int) -> None:
    """校验 SKU 存在、在售、且所属商品上架。"""
    sku = db.get(Sku, sku_id)
    if sku is None or sku.status != 1:
        raise AppError("SKU_NOT_FOUND", "SKU 不存在或已停售", status_code=404)
    product = db.get(Product, sku.product_id)
    if product is None or product.status != 1:
        raise AppError("PRODUCT_OFF_SALE", "商品已下架", status_code=404)


def _get_stock(db: Session, sku_id: int) -> int:
    inventory = db.scalar(select(Inventory).where(Inventory.sku_id == sku_id))
    return inventory.available if inventory else 0


def _get_owned_item(db: Session, user_id: int, sku_id: int) -> CartItem:
    item = db.scalar(select(CartItem).where(CartItem.user_id == user_id, CartItem.sku_id == sku_id))
    if item is None:
        raise AppError("CART_ITEM_NOT_FOUND", "购物车中不存在该商品", status_code=404)
    return item


def _to_out(db: Session, item: CartItem) -> CartItemOut:
    """单个购物车项 → 响应模型（含 SKU/商品/库存信息）。"""
    sku = db.get(Sku, item.sku_id)
    product = db.get(Product, sku.product_id)
    stock = _get_stock(db, item.sku_id)
    return CartItemOut(
        sku_id=item.sku_id,
        sku_code=sku.sku_code,
        sku_name=sku.name,
        product_id=product.id,
        product_name=product.name,
        price=sku.price,
        quantity=item.quantity,
        subtotal=sku.price * item.quantity,
        stock_available=stock,
    )
