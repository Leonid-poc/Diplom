"""Движок маршрутизации: построение графа сети и поиск кратчайшего пути.

Соответствует разделу 1.5 ВКР («Выбор и обоснование методического аппарата»):
- алгоритм Дейкстры (Dijkstra): O((V + E) log V);
- алгоритм A* (A-star): эвристика — евклидово расстояние по координатам.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Iterable

import networkx as nx
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import RoutingError
from app.models.bus_stop import BusStop, BusStopConnection


@dataclass
class RouteResult:
    path: list[int]               # упорядоченные id остановок
    total_distance_km: float
    estimated_time_min: float


class RouteEngine:
    """Инкапсулирует работу с графом дорожной сети."""

    def __init__(self, edges: Iterable[tuple[int, int, float, float | None]]):
        """
        :param edges: iterable из (from_stop, to_stop, distance_km, avg_time_min|None)
        """
        self.graph = nx.DiGraph()
        for u, v, dist, t in edges:
            self.graph.add_edge(int(u), int(v), weight=float(dist), avg_time=t)

    # ---------- Класс-методы для загрузки из БД ----------

    @classmethod
    def from_db(cls, db: Session) -> "RouteEngine":
        rows = db.execute(
            select(
                BusStopConnection.from_stop,
                BusStopConnection.to_stop,
                BusStopConnection.distance,
                BusStopConnection.avg_time,
            )
        ).all()
        return cls((r[0], r[1], float(r[2]), float(r[3]) if r[3] is not None else None) for r in rows)

    # ---------- Алгоритмы поиска ----------

    def shortest_path(self, src: int, dst: int, algo: str = "dijkstra") -> RouteResult:
        if src not in self.graph or dst not in self.graph:
            raise RoutingError("Начальная или конечная остановка отсутствует в графе сети")
        if not nx.has_path(self.graph, src, dst):
            raise RoutingError("Между указанными остановками нет связности")

        if algo == "dijkstra":
            path = nx.shortest_path(self.graph, src, dst, weight="weight")
        elif algo == "astar":
            # эвристика построится позже из координат БД, либо нулевая
            path = nx.astar_path(self.graph, src, dst, weight="weight")
        else:
            raise RoutingError(f"Неизвестный алгоритм: {algo}")

        total_dist = self._total_length(path)
        # время: суммируем avg_time, если есть; иначе ~ 35 км/ч
        total_time = self._total_time(path) or (total_dist / 35.0) * 60.0
        return RouteResult(path=path, total_distance_km=total_dist, estimated_time_min=total_time)

    def _total_length(self, path: list[int]) -> float:
        return sum(self.graph[u][v]["weight"] for u, v in zip(path, path[1:]))

    def _total_time(self, path: list[int]) -> float | None:
        parts = [self.graph[u][v].get("avg_time") for u, v in zip(path, path[1:])]
        if any(p is None for p in parts):
            return None
        return float(sum(parts))


# ---------- Дополнительные расчёты ----------

def calc_required_vehicles(length_km: float, avg_vehicle_speed_kmh: float = 25.0) -> int:
    """Минимальное число ТС для маршрута заданной длины с интервалом 7 мин."""
    return max(1, math.ceil(length_km / max(avg_vehicle_speed_kmh / 7.0 * 1.0, 1.0)))


def calc_interval_min(length_km: float, time_min: float) -> int:
    """Интервал движения исходя из времени оборота и количества ТС."""
    vehicles = calc_required_vehicles(length_km)
    return max(3, round(time_min / max(vehicles, 1)))


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Расстояние между точками на сфере (приближение Земли)."""
    R = 6371.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def find_stops_along_route(
    polyline: list[tuple[float, float]],
    candidate_stops: list[tuple[int, float, float]],
    max_dist_m: float = 80.0,
    min_spacing_m: float = 200.0,
) -> list[tuple[int, int, float]]:
    """Найти остановки, попадающие на линию маршрута (с допуском max_dist_m).

    :param polyline: реальная геометрия маршрута [(lat, lon), …] (например, из OSRM)
    :param candidate_stops: список всех остановок [(stop_id, lat, lon), …]
    :param max_dist_m: максимальное расстояние от остановки до линии (в метрах)
    :param min_spacing_m: минимальный интервал между подобранными остановками
                          (фильтрует дубли «обе стороны улицы»)
    :returns: [(stop_id, vertex_index, distance_m), …] упорядочено вдоль маршрута
    """
    if len(polyline) < 2:
        return []

    # Bbox-прескрин: переводим max_dist_m в градусы (~ 1° ≈ 111 км)
    lats = [p[0] for p in polyline]
    lons = [p[1] for p in polyline]
    margin_deg = (max_dist_m / 111_000.0) * 2.0
    min_lat, max_lat = min(lats) - margin_deg, max(lats) + margin_deg
    min_lon, max_lon = min(lons) - margin_deg, max(lons) + margin_deg

    matches: list[tuple[int, int, float]] = []
    for stop_id, slat, slon in candidate_stops:
        # 1. быстрый bbox-фильтр
        if not (min_lat <= slat <= max_lat and min_lon <= slon <= max_lon):
            continue
        # 2. ближайшая вершина полилинии
        best_idx = -1
        best_km = float("inf")
        for i, (plat, plon) in enumerate(polyline):
            d = haversine_km(slat, slon, plat, plon)
            if d < best_km:
                best_km = d
                best_idx = i
        best_m = best_km * 1000.0
        if best_m <= max_dist_m:
            matches.append((stop_id, best_idx, best_m))

    # Сортируем по положению вдоль маршрута
    matches.sort(key=lambda x: x[1])

    # Прореживание: если две остановки слишком близко (например, обе стороны улицы)
    # — оставляем ту, что ближе к линии.
    filtered: list[tuple[int, int, float]] = []
    for m in matches:
        if not filtered:
            filtered.append(m)
            continue
        prev = filtered[-1]
        # Дистанция «вдоль маршрута» приближённо как разница позиций
        # (точнее можно через накопленные длины сегментов).
        approx_along_m = _segment_length_m(polyline, prev[1], m[1])
        if approx_along_m < min_spacing_m:
            # выбираем ту, что ближе к линии
            if m[2] < prev[2]:
                filtered[-1] = m
        else:
            filtered.append(m)
    return filtered


def _segment_length_m(polyline: list[tuple[float, float]], i: int, j: int) -> float:
    """Длина отрезка полилинии между вершинами i и j (в метрах)."""
    if i == j:
        return 0.0
    a, b = (i, j) if i < j else (j, i)
    total_km = 0.0
    for k in range(a, b):
        total_km += haversine_km(*polyline[k], *polyline[k + 1])
    return total_km * 1000.0
