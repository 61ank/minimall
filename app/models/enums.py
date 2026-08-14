"""业务枚举（落库为 VARCHAR 可读字符串）。"""
from enum import Enum


class OrderStatus(str, Enum):
    PENDING = "PENDING"        # 待支付
    PAID = "PAID"              # 已支付
    SHIPPED = "SHIPPED"        # 已发货
    COMPLETED = "COMPLETED"    # 已完成
    CANCELED = "CANCELED"      # 已取消


class PaymentStatus(str, Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
