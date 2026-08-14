"""支付路由（需登录；真实支付回调会走服务端签名校验，此处为模拟）。"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models import User
from app.schemas.order import OrderOut, PaymentOut
from app.services import payments as payment_service

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/{order_no}", response_model=PaymentOut)
def create_payment(
    order_no: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PaymentOut:
    return PaymentOut.model_validate(payment_service.create_payment(db, current_user.id, order_no))


@router.post("/{order_no}/callback", response_model=OrderOut)
def payment_callback(
    order_no: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> OrderOut:
    return OrderOut.model_validate(payment_service.payment_callback(db, current_user.id, order_no))
