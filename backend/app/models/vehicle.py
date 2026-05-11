"""Парк транспортных средств (типы, модели, единицы ТС)."""
from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class VehicleType(Base):
    __tablename__ = "vehicle_types"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)

    models: Mapped[list["VehicleModel"]] = relationship(
        back_populates="vehicle_type", cascade="all, delete-orphan"
    )


class VehicleModel(Base):
    __tablename__ = "vehicle_models"
    __table_args__ = (
        CheckConstraint("capacity > 0", name="ck_vehicle_model_capacity_positive"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    type_id: Mapped[int] = mapped_column(
        ForeignKey("vehicle_types.id", ondelete="RESTRICT"), nullable=False
    )
    model_name: Mapped[str] = mapped_column(String(80), nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)

    vehicle_type: Mapped[VehicleType] = relationship(back_populates="models")
    vehicles: Mapped[list["Vehicle"]] = relationship(back_populates="model")


class Vehicle(Base):
    __tablename__ = "vehicles"
    __table_args__ = (
        CheckConstraint(
            "year_of_make BETWEEN 1990 AND 2100",
            name="ck_vehicle_year_range",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    model_id: Mapped[int] = mapped_column(
        ForeignKey("vehicle_models.id", ondelete="RESTRICT"), nullable=False
    )
    license_plate: Mapped[str] = mapped_column(String(15), unique=True, nullable=False)
    year_of_make: Mapped[int | None] = mapped_column(Integer)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    model: Mapped[VehicleModel] = relationship(back_populates="vehicles")
