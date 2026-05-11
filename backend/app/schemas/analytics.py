"""Схемы для аналитики и отчётов."""
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ClusterRequest(BaseModel):
    """Запрос на кластерный анализ маршрутов."""

    period_days: int = Field(default=30, ge=1, le=365)
    n_clusters: int = Field(default=4, ge=2, le=10)
    weights: list[float] | None = Field(
        default=None,
        description="Веса для признаков [длина, время, загрузка, поломки, интервал, неравн.]",
    )


class ClusterPoint(BaseModel):
    route_id: int
    route_number: str
    cluster: int
    efficiency: float
    features: list[float]


class ClusterResponse(BaseModel):
    points: list[ClusterPoint]
    centers: list[list[float]]
    n_clusters: int
    method: str = "k-means"


class AnalyticsReportRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    author_id: int | None = None
    payload: dict[str, Any]
    created_at: datetime
