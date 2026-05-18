"""Импорт реальных остановочных пунктов из OpenStreetMap.

Запуск:
    docker compose exec backend python -m app.seeds.import_osm_stops
    docker compose exec backend python -m app.seeds.import_osm_stops --city Москва
    docker compose exec backend python -m app.seeds.import_osm_stops --bbox 51.7,55.0,51.9,55.3

Также после загрузки остановок строит простой граф связности — каждая
остановка соединяется с 4 ближайшими (двунаправленно).
"""
from __future__ import annotations

import argparse
import sys
from decimal import Decimal

from sqlalchemy import select

from app.core.schema_sync import ensure_schema
from app.database import SessionLocal
from app.models.bus_stop import BusStop, BusStopConnection
from app.services.osm_overpass import (
    build_query_by_admin_name,
    build_query_by_bbox,
    fetch_stops,
)
from app.services.route_engine import haversine_km


# Bounding box Оренбурга (приближённый, для fallback)
OREMBURG_BBOX = (51.70, 55.00, 51.90, 55.30)  # south, west, north, east


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Импорт остановок из OSM")
    p.add_argument("--city", default="Оренбург", help="Название города (по name в OSM)")
    p.add_argument(
        "--bbox",
        help="Прямоугольник в формате south,west,north,east (если задан — использовать вместо --city)",
    )
    p.add_argument("--admin-level", type=int, default=6, help="OSM admin_level (default 6)")
    p.add_argument("--neighbours", type=int, default=4, help="Сколько ближайших соседей соединять")
    p.add_argument(
        "--merge-radius", type=float, default=50.0,
        help="Расстояние в метрах для объединения дубликатов (остановки на разных сторонах улицы). По умолчанию 50 м.",
    )
    p.add_argument("--no-graph", action="store_true", help="Не строить граф связности")
    p.add_argument("--clear", action="store_true", help="Удалить все остановки/связи перед импортом")
    p.add_argument("--dry-run", action="store_true", help="Только запросить OSM и показать статистику, без записи в БД")
    return p.parse_args()


def _deduplicate_by_proximity(
    stops: list[dict],
    radius_m: float,
) -> list[dict]:
    """Объединить остановки, находящиеся ближе radius_m метров друг от друга.

    Для каждой пары в пределах радиуса оставляет ту, у которой:
    - есть павильон (has_pavilion=True), либо
    - более полный адрес, либо
    - первая по порядку.
    """
    if len(stops) <= 1:
        return stops

    # Сортируем: с павильоном — выше приоритет
    stops = sorted(stops, key=lambda s: (not s["has_pavilion"], s.get("address") or "" == ""))
    kept: list[dict] = []
    kept_coords: list[tuple[float, float]] = []

    for s in stops:
        slat, slon = s["lat"], s["lon"]
        too_close = False
        for klat, klon in kept_coords:
            d = haversine_km(slat, slon, klat, klon) * 1000.0
            if d < radius_m:
                too_close = True
                break
        if not too_close:
            kept.append(s)
            kept_coords.append((slat, slon))

    return kept


def main() -> int:
    args = _parse_args()
    ensure_schema()

    if args.bbox:
        bb = [float(x) for x in args.bbox.split(",")]
        if len(bb) != 4:
            print("--bbox должен быть south,west,north,east", file=sys.stderr)
            return 1
        query = build_query_by_bbox(*bb)
        scope = f"bbox {bb}"
    else:
        query = build_query_by_admin_name(args.city, args.admin_level)
        scope = f"город «{args.city}» (admin_level={args.admin_level})"

    print(f"[*] Запрос Overpass: {scope}")
    print("[*] Это может занять 10–60 секунд, ожидайте…")

    try:
        stops = fetch_stops(query)
    except Exception as e:
        print(f"[!] Ошибка Overpass: {e}")
        if not args.bbox and args.city == "Оренбург":
            print("[*] Пробую fallback по bounding box Оренбурга…")
            stops = fetch_stops(build_query_by_bbox(*OREMBURG_BBOX))
        else:
            return 2

    print(f"[+] Получено {len(stops)} остановок из OSM")
    if not stops:
        print("[!] Ничего не найдено. Попробуйте --bbox или другое название.")
        return 3

    # Дедупликация по близости (остановки на разных сторонах улицы)
    if args.merge_radius > 0:
        before = len(stops)
        stops = _deduplicate_by_proximity(stops, args.merge_radius)
        removed = before - len(stops)
        if removed:
            print(f"[*] Дедупликация по близости ({args.merge_radius} м): удалено {removed} дубликатов")

    # Статистика для dry-run
    with_pavilion = sum(1 for s in stops if s["has_pavilion"])
    with_address = sum(1 for s in stops if s.get("address"))
    print(f"[*] Статистика: {len(stops)} остановок, {with_pavilion} с павильоном, {with_address} с адресом")

    if args.dry_run:
        print("[*] --dry-run: запись в БД пропущена")
        print("=== ГОТОВО (предпросмотр) ===")
        return 0

    db = SessionLocal()
    try:
        if args.clear:
            db.query(BusStopConnection).delete()
            db.query(BusStop).delete()
            db.commit()
            print("[+] Старые данные удалены")

        # Импорт остановок (по имени — дедупликация)
        existing_names = {
            row[0] for row in db.execute(select(BusStop.name)).all()
        }
        added = 0
        for s in stops:
            if s["name"] in existing_names:
                continue
            db.add(BusStop(
                name=s["name"],
                lat=Decimal(f"{s['lat']:.7f}"),
                lon=Decimal(f"{s['lon']:.7f}"),
                address=s["address"],
                has_pavilion=s["has_pavilion"],
            ))
            existing_names.add(s["name"])
            added += 1
            if added % 100 == 0:
                db.commit()
        db.commit()
        print(f"[+] В БД добавлено {added} остановок")

        if args.no_graph:
            return 0

        # Граф связности — каждой остановке соединяем N ближайших
        all_stops = list(db.execute(select(BusStop)).scalars().all())
        existing_pairs = {
            (c.from_stop, c.to_stop)
            for c in db.execute(select(BusStopConnection)).scalars().all()
        }
        edges_added = 0
        print(f"[*] Строю граф ({args.neighbours} ближайших соседей)…")
        for s1 in all_stops:
            dists = []
            for s2 in all_stops:
                if s2.id == s1.id:
                    continue
                d = haversine_km(float(s1.lat), float(s1.lon), float(s2.lat), float(s2.lon))
                dists.append((s2, d))
            dists.sort(key=lambda x: x[1])
            for s2, d_km in dists[:args.neighbours]:
                for src, dst in [(s1.id, s2.id), (s2.id, s1.id)]:
                    if (src, dst) in existing_pairs:
                        continue
                    db.add(BusStopConnection(
                        from_stop=src,
                        to_stop=dst,
                        distance=Decimal(f"{d_km:.2f}"),
                        avg_time=Decimal(f"{d_km / 0.5:.1f}"),  # 30 км/ч
                    ))
                    existing_pairs.add((src, dst))
                    edges_added += 1
            if edges_added % 500 == 0 and edges_added:
                db.commit()
        db.commit()
        print(f"[+] Граф: {edges_added} рёбер")

    finally:
        db.close()

    print("=== ГОТОВО ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
