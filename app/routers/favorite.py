"""收藏夹路由（全部需登录）。"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models import User
from app.schemas.common import Page
from app.schemas.favorite import FavoriteCreateRequest, FavoriteOut
from app.services import favorite as favorite_service

router = APIRouter(prefix="/favorites", tags=["favorites"])


@router.post("", response_model=FavoriteOut)
def add_favorite(
    data: FavoriteCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FavoriteOut:
    return favorite_service.add_favorite(db, current_user.id, data.product_id)


@router.get("", response_model=Page[FavoriteOut])
def list_favorites(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Page[FavoriteOut]:
    items, total = favorite_service.list_favorites(
        db, current_user.id, page=page, page_size=page_size
    )
    return Page[FavoriteOut](items=items, total=total, page=page, page_size=page_size)


@router.delete("/{product_id}", status_code=204)
def remove_favorite(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    favorite_service.remove_favorite(db, current_user.id, product_id)
