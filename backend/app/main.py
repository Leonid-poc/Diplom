"""Точка входа FastAPI."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import api_router
from app.config import settings


def create_app() -> FastAPI:
    app = FastAPI(
        title="ПИС «Маршрут» — API",
        description=(
            "Программно-информационная система автоматизированного "
            "проектирования городских маршрутов пассажирских перевозок. "
            "ВКР Л.Е. Георга, ОГУ 09.03.04.3025.755 ПЗ."
        ),
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router, prefix="/api/v1")

    return app


app = create_app()
