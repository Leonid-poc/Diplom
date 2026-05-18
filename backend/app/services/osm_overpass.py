"""Клиент к OpenStreetMap Overpass API для получения данных об остановках.

Overpass — публичный читающий API над OSM, бесплатный, без API-ключей.
"""
from __future__ import annotations

import time
from typing import Any

import httpx


# Список зеркал Overpass — пробуем по очереди, если основной не отвечает.
OVERPASS_MIRRORS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://lz4.overpass-api.de/api/interpreter",
    "https://z.overpass-api.de/api/interpreter",
]
DEFAULT_OVERPASS_URL = OVERPASS_MIRRORS[0]

# Overpass требует осмысленный User-Agent; без него часть инстансов отвечает 406/429.
REQUEST_HEADERS = {
    "User-Agent": "pis-marshrut/1.0 (OSU diploma; +https://github.com/example/pis-marshrut)",
    "Accept": "application/json,text/plain;q=0.9,*/*;q=0.1",
    "Accept-Encoding": "gzip, deflate",
}


def build_query_by_admin_name(city_name: str, admin_level: int = 6) -> str:
    """Запрос к Overpass: ищет все bus_stop / tram_stop / trolleybus_stop
    внутри административной области с указанным названием.
    """
    return f"""
    [out:json][timeout:60];
    area["name"="{city_name}"]["admin_level"="{admin_level}"]->.searchArea;
    (
      node["highway"="bus_stop"](area.searchArea);
      node["public_transport"="platform"](area.searchArea);
      node["railway"="tram_stop"](area.searchArea);
    );
    out body;
    """


def build_query_by_bbox(south: float, west: float, north: float, east: float) -> str:
    """Запрос по прямоугольнику координат — fallback, если area не сработает."""
    return f"""
    [out:json][timeout:60];
    (
      node["highway"="bus_stop"]({south},{west},{north},{east});
      node["public_transport"="platform"]({south},{west},{north},{east});
      node["railway"="tram_stop"]({south},{west},{north},{east});
    );
    out body;
    """


def _post_one(url: str, query: str, timeout_s: float) -> dict[str, Any]:
    """Один запрос к конкретному Overpass-инстансу."""
    with httpx.Client(timeout=timeout_s, headers=REQUEST_HEADERS, follow_redirects=True) as client:
        r = client.post(url, data={"data": query})
        r.raise_for_status()
        return r.json()


def fetch_stops(
    query: str,
    overpass_url: str | None = None,
    timeout_s: float = 90.0,
) -> list[dict[str, Any]]:
    """Выполнить Overpass-запрос и вернуть нормализованный список остановок.

    Пробует список зеркал, если основной хост возвращает 4xx/5xx.
    Возвращает: [{name, lat, lon, osm_id, address, has_pavilion}, ...]
    """
    urls = [overpass_url] if overpass_url else OVERPASS_MIRRORS
    last_error: Exception | None = None
    data: dict[str, Any] | None = None

    for i, url in enumerate(urls):
        try:
            data = _post_one(url, query, timeout_s)
            break
        except httpx.HTTPStatusError as e:
            last_error = e
            # 4xx (кроме 429) — менять зеркало не поможет
            if e.response.status_code in (400, 401, 403, 404):
                raise
            print(f"[!] Overpass mirror {url} вернул {e.response.status_code}, пробую следующий…")
            time.sleep(1.5)
        except (httpx.TimeoutException, httpx.ConnectError, httpx.NetworkError) as e:
            last_error = e
            print(f"[!] Overpass mirror {url} недоступен ({type(e).__name__}), пробую следующий…")
            time.sleep(1.5)

    if data is None:
        assert last_error is not None
        raise last_error

    elements = data.get("elements", [])
    stops: list[dict[str, Any]] = []
    seen_names: set[str] = set()

    for el in elements:
        if el.get("type") != "node":
            continue
        tags = el.get("tags") or {}
        name = (tags.get("name") or tags.get("name:ru") or "").strip()
        if not name:
            continue  # пропускаем безымянные

        # Простая дедупликация по названию
        if name in seen_names:
            continue
        seen_names.add(name)

        lat = el.get("lat")
        lon = el.get("lon")
        if lat is None or lon is None:
            continue

        # Собираем адрес: улица + номер дома
        street = tags.get("addr:street") or ""
        housenumber = tags.get("addr:housenumber") or ""
        address_parts = []
        if street:
            address_parts.append(street.strip())
        if housenumber:
            address_parts.append(housenumber.strip())
        address = " ".join(address_parts)[:160] if address_parts else None

        stops.append({
            "name": name[:120],
            "lat": float(lat),
            "lon": float(lon),
            "osm_id": el.get("id"),
            "address": address,
            "has_pavilion": tags.get("shelter") in ("yes", "true", "1"),
        })

    return stops
