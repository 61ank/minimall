"""分类路由（公开读）。"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.product import CategoryOut
from app.services import products as product_service

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=list[CategoryOut])
def list_categories(db: Session = Depends(get_db)) -> list[CategoryOut]:
    return [CategoryOut.model_validate(c) for c in product_service.list_categories(db)]
