"""认证业务逻辑：注册、登录。"""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.core.security import hash_password, verify_password
from app.models import User
from app.schemas.auth import LoginRequest, RegisterRequest


def register_user(db: Session, data: RegisterRequest) -> User:
    if db.scalar(select(User).where(User.username == data.username)):
        raise AppError("USERNAME_TAKEN", "用户名已被占用", status_code=409)
    if data.email and db.scalar(select(User).where(User.email == data.email)):
        raise AppError("EMAIL_TAKEN", "邮箱已被占用", status_code=409)

    user = User(
        username=data.username,
        email=data.email,
        nickname=data.nickname,
        password_hash=hash_password(data.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, data: LoginRequest) -> User:
    user = db.scalar(select(User).where(User.username == data.username))
    if user is None or not verify_password(data.password, user.password_hash):
        raise AppError("INVALID_CREDENTIALS", "用户名或密码错误", status_code=401)
    if user.status != 1:
        raise AppError("ACCOUNT_DISABLED", "账号已被禁用", status_code=403)
    return user
