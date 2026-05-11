"""Тестовые данные: пользователи, типы/модели/ТС, остановки Оренбурга, рёбра графа.

Запуск: docker compose exec backend python -m app.seeds.seed_oremburg
"""
from decimal import Decimal

from sqlalchemy import select

from app.core.security import hash_password
from app.database import SessionLocal
from app.models.bus_stop import BusStop, BusStopConnection
from app.models.route import Route
from app.models.user import User, UserRole
from app.models.vehicle import Vehicle, VehicleModel, VehicleType
from app.services.route_engine import haversine_km


USERS = [
    {"login": "admin",   "password": "admin123",   "full_name": "Администратор", "role": UserRole.ADMIN},
    {"login": "analyst", "password": "analyst123", "full_name": "Иванов И.И. (аналитик)", "role": UserRole.ANALYST},
    {"login": "manager", "password": "manager123", "full_name": "Петров П.П. (руководитель)", "role": UserRole.MANAGER},
]

VEHICLE_TYPES = [
    {"name": "автобус",        "description": "Городской автобус"},
    {"name": "троллейбус",     "description": "Городской электрический транспорт с контактной сетью"},
    {"name": "маршрутное такси", "description": "Микроавтобус малой вместимости"},
]

VEHICLE_MODELS = [
    {"type": "автобус",          "model_name": "ЛиАЗ-5292",    "capacity": 108},
    {"type": "автобус",          "model_name": "НефАЗ-5299",   "capacity": 105},
    {"type": "автобус",          "model_name": "ПАЗ-3204",     "capacity": 45},
    {"type": "троллейбус",       "model_name": "Тролза-5275",  "capacity": 96},
    {"type": "маршрутное такси", "model_name": "Ford Transit", "capacity": 20},
]

VEHICLES = [
    {"model": "ЛиАЗ-5292",    "plate": "А123ВХ56", "year": 2022},
    {"model": "ЛиАЗ-5292",    "plate": "А234ВХ56", "year": 2023},
    {"model": "НефАЗ-5299",   "plate": "В345ВХ56", "year": 2021},
    {"model": "ПАЗ-3204",     "plate": "С456ВХ56", "year": 2020},
    {"model": "Тролза-5275",  "plate": "Т567ВХ56", "year": 2019},
    {"model": "Ford Transit", "plate": "К678ВХ56", "year": 2021},
]

# Примерные остановки Оренбурга (координаты приблизительные)
BUS_STOPS = [
    {"name": "пл. Ленина",            "lat": "51.7682", "lon": "55.0972"},
    {"name": "ОГУ",                   "lat": "51.8067", "lon": "55.0566"},
    {"name": "Центральный рынок",     "lat": "51.7691", "lon": "55.0987"},
    {"name": "ул. Терешковой",        "lat": "51.7892", "lon": "55.0432"},
    {"name": "пр. Победы",            "lat": "51.7989", "lon": "55.1102"},
    {"name": "ТРЦ «Армада»",          "lat": "51.7321", "lon": "55.1789"},
    {"name": "Аэропорт",              "lat": "51.7896", "lon": "55.4567"},
    {"name": "ж/д вокзал",            "lat": "51.7741", "lon": "55.1024"},
    {"name": "Маяк",                  "lat": "51.8123", "lon": "55.0234"},
    {"name": "Степной",               "lat": "51.7398", "lon": "55.0445"},
    {"name": "Гагарина",              "lat": "51.7864", "lon": "55.1234"},
    {"name": "Заречье",               "lat": "51.7501", "lon": "55.0823"},
    {"name": "Силикатный завод",      "lat": "51.8234", "lon": "55.0989"},
    {"name": "Дзержинский р-н",       "lat": "51.7621", "lon": "55.1432"},
    {"name": "ул. Чкалова",           "lat": "51.7956", "lon": "55.0801"},
    {"name": "пл. 1 Мая",             "lat": "51.7745", "lon": "55.0856"},
    {"name": "ТЦ «Гудвин»",           "lat": "51.7423", "lon": "55.1289"},
    {"name": "Восточная",             "lat": "51.7989", "lon": "55.1567"},
    {"name": "Северная",              "lat": "51.8232", "lon": "55.1102"},
    {"name": "Южный мкр.",            "lat": "51.7234", "lon": "55.0689"},
]


def seed() -> None:
    db = SessionLocal()
    try:
        # ----- Users -----
        for u in USERS:
            existing = db.execute(select(User).where(User.login == u["login"])).scalar_one_or_none()
            if existing:
                continue
            db.add(User(
                login=u["login"],
                full_name=u["full_name"],
                hashed_password=hash_password(u["password"]),
                role=u["role"],
                is_active=True,
            ))
        db.commit()
        print("[+] Пользователи загружены")

        # ----- Vehicle types -----
        types_map: dict[str, VehicleType] = {}
        for t in VEHICLE_TYPES:
            obj = db.execute(select(VehicleType).where(VehicleType.name == t["name"])).scalar_one_or_none()
            if obj is None:
                obj = VehicleType(**t)
                db.add(obj)
                db.flush()
            types_map[t["name"]] = obj
        db.commit()

        # ----- Vehicle models -----
        models_map: dict[str, VehicleModel] = {}
        for m in VEHICLE_MODELS:
            obj = db.execute(
                select(VehicleModel).where(VehicleModel.model_name == m["model_name"])
            ).scalar_one_or_none()
            if obj is None:
                obj = VehicleModel(
                    type_id=types_map[m["type"]].id,
                    model_name=m["model_name"],
                    capacity=m["capacity"],
                )
                db.add(obj)
                db.flush()
            models_map[m["model_name"]] = obj
        db.commit()
        print("[+] Типы и модели ТС загружены")

        # ----- Vehicles -----
        for v in VEHICLES:
            existing = db.execute(
                select(Vehicle).where(Vehicle.license_plate == v["plate"])
            ).scalar_one_or_none()
            if existing:
                continue
            db.add(Vehicle(
                model_id=models_map[v["model"]].id,
                license_plate=v["plate"],
                year_of_make=v["year"],
                is_active=True,
            ))
        db.commit()
        print(f"[+] {len(VEHICLES)} ТС в парке")

        # ----- Bus stops -----
        stops_map: dict[str, BusStop] = {}
        for s in BUS_STOPS:
            existing = db.execute(
                select(BusStop).where(BusStop.name == s["name"])
            ).scalar_one_or_none()
            if existing:
                stops_map[s["name"]] = existing
                continue
            obj = BusStop(
                name=s["name"],
                lat=Decimal(s["lat"]),
                lon=Decimal(s["lon"]),
                has_pavilion=True,
            )
            db.add(obj)
            db.flush()
            stops_map[s["name"]] = obj
        db.commit()
        print(f"[+] {len(BUS_STOPS)} остановок Оренбурга")

        # ----- Bus stop connections (граф сети) -----
        # Простая стратегия: соединяем каждую остановку с 3 ближайшими (двунаправленно)
        all_stops = list(stops_map.values())
        existing_pairs: set[tuple[int, int]] = {
            (c.from_stop, c.to_stop)
            for c in db.execute(select(BusStopConnection)).scalars().all()
        }
        added = 0
        for s1 in all_stops:
            dists = [
                (s2, haversine_km(float(s1.lat), float(s1.lon), float(s2.lat), float(s2.lon)))
                for s2 in all_stops if s2.id != s1.id
            ]
            dists.sort(key=lambda x: x[1])
            for s2, dist_km in dists[:3]:
                for src, dst in [(s1.id, s2.id), (s2.id, s1.id)]:
                    if (src, dst) in existing_pairs:
                        continue
                    db.add(BusStopConnection(
                        from_stop=src,
                        to_stop=dst,
                        distance=Decimal(f"{dist_km:.2f}"),
                        avg_time=Decimal(f"{dist_km / 0.5:.1f}"),  # 30 км/ч
                    ))
                    existing_pairs.add((src, dst))
                    added += 1
        db.commit()
        print(f"[+] {added} рёбер графа дорожной сети")

        # ----- Routes (пример: один маршрут) -----
        existing_route = db.execute(select(Route).where(Route.route_number == "11")).scalar_one_or_none()
        if existing_route is None:
            db.add(Route(
                route_number="11",
                name="Степной — Маяк",
                type="городской",
                total_length=Decimal("14.7"),
                is_active=True,
            ))
            db.commit()
            print("[+] Демо-маршрут №11")

        print("\n=== ГОТОВО ===")
        print("Логины:")
        for u in USERS:
            print(f"  {u['login']:8s} / {u['password']}  ({u['role'].value})")

    finally:
        db.close()


if __name__ == "__main__":
    seed()
