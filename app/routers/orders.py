"""订单路由（全部需登录）。"""
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models import OrderStatus, User
from app.schemas.common import Page
from app.schemas.order import CreateOrderRequest, OrderListItem, OrderOut
from app.services import orders as order_service

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("", response_model=OrderOut, status_code=201)
def create_order(
    data: CreateOrderRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> OrderOut:
    return OrderOut.model_validate(order_service.create_order(db, current_user, data))


@router.get("", response_model=Page[OrderListItem])
def list_orders(
    status: Optional[OrderStatus] = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Page[OrderListItem]:
    orders, total = order_service.list_orders(db, current_user.id, status, page, page_size)
    return Page[OrderListItem](
        items=[OrderListItem.model_validate(o) for o in orders],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{order_id}", response_model=OrderOut)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> OrderOut:
    return OrderOut.model_validate(order_service.get_order(db, current_user.id, order_id))


@router.post("/{order_id}/cancel", response_model=OrderOut)
def cancel_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> OrderOut:
    return OrderOut.model_validate(order_service.cancel_order(db, current_user, order_id))


@router.post("/{order_id}/ship", response_model=OrderOut)
def ship_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> OrderOut:
    return OrderOut.model_validate(order_service.ship_order(db, current_user, order_id))


@router.post("/{order_id}/complete", response_model=OrderOut)
def complete_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> OrderOut:
    return OrderOut.model_validate(order_service.complete_order(db, current_user, order_id))
