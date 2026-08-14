"""通用响应模型。"""
from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    """分页响应：{items, total, page, page_size}（架构文档约定）。"""

    items: list[T]
    total: int
    page: int
    page_size: int
