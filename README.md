# ПИС «Маршрут» — программная реализация

Программно-информационная система автоматизированного проектирования городских
маршрутов пассажирских перевозок. Реализация выпускной квалификационной работы
Л.Е. Георга (ОГУ, 09.03.04 «Программная инженерия»,
шифр ОГУ 09.03.04.3025.755 ПЗ, 2026 г.).

## Стек технологий

| Слой         | Технология |
|--------------|-----------|
| Frontend     | Next.js 14 (App Router) + TypeScript + ShadcnUI + Tailwind CSS |
| Backend      | FastAPI (Python 3.12) + SQLAlchemy 2 + Alembic |
| СУБД         | PostgreSQL 16 |
| Кэш          | Redis 7 |
| Граф/алгоритмы | NetworkX (Dijkstra, A*) |
| Машинное обучение | scikit-learn (k-means) |
| Карты        | Leaflet + OpenStreetMap (без API-ключей) |
| Контейнеризация | Docker + Docker Compose |

## Архитектура

```
┌───────────┐     HTTPS      ┌──────────────┐
│  Браузер  │ ─────────────► │ Next.js 14   │
│ (Leaflet) │ ◄───────────── │  (frontend)  │
└───────────┘                 └──────┬───────┘
                                     │ REST / JSON
                                     ▼
                              ┌──────────────┐
                              │   FastAPI    │
                              │  (backend)   │
                              └──┬──────┬────┘
                       ┌─────────┘      └───────┐
                       ▼                        ▼
                ┌─────────────┐         ┌──────────────┐
                │ PostgreSQL  │         │   Redis      │
                │  routes,    │         │   cache,     │
                │  bus_stops, │         │   sessions   │
                │  vehicles…  │         │              │
                └─────────────┘         └──────────────┘
```

## Быстрый старт

### 1. Клонировать и подготовить `.env`

```bash
git clone <this-repo>
cd programm
cp .env.example .env
# отредактируйте .env — обязательно поменяйте POSTGRES_PASSWORD и JWT_SECRET
```

### 2. Запустить через Docker Compose

```bash
docker compose up -d --build
# дождитесь, пока контейнеры станут healthy
docker compose logs -f backend
```

При первом запуске backend автоматически применит миграции Alembic.

### 3. Инициализировать тестовые данные

```bash
docker compose exec backend python -m app.seeds.seed_oremburg
```

Это создаст: учётную запись администратора (логин `admin` / пароль `admin123`),
несколько типов и моделей ТС, ~20 остановочных пунктов Оренбурга и пример маршрута.

### 4. Открыть приложение

- Frontend: <http://localhost:3000/>
- Backend OpenAPI docs: <http://localhost:8000/docs>
- Backend ReDoc: <http://localhost:8000/redoc>

## Структура проекта

```
programm/
├── docker-compose.yml
├── .env.example
├── .gitignore
├── README.md
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── alembic.ini
│   ├── alembic/              # миграции БД
│   ├── app/
│   │   ├── main.py           # точка входа FastAPI
│   │   ├── config.py         # настройки (pydantic-settings)
│   │   ├── database.py       # SQLAlchemy engine + Session
│   │   ├── deps.py           # get_db, get_current_user
│   │   ├── core/             # security, exceptions
│   │   ├── models/           # ORM-модели (User, Route, BusStop, Vehicle, ...)
│   │   ├── schemas/          # Pydantic v2
│   │   ├── services/         # бизнес-логика
│   │   │   ├── route_engine.py     # Dijkstra / A*
│   │   │   ├── cluster_service.py  # k-means
│   │   │   ├── auth_service.py
│   │   │   └── vis_integration.py
│   │   ├── api/v1/           # роутеры
│   │   └── seeds/            # начальные данные
│   └── tests/
└── frontend/
    ├── Dockerfile
    ├── package.json
    ├── next.config.js
    ├── tailwind.config.ts
    ├── components.json       # shadcn config
    ├── app/                  # App Router pages
    ├── components/
    │   ├── ui/               # shadcn компоненты
    │   ├── layout/
    │   ├── map/              # LeafletMap
    │   └── routes/
    ├── lib/                  # api wrapper, utils
    ├── hooks/
    └── stores/               # Zustand
```

## API (v1)

| Метод | Endpoint                           | Описание                              |
|-------|------------------------------------|---------------------------------------|
| POST  | `/api/v1/auth/login`               | Авторизация, получение JWT             |
| GET   | `/api/v1/auth/me`                  | Текущий пользователь                  |
| GET   | `/api/v1/routes`                   | Список маршрутов                       |
| POST  | `/api/v1/routes`                   | Создание маршрута                      |
| GET   | `/api/v1/routes/{id}`              | Карточка маршрута                      |
| POST  | `/api/v1/routes/build`             | Расчёт оптимального пути (Dijkstra/A*) |
| GET   | `/api/v1/bus_stops`                | Список остановок                       |
| POST  | `/api/v1/bus_stops`                | Добавить остановку                     |
| GET   | `/api/v1/connections`              | Рёбра графа сети                       |
| POST  | `/api/v1/connections`              | Добавить ребро                         |
| GET   | `/api/v1/vehicles`                 | Парк ТС                                |
| GET   | `/api/v1/passenger_flows`          | Замеры пассажиропотока                 |
| POST  | `/api/v1/analytics/cluster`        | Кластерный анализ маршрутов            |
| GET   | `/api/v1/reports`                  | Аналитические отчёты                   |
| GET   | `/api/v1/health`                   | Health-check                           |

Полная интерактивная документация: <http://localhost:8000/docs>.

## Карты (OpenStreetMap)

В приложении используются **бесплатные тайлы OpenStreetMap** без необходимости
получения API-ключей. Тайл-сервер задаётся переменной `NEXT_PUBLIC_MAP_TILE_URL`
в `.env`. По умолчанию: `https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png`.

> **Примечание:** для production-нагрузок (>5 000 запросов в день на пользователя)
> следует развернуть собственный tile-сервер либо использовать платный CDN
> (Stadia Maps, Mapbox, Yandex Maps API).

## Разработка

### Backend (без Docker)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate            # macOS/Linux
# .venv\Scripts\activate              # Windows PowerShell
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

### Frontend (без Docker)

```bash
cd frontend
npm install
npm run dev
```

### Запуск тестов

```bash
# Backend
docker compose exec backend pytest -v
# Frontend
docker compose exec frontend npm test
```

### Миграции

```bash
# Создать новую миграцию по изменениям моделей
docker compose exec backend alembic revision --autogenerate -m "описание"
# Применить
docker compose exec backend alembic upgrade head
# Откатить на одну
docker compose exec backend alembic downgrade -1
```

## Доменная модель

Соответствует разделу 2.3 пояснительной записки:

- `routes` — справочник маршрутов;
- `bus_stops` — справочник остановочных пунктов (lat/lon);
- `bus_stop_routes` — связь «остановка ↔ маршрут» (порядок);
- `bus_stop_connections` — рёбра графа дорожной сети (расстояние, время);
- `vehicle_types`, `vehicle_models`, `vehicles` — парк подвижного состава;
- `passenger_flows` — замеры пассажиропотока;
- `trips` — журнал рейсов;
- `analytics_reports` — аналитические отчёты;
- `users` — пользователи системы.

## Лицензия и атрибуция

- Карты: © OpenStreetMap contributors, [ODbL](https://www.openstreetmap.org/copyright)
- Иконки: [Lucide](https://lucide.dev) (ISC License)
- UI-компоненты: [shadcn/ui](https://ui.shadcn.com) (MIT)
