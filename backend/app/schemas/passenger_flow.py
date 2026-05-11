"""Схемы пассажиропотока."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PassengerFlowCreate(BaseModel):
    route_id: int
    stop_id: int
    passengers: int = Field(..., ge=0)
    measured_at: datetime


class PassengerFlowRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    route_id: int
    stop_id: int
    passengers: int
    measured_at: datetime
