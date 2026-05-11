"""Зависимости FastAPI: сессия БД и текущий пользователь."""
from typing import Generator

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.exceptions import CredentialsError
from app.core.security import decode_token
from app.database import SessionLocal
from app.models.user import User


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    try:
        payload = decode_token(token)
        user_id = int(payload.get("sub"))
    except (JWTError, ValueError, TypeError):
        raise CredentialsError()

    user = db.get(User, user_id)
    if user is None or not user.is_active:
        raise CredentialsError("Пользователь не найден или неактивен")
    return user
