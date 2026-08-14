"""模型统一导出：导入本模块即注册全部表到 Base.metadata。"""
from app.models.base import Base
from app.models.cart import CartItem
from app.models.enums import OrderStatus, PaymentStatus
from app.models.order import Order, OrderItem, PaymentRecord
from app.models.product import Category, Inventory, Product, Sku
from app.models.user import Address, User

__all__ = [
    "Address",
    "Base",
    "CartItem",
    "Category",
    "Inventory",
    "Order",
    "OrderItem",
    "OrderStatus",
    "PaymentRecord",
    "PaymentStatus",
    "Product",
    "Sku",
    "User",
]
