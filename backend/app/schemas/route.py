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
    created_at: datetime
    updated_at: datetime


# ----- Расчёт маршрута -----

class RouteBuildRequest(BaseModel):
    start_stop_id: int
    end_stop_id: int
    algorithm: Literal["dijkstra", "astar"] = "dijkstra"


class RouteBuildResponse(BaseModel):
    path: list[int]
    total_distance_km: float
    estimated_time_min: float
    required_vehicles: int
    interval_min: int
    algorithm: str
