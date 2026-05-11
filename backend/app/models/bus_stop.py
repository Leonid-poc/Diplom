"""Остановочные пункты, рёбра графа сети, связь остановок и маршрутов."""
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    ForeignKey,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class BusStop(Base):
    __tablename__ = "bus_stops"
    __table_args__ = (UniqueConstraint("lat", "lon", name="uq_bus_stop_coords"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    lat: Mapped[Decimal] = mapped_column(Numeric(10, 7), nullable=False)
    lon: Mapped[Decimal] = mapped_column(Numeric(10, 7), nullable=False)
    address: Mapped[str | None] = mapped_column(String(160))
    has_pavilion: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


class BusStopRoute(Base):
    """Связь «остановка ↔ маршрут» (с порядковым номером)."""

    __tablename__ = "bus_stop_routes"
    __table_args__ = (
        CheckConstraint("order_num > 0", name="ck_bsr_order_positive"),
        UniqueConstraint("route_id", "order_num", name="uq_bsr_route_order"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    stop_id: Mapped[int] = mapped_column(
        ForeignKey("bus_stops.id", ondelete="RESTRICT"), nullable=False
    )
    route_id: Mapped[int] = mapped_column(
        ForeignKey("routes.id", ondelete="CASCADE"), nullable=False
    )
    order_num: Mapped[int] = mapped_column(Integer, nullable=False)

    stop: Mapped["BusStop"] = relationship(lazy="joined")


class BusStopConnection(Base):
    """Ребро графа дорожной сети между двумя остановочными пунктами."""

    __tablename__ = "bus_stop_connections"
    __table_args__ = (
        CheckConstraint("distance > 0", name="ck_bsc_distance_positive"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    from_stop: Mapped[int] = mapped_column(
        ForeignKey("bus_stops.id", ondelete="CASCADE"), nullable=False
    )
    to_stop: Mapped[int] = mapped_column(
        ForeignKey("bus_stops.id", ondelete="CASCADE"), nullable=False
    )
    distance: Mapped[Decimal] = mapped_column(Numeric(6, 2), nullable=False)
    avg_time: Mapped[Decimal | None] = mapped_column(Numeric(5, 1))
