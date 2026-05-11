"""Интеграция с внешней информационной системой (ВИС) муниципалитета.

В дипломе ВИС обеспечивает: импорт реестра маршрутов и остановок,
импорт пассажиропотока, экспорт утверждённых проектов маршрутов.
Здесь реализована заглушка-клиент. Реальная интеграция зависит от ВИС.
"""
from __future__ import annotations

from typing import Any

import httpx

from app.config import settings


class VisClient:
    """HTTP-клиент к ВИС. Используется бэкендом для интеграции."""

    def __init__(self, base_url: str | None = None, api_key: str | None = None):
        self.base_url = base_url or settings.vis_base_url
        self.api_key = api_key or settings.vis_api_key
        self._headers = {"X-API-Key": self.api_key} if self.api_key else {}

    async def fetch_bus_stops(self) -> list[dict[str, Any]]:
        """Получить реестр остановочных пунктов от ВИС."""
        if not self.base_url:
            return []  # ВИС не сконфигурирована
        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.get(f"{self.base_url}/bus-stops", headers=self._headers)
            r.raise_for_status()
            return r.json()

    async def fetch_passenger_flows(self, period_days: int = 30) -> list[dict[str, Any]]:
        """Получить замеры пассажиропотока за указанный период."""
        if not self.base_url:
            return []
        async with httpx.AsyncClient(timeout=60.0) as client:
            r = await client.get(
                f"{self.base_url}/passenger-flows",
                params={"period_days": period_days},
                headers=self._headers,
            )
            r.raise_for_status()
            return r.json()

    async def push_route(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Отправить утверждённый проект маршрута во ВИС."""
        if not self.base_url:
            return {"status": "skipped", "reason": "VIS not configured"}
        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.post(
                f"{self.base_url}/routes",
                json=payload,
                headers=self._headers,
            )
            r.raise_for_status()
            return r.json()


def get_vis_client() -> VisClient:
    return VisClient()
