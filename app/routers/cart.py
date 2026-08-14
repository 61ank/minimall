"""购物车路由（全部需登录）。"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models import User
from app.schemas.cart import AddCartRequest, CartItemOut, UpdateCartRequest
from app.services import cart as cart_service

router = APIRouter(prefix="/cart", tags=["cart"])


@router.get("", response_model=list[CartItemOut])
def get_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[CartItemOut]:
    return cart_service.list_cart(db, current_user.id)


@router.post("", response_model=CartItemOut, status_code=201)
def add_item(
    data: AddCartRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CartItemOut:
    return cart_service.add_to_cart(db, current_user.id, data)


@router.put("/{sku_id}", response_model=CartItemOut)
def update_item(
    sku_id: int,
    data: UpdateCartRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CartItemOut:
    return cart_service.update_cart_quantity(db, current_user.id, sku_id, data.quantity)


@router.delete("/{sku_id}", status_code=204)
def remove_item(
    sku_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    cart_service.remove_cart_item(db, current_user.id, sku_id)


@router.delete("", status_code=204)
def clear_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    cart_service.clear_cart(db, current_user.id)
