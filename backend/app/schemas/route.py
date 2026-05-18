"""Схемы для маршрутов."""
from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class RouteCreate(BaseModel):
    route_number: str = Field(..., max_length=10)
    name: str = Field(..., max_length=120)
    type: str = Field(default="городской", max_length=20)
    total_length: Decimal = Field(..., gt=0)
    is_active: bool = True
    description: str | None = None
    geometry: list[list[float]] = Field(default_factory=list)  # [[lat, lon], ...]
    estimated_time_min: float | None = None
    algorithm: str | None = None
    stop_ids: list[int] = Field(default_factory=list)


class RouteStopRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    order_num: int
    stop_id: int


class RouteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    route_number: str
    name: str
    type: str
    total_length: Decimal
    is_active: bool
    description: str | None = None
    geometry: list[list[float]] = Field(default_factory=list)
    estimated_time_min: float | None = None
    algorithm: str | None = None
    created_at: datetime
    updated_at: datetime


class RouteStopDetail(BaseModel):
    """Остановка в составе маршрута с координатами."""
    model_config = ConfigDict(from_attributes=True)

    stop_id: int
    name: str
    lat: float
    lon: float
    order_num: int


class RouteDetailRead(BaseModel):
    """Расширенная карточка маршрута со списком остановок."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    route_number: str
    name: str
    type: str
    total_length: Decimal
    is_active: bool
    description: str | None = None
    geometry: list[list[float]] = Field(default_factory=list)
    estimated_time_min: float | None = None
    algorithm: str | None = None
    created_at: datetime
    updated_at: datetime
    stops: list[RouteStopDetail] = Field(default_factory=list)


# ----- Расчёт маршрута -----

class RouteBuildRequest(BaseModel):
    start_stop_id: int
    end_stop_id: int
    algorithm: Literal["dijkstra", "astar", "osrm"] = "osrm"
    via_stop_ids: list[int] = Field(default_factory=list)  # промежуточные точки
    # Радиус (метры): остановки в пределах этого расстояния от линии маршрута
    # будут добавлены автоматически. Используется только для OSRM.
    snap_radius_m: float = Field(default=80.0, ge=10.0, le=500.0)
    # Минимальный интервал между подобранными остановками (фильтр «двойников»)
    min_stop_spacing_m: float = Field(default=200.0, ge=50.0, le=2000.0)


class MatchedStop(BaseModel):
    """Остановка, подобранная вдоль построенного маршрута."""
    id: int
    name: str
    lat: float
    lon: float
    distance_from_route_m: float = 0.0   # отклонение от линии


class RouteBuildResponse(BaseModel):
    path: list[int]                              # id остановок по порядку следования
    matched_stops: list[MatchedStop] = []        # подробная инфа об остановках вдоль линии
    geometry: list[list[float]] = []             # [[lat, lon], ...] реальной дороги
    total_distance_km: float
    estimated_time_min: float
    required_vehicles: int
    interval_min: int
    algorithm: str
    source: Literal["osrm", "graph"] = "graph"   # откуда геометрия
