"""Рёбра графа дорожной сети (связи между остановками)."""
from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.deps import get_current_user, get_db
from app.models.bus_stop import BusStopConnection
from app.models.user import User
from app.schemas.bus_stop import BusStopConnectionCreate, BusStopConnectionRead

router = APIRouter()


@router.get("", response_model=list[BusStopConnectionRead])
def list_connections(
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    return db.execute(select(BusStopConnection)).scalars().all()


@router.post("", response_model=BusStopConnectionRead, status_code=status.HTTP_201_CREATED)
def create_connection(
    payload: BusStopConnectionCreate,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    conn = BusStopConnection(**payload.model_dump())
    db.add(conn)
    db.commit()
    db.refresh(conn)
    return conn


@router.delete("/{conn_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_connection(
    conn_id: int,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    conn = db.get(BusStopConnection, conn_id)
    if not conn:
        raise NotFoundError("Связь между остановками")
    db.delete(conn)
    db.commit()
