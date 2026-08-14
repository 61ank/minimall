"""安全相关：密码哈希、JWT 签发与校验、当前用户依赖。"""
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import InvalidTokenError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.exceptions import AppError
from app.models import User

bearer_scheme = HTTPBearer(auto_error=False)


def hash_password(plain: str) -> str:
    """对明文密码做 bcrypt 哈希，返回可入库的字符串。"""
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """校验明文与哈希是否匹配。"""
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except ValueError:
        return False


def create_access_token(user_id: int) -> str:
    """签发 access token，sub 为 user_id，含过期时间。"""
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> Optional[int]:
    """解析 token 返回 user_id；无效/过期返回 None。"""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
    except InvalidTokenError:
        return None
    sub = payload.get("sub")
    if sub is None:
        return None
    return int(sub)


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """FastAPI 依赖：校验 Bearer token 并返回当前用户，失败抛 401。"""
    if credentials is None:
        raise AppError("UNAUTHORIZED", "未登录或缺少令牌", status_code=401)
    user_id = decode_access_token(credentials.credentials)
    if user_id is None:
        raise AppError("UNAUTHORIZED", "令牌无效或已过期", status_code=401)
    user = db.get(User, user_id)
    if user is None or user.status != 1:
        raise AppError("UNAUTHORIZED", "用户不存在或已被禁用", status_code=401)
    return user
