"""Клиент к OSRM (Open Source Routing Machine) для расчёта маршрутов
по реальной дорожной сети OpenStreetMap.

По умолчанию используется публичный демо-сервер `router.project-osrm.org`.
Для production-нагрузок рекомендуется поднять собственный OSRM-инстанс
(см. https://github.com/Project-OSRM/osrm-backend).
"""
from __future__ import annotations

from dataclasses import dataclass

import httpx

from app.config import settings


@dataclass
class OsrmRoute:
    coordinates: list[tuple[float, float]]  # [(lat, lon), ...] для Leaflet
    distance_km: float
    duration_min: float


class OsrmRouter:
    def __init__(self, base_url: str | None = None, profile: str = "driving"):
        self.base_url = (base_url or settings.osrm_base_url).rstrip("/")
        self.profile = profile

    def route(
        self,
        waypoints: list[tuple[float, float]],
        timeout_s: float = 30.0,
    ) -> OsrmRoute:
        """Запросить маршрут через несколько точек.

        :param waypoints: список (lat, lon)
        :returns: OsrmRoute с реальной геометрией и метрикой
        """
        if len(waypoints) < 2:
            raise ValueError("Нужно минимум 2 точки для маршрутизации")

        # OSRM ожидает координаты в порядке lon,lat
        coords_str = ";".join(f"{lon},{lat}" for lat, lon in waypoints)
        url = f"{self.base_url}/route/v1/{self.profile}/{coords_str}"
        params = {
            "overview": "full",
            "geometries": "geojson",
            "steps": "false",
            "alternatives": "false",
        }

        with httpx.Client(timeout=timeout_s) as client:
            r = client.get(url, params=params)
            r.raise_for_status()
            data = r.json()

        if data.get("code") != "Ok" or not data.get("routes"):
            raise RuntimeError(f"OSRM не смог построить маршрут: {data.get('message')}")

        route = data["routes"][0]
        geojson = route["geometry"]["coordinates"]  # [[lon, lat], ...]
        # Преобразуем в формат Leaflet: [lat, lon]
        coords = [(lat, lon) for lon, lat in geojson]

        return OsrmRoute(
            coordinates=coords,
            distance_km=route["distance"] / 1000.0,
            duration_min=route["duration"] / 60.0,
        )


def get_osrm_router() -> OsrmRouter:
    return OsrmRouter()
