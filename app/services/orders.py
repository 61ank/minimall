"""订单业务逻辑：下单事务、库存防超卖、状态机、取消回补。"""
import random
from datetime import datetime, timezone

from sqlalchemy import func, select, update
from sqlalchemy.orm import Session, selectinload

from app.core.exceptions import AppError
from app.models import (
    Address,
    CartItem,
    Inventory,
    Order,
    OrderItem,
    OrderStatus,
    Product,
    Sku,
    User,
)
from app.schemas.order import CreateOrderRequest

# 状态机白名单：key = 当前状态，value = 允许迁移到的状态集合
ORDER_TRANSITIONS: dict[OrderStatus, set[OrderStatus]] = {
    OrderStatus.PENDING: {OrderStatus.PAID, OrderStatus.CANCELED},
    OrderStatus.PAID: {OrderStatus.SHIPPED},
    OrderStatus.SHIPPED: {OrderStatus.COMPLETED},
    OrderStatus.COMPLETED: set(),
    OrderStatus.CANCELED: set(),
}

_STATUS_TIME_FIELD = {
    OrderStatus.PAID: "paid_at",
    OrderStatus.SHIPPED: "shipped_at",
    OrderStatus.COMPLETED: "completed_at",
    OrderStatus.CANCELED: "canceled_at",
}


def generate_order_no() -> str:
    """订单号：ORD + 时间戳 + 6 位随机（架构文档决策），唯一索引兜底防碰撞。"""
    ts = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"ORD{ts}{random.randint(0, 999999):06d}"


def create_order(db: Session, user: User, data: CreateOrderRequest) -> Order:
    """从购物车下单：一个事务内完成 校验→扣库存→建订单→写明细→清购物车。

    任一步失败整体回滚；防超卖靠条件更新（影响行数=1 才成功）。
    """
    address = db.get(Address, data.address_id)
    if address is None or address.user_id != user.id:
        raise AppError("ADDRESS_NOT_FOUND", "收货地址不存在", status_code=404)

    cart_items = db.scalars(select(CartItem).where(CartItem.user_id == user.id)).all()
    if not cart_items:
        raise AppError("EMPTY_CART", "购物车为空，无法下单", status_code=400)

    order = Order(
        order_no=generate_order_no(),
        user_id=user.id,
        address_id=address.id,
        receiver=address.receiver,
        phone=address.phone,
        address=" ".join([address.province, address.city, address.district, address.detail]),
        total_amount=0,
        status=OrderStatus.PENDING,
    )
    db.add(order)
    db.flush()

    total = 0
    for item in cart_items:
        sku = db.get(Sku, item.sku_id)
        if sku is None or sku.status != 1:
            raise AppError("SKU_NOT_FOUND", f"SKU {item.sku_id} 不存在或已停售", status_code=404)
        product = db.get(Product, sku.product_id)
        if product is None or product.status != 1:
            raise AppError("PRODUCT_OFF_SALE", "商品已下架", status_code=404)

        # 防超卖：条件更新，仅当库存充足才扣减；影响行数为 1 才算成功
        result = db.execute(
            update(Inventory)
            .where(Inventory.sku_id == item.sku_id, Inventory.available >= item.quantity)
            .values(available=Inventory.available - item.quantity)
        )
        if result.rowcount != 1:
            raise AppError("INSUFFICIENT_STOCK", "库存不足", status_code=409)

        subtotal = sku.price * item.quantity
        total += subtotal
        db.add(OrderItem(
            order_id=order.id,
            sku_id=item.sku_id,
            product_name=product.name,
            sku_name=sku.name,
            price=sku.price,
            quantity=item.quantity,
            subtotal=subtotal,
        ))

    order.total_amount = total
    for item in cart_items:
        db.delete(item)

    db.commit()
    return _load_order(db, order.id)


def list_orders(
    db: Session,
    user_id: int,
    status: OrderStatus | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[Order], int]:
    page = max(page, 1)
    page_size = min(max(page_size, 1), 100)
    conditions = [Order.user_id == user_id]
    if status is not None:
        conditions.append(Order.status == status)
    total = db.scalar(select(func.count()).select_from(Order).where(*conditions)) or 0
    orders = db.scalars(
        select(Order)
        .where(*conditions)
        .order_by(Order.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return list(orders), total


def get_order(db: Session, user_id: int, order_id: int) -> Order:
    return _get_owned_order(db, user_id, order_id)


def cancel_order(db: Session, user: User, order_id: int) -> Order:
    """取消订单（仅 PENDING→CANCELED）并回补库存。"""
    order = _get_owned_order(db, user.id, order_id)
    transition(db, order, OrderStatus.CANCELED)
    for item in order.items:
        db.execute(
            update(Inventory)
            .where(Inventory.sku_id == item.sku_id)
            .values(available=Inventory.available + item.quantity)
        )
    db.commit()
    return _load_order(db, order.id)


def ship_order(db: Session, user: User, order_id: int) -> Order:
    order = _get_owned_order(db, user.id, order_id)
    transition(db, order, OrderStatus.SHIPPED)
    db.commit()
    return _load_order(db, order.id)


def complete_order(db: Session, user: User, order_id: int) -> Order:
    order = _get_owned_order(db, user.id, order_id)
    transition(db, order, OrderStatus.COMPLETED)
    db.commit()
    return _load_order(db, order.id)


def transition(db: Session, order: Order, target: OrderStatus) -> None:
    """状态迁移：白名单校验，非法迁移抛 409；并记录迁移时刻。"""
    if target not in ORDER_TRANSITIONS[order.status]:
        raise AppError(
            "INVALID_STATUS_TRANSITION",
            f"不允许从 {order.status.value} 迁移到 {target.value}",
            status_code=409,
        )
    order.status = target
    field = _STATUS_TIME_FIELD.get(target)
    if field:
        setattr(order, field, datetime.now(timezone.utc))
    db.add(order)


def _get_owned_order(db: Session, user_id: int, order_id: int) -> Order:
    order = db.scalar(
        select(Order).options(selectinload(Order.items)).where(Order.id == order_id)
    )
    if order is None or order.user_id != user_id:
        raise AppError("ORDER_NOT_FOUND", "订单不存在", status_code=404)
    return order


def _load_order(db: Session, order_id: int) -> Order:
    order = db.scalar(
        select(Order).options(selectinload(Order.items)).where(Order.id == order_id)
    )
    if order is None:
        raise AppError("ORDER_NOT_FOUND", "订单不存在", status_code=404)
    return order
