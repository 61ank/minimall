"""订单与支付请求/响应模型。"""
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.enums import OrderStatus, PaymentStatus


class CreateOrderRequest(BaseModel):
    address_id: int


class OrderItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sku_id: int
    product_name: str
    sku_name: str
    price: Decimal
    quantity: int
    subtotal: Decimal


class OrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_no: str
    receiver: str
    phone: str
    address: str
    total_amount: Decimal
    status: OrderStatus
    paid_at: Optional[datetime] = None
    shipped_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    canceled_at: Optional[datetime] = None
    created_at: datetime
    items: list[OrderItemOut] = []


class OrderListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_no: str
    total_amount: Decimal
    status: OrderStatus
    created_at: datetime


class PaymentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_id: int
    pay_no: str
    amount: Decimal
    status: PaymentStatus
    channel: str
