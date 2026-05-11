"""Unit-тесты движка маршрутизации."""
import pytest

from app.core.exceptions import RoutingError
from app.services.route_engine import (
    RouteEngine,
    calc_interval_min,
    calc_required_vehicles,
    haversine_km,
)


def make_simple_engine() -> RouteEngine:
    # 1 -> 2 -> 3 (длинный путь), 1 -> 3 (короткий)
    edges = [
        (1, 2, 5.0, 10.0),
        (2, 3, 5.0, 10.0),
        (1, 3, 7.0, 14.0),
        (3, 1, 7.0, 14.0),
    ]
    return RouteEngine(edges)


def test_dijkstra_finds_shortest():
    engine = make_simple_engine()
    res = engine.shortest_path(1, 3, algo="dijkstra")
    assert res.path == [1, 3]
    assert res.total_distance_km == pytest.approx(7.0)
    assert res.estimated_time_min == pytest.approx(14.0)


def test_astar_finds_shortest():
    engine = make_simple_engine()
    res = engine.shortest_path(1, 3, algo="astar")
    assert res.path == [1, 3]


def test_missing_node_raises():
    engine = make_simple_engine()
    with pytest.raises(RoutingError):
        engine.shortest_path(1, 999)


def test_no_path_raises():
    # 4 — изолированная вершина
    engine = RouteEngine([(1, 2, 1.0, None), (3, 4, 1.0, None)])
    with pytest.raises(RoutingError):
        engine.shortest_path(1, 4)


def test_required_vehicles_min_one():
    assert calc_required_vehicles(0.1) == 1
    assert calc_required_vehicles(50.0) >= 1


def test_interval_min_floor():
    assert calc_interval_min(10.0, 40.0) >= 3


def test_haversine_known_distance():
    # Москва — Санкт-Петербург ≈ 635 км
    d = haversine_km(55.7558, 37.6173, 59.9343, 30.3351)
    assert 620 < d < 700
