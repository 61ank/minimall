"""MiniMall 精简电商平台 — 应用入口。

启动方式（在项目根目录）：
    uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
"""
import logging

from fastapi import FastAPI

from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import setup_logging
from app.routers import auth, cart, categories, health, orders, payments, products, users

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """应用工厂：便于测试时创建隔离实例。"""
    setup_logging(settings.log_level)
    logger.info("初始化 %s 应用（env=%s）", settings.app_name, settings.app_env)

    application = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description="精简电商平台后端 API",
    )

    register_exception_handlers(application)
    application.include_router(health.router)
    application.include_router(auth.router)
    application.include_router(users.router)
    application.include_router(categories.router)
    application.include_router(products.router)
    application.include_router(cart.router)
    application.include_router(orders.router)
    application.include_router(payments.router)

    return application


app = create_app()
