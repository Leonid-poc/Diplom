"""CRUD парка ТС: типы, модели, ТС."""
from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.deps import get_current_user, get_db
from app.models.user import User
from app.models.vehicle import Vehicle, VehicleModel, VehicleType
from app.schemas.vehicle import (
    VehicleCreate,
    VehicleModelCreate,
    VehicleModelRead,
    VehicleRead,
    VehicleTypeCreate,
    VehicleTypeRead,
)

router = APIRouter()


# ---------- VehicleType ----------

@router.get("/types", response_model=list[VehicleTypeRead])
def list_types(db: Session = Depends(get_db), _user: User = Depends(get_current_user)):
    return db.execute(select(VehicleType).order_by(VehicleType.name)).scalars().all()


@router.post("/types", response_model=VehicleTypeRead, status_code=status.HTTP_201_CREATED)
def create_type(
    payload: VehicleTypeCreate,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    obj = VehicleType(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


# ---------- VehicleModel ----------

@router.get("/models", response_model=list[VehicleModelRead])
def list_models(db: Session = Depends(get_db), _user: User = Depends(get_current_user)):
    return db.execute(select(VehicleModel).order_by(VehicleModel.model_name)).scalars().all()


@router.post("/models", response_model=VehicleModelRead, status_code=status.HTTP_201_CREATED)
def create_model(
    payload: VehicleModelCreate,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    obj = VehicleModel(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


# ---------- Vehicle ----------

@router.get("", response_model=list[VehicleRead])
def list_vehicles(db: Session = Depends(get_db), _user: User = Depends(get_current_user)):
    return db.execute(select(Vehicle).order_by(Vehicle.license_plate)).scalars().all()


@router.post("", response_model=VehicleRead, status_code=status.HTTP_201_CREATED)
def create_vehicle(
    payload: VehicleCreate,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    obj = Vehicle(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vehicle(
    vehicle_id: int,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    obj = db.get(Vehicle, vehicle_id)
    if not obj:
        raise NotFoundError("Транспортное средство")
    db.delete(obj)
    db.commit()
