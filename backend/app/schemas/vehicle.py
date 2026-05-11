"""Схемы для парка ТС."""
from pydantic import BaseModel, ConfigDict, Field


class VehicleTypeCreate(BaseModel):
    name: str = Field(..., max_length=80)
    description: str | None = None


class VehicleTypeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None = None


class VehicleModelCreate(BaseModel):
    type_id: int
    model_name: str = Field(..., max_length=80)
    capacity: int = Field(..., gt=0)


class VehicleModelRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    type_id: int
    model_name: str
    capacity: int


class VehicleCreate(BaseModel):
    model_id: int
    license_plate: str = Field(..., max_length=15)
    year_of_make: int | None = Field(default=None, ge=1990, le=2100)
    is_active: bool = True


class VehicleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    model_id: int
    license_plate: str
    year_of_make: int | None
    is_active: bool
