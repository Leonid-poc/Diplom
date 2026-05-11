"""Идемпотентное обновление схемы БД.

Применяется при старте seed-скриптов и (опционально) приложения, чтобы
поддерживать совместимость с существующими БД без полной миграции.
Не заменяет Alembic — это страховка для разработки.
"""
from sqlalchemy import text

from app.database import Base, engine


# Список колонок, добавляемых после первоначального create_all
# (формат: (table, column, type, default))
INCREMENTAL_COLUMNS = [
    ("routes", "description",         "TEXT",         None),
    ("routes", "geometry",            "JSONB",        "'[]'::jsonb"),
    ("routes", "estimated_time_min",  "NUMERIC(7,1)", None),
    ("routes", "algorithm",           "VARCHAR(20)",  None),
]


def ensure_schema() -> None:
    """Создать недостающие таблицы и добавить колонки, если их нет."""
    Base.metadata.create_all(bind=engine)
    with engine.begin() as conn:
        for table, column, col_type, default in INCREMENTAL_COLUMNS:
            stmt = f"ALTER TABLE {table} ADD COLUMN IF NOT EXISTS {column} {col_type}"
            if default is not None:
                stmt += f" DEFAULT {default}"
            conn.execute(text(stmt))
