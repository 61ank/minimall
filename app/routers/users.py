"""用户路由：个人资料与收货地址（需登录）。"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models import User
from app.schemas.user import AddressCreateRequest, AddressOut, UserOut, UserUpdateRequest
from app.services import users as user_service

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)) -> UserOut:
    return UserOut.model_validate(current_user)


@router.put("/me", response_model=UserOut)
def update_me(
    data: UserUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserOut:
    return UserOut.model_validate(user_service.update_user(db, current_user, data))


@router.get("/me/addresses", response_model=list[AddressOut])
def list_addresses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[AddressOut]:
    return [AddressOut.model_validate(a) for a in user_service.list_addresses(db, current_user.id)]


@router.post("/me/addresses", response_model=AddressOut, status_code=201)
def create_address(
    data: AddressCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AddressOut:
    return AddressOut.model_validate(user_service.create_address(db, current_user.id, data))


@router.put("/me/addresses/{address_id}", response_model=AddressOut)
def update_address(
    address_id: int,
    data: AddressCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AddressOut:
    return AddressOut.model_validate(user_service.update_address(db, current_user.id, address_id, data))


@router.delete("/me/addresses/{address_id}", status_code=204)
def delete_address(
    address_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    user_service.delete_address(db, current_user.id, address_id)
