"""数据库连接与会话管理（同步 SQLAlchemy 2.0）。"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

engine = create_engine(
    settings.db_url,
    pool_pre_ping=True,   # 取连接前校验，避免取到失效连接
    pool_recycle=3600,    # 连接复用上限 1 小时，规避 MySQL wait_timeout
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db():
    """FastAPI 依赖：为每个请求提供一个数据库会话，请求结束关闭。"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
