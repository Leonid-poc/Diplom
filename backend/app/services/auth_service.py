"""Сервис аутентификации."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import CredentialsError
from app.core.security import create_access_token, verify_password
from app.models.user import User
from app.config import settings


def authenticate(db: Session, login: str, password: str) -> tuple[User, str, int]:
    """Проверить логин/пароль и выпустить JWT.

    :returns: (user, access_token, expires_in_minutes)
    """
    user = db.execute(select(User).where(User.login == login)).scalar_one_or_none()
    if user is None or not verify_password(password, user.hashed_password):
        raise CredentialsError("Неверный логин или пароль")
    if not user.is_active:
        raise CredentialsError("Учётная запись отключена")

    token = create_access_token(subject=user.id, extra={"role": user.role.value})
    return user, token, settings.jwt_access_token_expire_minutes
