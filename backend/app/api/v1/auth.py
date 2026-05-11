"""Авторизация и текущий пользователь."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse, UserPublic
from app.services.auth_service import authenticate

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    _user, token, ttl = authenticate(db, payload.login, payload.password)
    return TokenResponse(access_token=token, expires_in=ttl)


@router.get("/me", response_model=UserPublic)
def me(current: User = Depends(get_current_user)) -> User:
    return current
