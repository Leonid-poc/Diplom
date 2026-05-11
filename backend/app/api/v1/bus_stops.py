"""CRUD для остановочных пунктов."""
from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.deps import get_current_user, get_db
from app.models.bus_stop import BusStop
from app.models.user import User
from app.schemas.bus_stop import BusStopCreate, BusStopRead

router = APIRouter()


@router.get("", response_model=list[BusStopRead])
def list_stops(
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    return db.execute(select(BusStop).order_by(BusStop.name)).scalars().all()


@router.post("", response_model=BusStopRead, status_code=status.HTTP_201_CREATED)
def create_stop(
    payload: BusStopCreate,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    stop = BusStop(**payload.model_dump())
    db.add(stop)
    db.commit()
    db.refresh(stop)
    return stop


@router.get("/{stop_id}", response_model=BusStopRead)
def get_stop(stop_id: int, db: Session = Depends(get_db), _user: User = Depends(get_current_user)):
    stop = db.get(BusStop, stop_id)
    if not stop:
        raise NotFoundError("Остановка")
    return stop


@router.delete("/{stop_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_stop(stop_id: int, db: Session = Depends(get_db), _user: User = Depends(get_current_user)):
    stop = db.get(BusStop, stop_id)
    if not stop:
        raise NotFoundError("Остановка")
    db.delete(stop)
    db.commit()
