"""Маршруты: CRUD + расчёт оптимального пути."""
from decimal import Decimal

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError, RoutingError
from app.deps import get_current_user, get_db
from app.models.bus_stop import BusStop, BusStopRoute
from app.models.route import Route
from app.models.user import User
from app.schemas.route import (
    RouteBuildRequest,
    RouteBuildResponse,
    RouteCreate,
    RouteRead,
)
from app.schemas.route import MatchedStop
from app.services.osrm_router import OsrmRouter
from app.services.route_engine import (
    RouteEngine,
    calc_interval_min,
    calc_required_vehicles,
    find_stops_along_route,
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
    """Построить маршрут.

    Два режима:
    1. `osrm` (по умолчанию) — маршрут по реальным дорогам через OSRM.
       Использует координаты остановок и возвращает полилинию реальной траектории.
    2. `dijkstra` / `astar` — поиск по графу `bus_stop_connections` в БД.
       Возвращает упорядоченный список остановок.
    """
    start = db.get(BusStop, payload.start_stop_id)
    end = db.get(BusStop, payload.end_stop_id)
    if not start or not end:
        raise NotFoundError("Остановка")

    if payload.algorithm == "osrm":
        # Реальная маршрутизация по OSM/OSRM
        waypoints: list[tuple[float, float]] = [(float(start.lat), float(start.lon))]
        for vid in payload.via_stop_ids:
            via = db.get(BusStop, vid)
            if via:
                waypoints.append((float(via.lat), float(via.lon)))
        waypoints.append((float(end.lat), float(end.lon)))

        try:
            osrm = OsrmRouter()
            osrm_res = osrm.route(waypoints)
        except Exception as e:
            raise RoutingError(f"OSRM-маршрутизация недоступна: {e}")

        length = osrm_res.distance_km
        time = osrm_res.duration_min

        # --- Подбор остановок вдоль построенного маршрута ---
        all_stops = db.execute(select(BusStop)).scalars().all()
        candidate = [(s.id, float(s.lat), float(s.lon)) for s in all_stops]
        matched = find_stops_along_route(
            osrm_res.coordinates,
            candidate,
            max_dist_m=payload.snap_radius_m,
            min_spacing_m=payload.min_stop_spacing_m,
        )
        stop_by_id = {s.id: s for s in all_stops}

        # Гарантируем, что start и end попали в path (даже если стоят чуть дальше радиуса)
        ordered_ids: list[int] = []
        for stop_id, _idx, _d in matched:
            if stop_id not in ordered_ids:
                ordered_ids.append(stop_id)
        if start.id not in ordered_ids:
            ordered_ids.insert(0, start.id)
        elif ordered_ids[0] != start.id:
            ordered_ids.remove(start.id)
            ordered_ids.insert(0, start.id)
        if end.id not in ordered_ids:
            ordered_ids.append(end.id)
        elif ordered_ids[-1] != end.id:
            ordered_ids.remove(end.id)
            ordered_ids.append(end.id)

        dist_by_id = {m[0]: m[2] for m in matched}
        matched_stops = [
            MatchedStop(
                id=sid,
                name=stop_by_id[sid].name,
                lat=float(stop_by_id[sid].lat),
                lon=float(stop_by_id[sid].lon),
                distance_from_route_m=round(dist_by_id.get(sid, 0.0), 1),
            )
            for sid in ordered_ids
            if sid in stop_by_id
        ]

        return RouteBuildResponse(
            path=ordered_ids,
            matched_stops=matched_stops,
            geometry=[[lat, lon] for lat, lon in osrm_res.coordinates],
            total_distance_km=round(length, 2),
            estimated_time_min=round(time, 1),
            required_vehicles=calc_required_vehicles(length),
            interval_min=calc_interval_min(length, time),
            algorithm=payload.algorithm,
            source="osrm",
        )

    # Fallback на локальный граф связности
    engine = RouteEngine.from_db(db)
    result = engine.shortest_path(
        src=payload.start_stop_id,
        dst=payload.end_stop_id,
        algo=payload.algorithm,
    )
    length = result.total_distance_km
    time = result.estimated_time_min

    # Геометрия из БД-остановок маршрута
    stop_rows = {s.id: s for s in db.execute(select(BusStop)).scalars().all()}
    geometry = [[float(stop_rows[i].lat), float(stop_rows[i].lon)] for i in result.path if i in stop_rows]

    return RouteBuildResponse(
        path=result.path,
        geometry=geometry,
        total_distance_km=round(length, 2),
        estimated_time_min=round(time, 1),
        required_vehicles=calc_required_vehicles(length),
        interval_min=calc_interval_min(length, time),
        algorithm=payload.algorithm,
        source="graph",
    )
