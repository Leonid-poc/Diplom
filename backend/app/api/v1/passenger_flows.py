"""Замеры пассажиропотока."""
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.deps import get_current_user, get_db
from app.models.passenger_flow import PassengerFlow
from app.models.user import User
from app.schemas.passenger_flow import PassengerFlowCreate, PassengerFlowRead

router = APIRouter()


@router.get("", response_model=list[PassengerFlowRead])
def list_flows(
    period_days: int = Query(default=30, ge=1, le=365),
    route_id: int | None = None,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    since = datetime.now(timezone.utc) - timedelta(days=period_days)
    stmt = select(PassengerFlow).where(PassengerFlow.measured_at >= since)
    if route_id is not None:
        stmt = stmt.where(PassengerFlow.route_id == route_id)
    return db.execute(stmt.order_by(PassengerFlow.measured_at.desc())).scalars().all()


@router.post("", response_model=PassengerFlowRead, status_code=status.HTTP_201_CREATED)
def create_flow(
    payload: PassengerFlowCreate,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    obj = PassengerFlow(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj
