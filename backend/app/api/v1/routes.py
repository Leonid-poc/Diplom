"""Маршруты: CRUD + расчёт оптимального пути."""
from decimal import Decimal

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.deps import get_current_user, get_db
from app.models.bus_stop import BusStopRoute
from app.models.route import Route
from app.models.user import User
from app.schemas.route import (
    RouteBuildRequest,
    RouteBuildResponse,
    RouteCreate,
    RouteRead,
)
from app.services.route_engine import (
    RouteEngine,
    calc_interval_min,
    calc_required_vehicles,
)

router = APIRouter()


# ---------- CRUD ----------

@router.get("", response_model=list[RouteRead])
def list_routes(db: Session = Depends(get_db), _user: User = Depends(get_current_user)):
    return db.execute(select(Route).order_by(Route.route_number)).scalars().all()


@router.post("", response_model=RouteRead, status_code=status.HTTP_201_CREATED)
def create_route(
    payload: RouteCreate,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    data = payload.model_dump(exclude={"stop_ids"})
    route = Route(**data)
    db.add(route)
    db.flush()

    for order_num, stop_id in enumerate(payload.stop_ids, start=1):
        db.add(BusStopRoute(route_id=route.id, stop_id=stop_id, order_num=order_num))

    db.commit()
    db.refresh(route)
    return route


@router.get("/{route_id}", response_model=RouteRead)
def get_route(route_id: int, db: Session = Depends(get_db), _user: User = Depends(get_current_user)):
    route = db.get(Route, route_id)
    if not route:
        raise NotFoundError("Маршрут")
    return route


@router.delete("/{route_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_route(route_id: int, db: Session = Depends(get_db), _user: User = Depends(get_current_user)):
    route = db.get(Route, route_id)
    if not route:
        raise NotFoundError("Маршрут")
    db.delete(route)
    db.commit()


# ---------- Построение оптимального пути ----------

@router.post("/build", response_model=RouteBuildResponse)
def build_route(
    payload: RouteBuildRequest,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    engine = RouteEngine.from_db(db)
    result = engine.shortest_path(
        src=payload.start_stop_id,
        dst=payload.end_stop_id,
        algo=payload.algorithm,
    )
    length = result.total_distance_km
    time = result.estimated_time_min
    return RouteBuildResponse(
        path=result.path,
        total_distance_km=round(length, 2),
        estimated_time_min=round(time, 1),
        required_vehicles=calc_required_vehicles(length),
        interval_min=calc_interval_min(length, time),
        algorithm=payload.algorithm,
    )
