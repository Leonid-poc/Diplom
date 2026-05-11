"""Сводный роутер API v1."""
from fastapi import APIRouter

from app.api.v1 import (
    analytics,
    auth,
    bus_stops,
    connections,
    health,
    passenger_flows,
    reports,
    routes,
    vehicles,
)

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(routes.router, prefix="/routes", tags=["routes"])
api_router.include_router(bus_stops.router, prefix="/bus_stops", tags=["bus_stops"])
api_router.include_router(connections.router, prefix="/connections", tags=["connections"])
api_router.include_router(vehicles.router, prefix="/vehicles", tags=["vehicles"])
api_router.include_router(
    passenger_flows.router, prefix="/passenger_flows", tags=["passenger_flows"]
)
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
