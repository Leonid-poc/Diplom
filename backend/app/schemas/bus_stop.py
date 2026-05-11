"""Схемы для остановок и рёбер графа."""
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class BusStopCreate(BaseModel):
    name: str = Field(..., max_length=120)
    lat: Decimal
    lon: Decimal
    address: str | None = Field(default=None, max_length=160)
    has_pavilion: bool = False


class BusStopRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    lat: Decimal
    lon: Decimal
    address: str | None = None
    has_pavilion: bool


class BusStopConnectionCreate(BaseModel):
    from_stop: int
    to_stop: int
    distance: Decimal = Field(..., gt=0)
    avg_time: Decimal | None = None


class BusStopConnectionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    from_stop: int
    to_stop: int
    distance: Decimal
    avg_time: Decimal | None = None
