"""Pydantic v2 — схемы запросов и ответов."""
from app.schemas.auth import LoginRequest, TokenResponse, UserPublic
from app.schemas.bus_stop import (
    BusStopCreate,
    BusStopRead,
    BusStopConnectionCreate,
    BusStopConnectionRead,
)
from app.schemas.route import (
    RouteCreate,
    RouteRead,
    RouteBuildRequest,
    RouteBuildResponse,
)
from app.schemas.vehicle import (
    VehicleTypeCreate,
    VehicleTypeRead,
    VehicleModelCreate,
    VehicleModelRead,
    VehicleCreate,
    VehicleRead,
)
from app.schemas.passenger_flow import (
    PassengerFlowCreate,
    PassengerFlowRead,
)
from app.schemas.analytics import (
    ClusterRequest,
    ClusterResponse,
    AnalyticsReportRead,
)

__all__ = [
    "LoginRequest", "TokenResponse", "UserPublic",
    "BusStopCreate", "BusStopRead",
    "BusStopConnectionCreate", "BusStopConnectionRead",
    "RouteCreate", "RouteRead", "RouteBuildRequest", "RouteBuildResponse",
    "VehicleTypeCreate", "VehicleTypeRead",
    "VehicleModelCreate", "VehicleModelRead",
    "VehicleCreate", "VehicleRead",
    "PassengerFlowCreate", "PassengerFlowRead",
    "ClusterRequest", "ClusterResponse", "AnalyticsReportRead",
]
