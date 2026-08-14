"""用户与地址业务逻辑。"""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.models import Address, User
from app.schemas.user import AddressCreateRequest, UserUpdateRequest


def update_user(db: Session, user: User, data: UserUpdateRequest) -> User:
    if data.email is not None:
        exists = db.scalar(select(User).where(User.email == data.email, User.id != user.id))
        if exists:
            raise AppError("EMAIL_TAKEN", "邮箱已被占用", status_code=409)
        user.email = data.email
    if data.nickname is not None:
        user.nickname = data.nickname
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def list_addresses(db: Session, user_id: int) -> list[Address]:
    return list(
        db.scalars(
            select(Address).where(Address.user_id == user_id).order_by(Address.is_default.desc(), Address.id)
        )
    )


def create_address(db: Session, user_id: int, data: AddressCreateRequest) -> Address:
    if data.is_default:
        _clear_default(db, user_id)
    address = Address(user_id=user_id, **data.model_dump())
    db.add(address)
    db.commit()
    db.refresh(address)
    return address


def update_address(db: Session, user_id: int, address_id: int, data: AddressCreateRequest) -> Address:
    address = _get_owned_address(db, user_id, address_id)
    if data.is_default:
        _clear_default(db, user_id)
    for field, value in data.model_dump().items():
        setattr(address, field, value)
    db.add(address)
    db.commit()
    db.refresh(address)
    return address


def delete_address(db: Session, user_id: int, address_id: int) -> None:
    address = _get_owned_address(db, user_id, address_id)
    db.delete(address)
    db.commit()


def _get_owned_address(db: Session, user_id: int, address_id: int) -> Address:
    address = db.get(Address, address_id)
    if address is None or address.user_id != user_id:
        raise AppError("ADDRESS_NOT_FOUND", "地址不存在", status_code=404)
    return address


def _clear_default(db: Session, user_id: int) -> None:
    for addr in db.scalars(select(Address).where(Address.user_id == user_id, Address.is_default.is_(True))):
        addr.is_default = False
