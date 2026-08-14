"""支付业务逻辑：模拟支付发起与回调（幂等）。"""
import random
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.models import Order, OrderStatus, PaymentRecord, PaymentStatus
from app.services.orders import transition


def generate_pay_no() -> str:
    ts = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"PAY{ts}{random.randint(0, 999999):06d}"


def create_payment(db: Session, user_id: int, order_no: str) -> PaymentRecord:
    """发起支付：生成 mock 支付单；已存在则幂等返回。"""
    order = db.scalar(select(Order).where(Order.order_no == order_no))
    if order is None or order.user_id != user_id:
        raise AppError("ORDER_NOT_FOUND", "订单不存在", status_code=404)
    if order.status != OrderStatus.PENDING:
        raise AppError("ORDER_NOT_PAYABLE", "订单当前状态不可支付", status_code=409)

    existing = db.scalar(select(PaymentRecord).where(PaymentRecord.order_id == order.id))
    if existing:
        return existing  # 幂等：已存在支付单，直接返回

    record = PaymentRecord(
        order_id=order.id,
        pay_no=generate_pay_no(),
        amount=order.total_amount,
        status=PaymentStatus.PENDING,
        channel="mock",
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def payment_callback(db: Session, user_id: int, order_no: str) -> Order:
    """模拟支付回调：支付单置成功、订单 PENDING→PAID；重复回调幂等。"""
    order = db.scalar(select(Order).where(Order.order_no == order_no))
    if order is None or order.user_id != user_id:
        raise AppError("ORDER_NOT_FOUND", "订单不存在", status_code=404)

    record = db.scalar(select(PaymentRecord).where(PaymentRecord.order_id == order.id))
    if record is None:
        raise AppError("PAYMENT_NOT_FOUND", "未找到支付单", status_code=404)

    if record.status == PaymentStatus.SUCCESS:
        return order  # 幂等：已支付成功，不重复处理

    record.status = PaymentStatus.SUCCESS
    record.paid_at = datetime.now(timezone.utc)
    transition(db, order, OrderStatus.PAID)
    db.commit()
    db.refresh(order)
    return order
