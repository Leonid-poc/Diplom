"""Замеры пассажиропотока на остановках маршрутов."""
from datetime import datetime

from sqlalchemy import BigInteger, CheckConstraint, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class PassengerFlow(Base):
    __tablename__ = "passenger_flows"
    __table_args__ = (
        CheckConstraint("passengers >= 0", name="ck_pf_passengers_non_negative"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    route_id: Mapped[int] = mapped_column(
        ForeignKey("routes.id", ondelete="CASCADE"), nullable=False, index=True
    )
    stop_id: Mapped[int] = mapped_column(
        ForeignKey("bus_stops.id", ondelete="RESTRICT"), nullable=False
    )
    passengers: Mapped[int] = mapped_column(Integer, nullable=False)
    measured_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
