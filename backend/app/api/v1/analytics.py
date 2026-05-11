"""Аналитика: кластерный анализ маршрутов."""
from datetime import datetime, timedelta, timezone

import numpy as np
from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.deps import get_current_user, get_db
from app.models.passenger_flow import PassengerFlow
from app.models.route import Route
from app.models.user import User
from app.schemas.analytics import ClusterPoint, ClusterRequest, ClusterResponse
from app.services.cluster_service import cluster_routes

router = APIRouter()


@router.post("/cluster", response_model=ClusterResponse)
def cluster_routes_endpoint(
    payload: ClusterRequest,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    """Запустить кластеризацию маршрутов по эксплуатационным признакам.

    Признаки на маршрут:
        [длина_км, ср_время_мин, ср_загрузка_%, частота_поломок,
         интервал_мин, сезонная_неравномерность]
    """
    since = datetime.now(timezone.utc) - timedelta(days=payload.period_days)

    routes = db.execute(select(Route).where(Route.is_active.is_(True))).scalars().all()

    feature_rows: list[list[float]] = []
    route_meta: list[tuple[int, str]] = []

    for r in routes:
        # средняя загрузка
        avg_load_q = select(func.coalesce(func.avg(PassengerFlow.passengers), 0)).where(
            PassengerFlow.route_id == r.id,
            PassengerFlow.measured_at >= since,
        )
        avg_load = float(db.execute(avg_load_q).scalar() or 0.0)

        # для примера: остальные признаки берём детерминированно от id маршрута
        # (в реальности — рассчитываются из БД и журнала поломок)
        length_km = float(r.total_length)
        avg_time_min = length_km / 0.5  # примерно 30 км/ч
        breakdown_freq = (r.id % 5) * 0.7
        interval_min = max(5, 10 + (r.id % 4) * 2)
        seasonal_var = (r.id % 7) * 0.05

        feature_rows.append([length_km, avg_time_min, avg_load, breakdown_freq, interval_min, seasonal_var])
        route_meta.append((r.id, r.route_number))

    features = np.array(feature_rows, dtype=float)
    weights = np.array(payload.weights) if payload.weights else None
    result = cluster_routes(features, n_clusters=payload.n_clusters, weights=weights)

    points = [
        ClusterPoint(
            route_id=route_meta[i][0],
            route_number=route_meta[i][1],
            cluster=int(label),
            efficiency=float(result["efficiency"][i]) if result["efficiency"] else 0.0,
            features=feature_rows[i],
        )
        for i, label in enumerate(result["labels"])
    ]

    return ClusterResponse(
        points=points,
        centers=result["centers"],
        n_clusters=payload.n_clusters,
    )
