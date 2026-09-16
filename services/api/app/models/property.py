import enum
import uuid

from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, str_enum_column, uuid_pk


class PropertyStatus(str, enum.Enum):
    VACANT = "vacant"
    OCCUPIED = "occupied"
    UNDER_MAINTENANCE = "under_maintenance"
    INACTIVE = "inactive"


class Property(Base, TimestampMixin):
    """Root of the property hierarchy: Property -> Building -> Block -> Floor -> Unit -> Room.

    Every later phase (tenant, lease, rent, maintenance, inspections, assets,
    sale) attaches records to this backbone, so this schema is deliberately
    built now rather than left to grow ad hoc.
    """

    __tablename__ = "properties"

    id: Mapped[uuid.UUID] = uuid_pk()
    owner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    category: Mapped[str] = mapped_column(String(50))
    name: Mapped[str] = mapped_column(String(255))
    address_line: Mapped[str] = mapped_column(String(500))
    city: Mapped[str] = mapped_column(String(100))
    state: Mapped[str] = mapped_column(String(100))
    postal_code: Mapped[str] = mapped_column(String(20))
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    status: Mapped[PropertyStatus] = mapped_column(
        str_enum_column(PropertyStatus, "property_status"), default=PropertyStatus.VACANT
    )

    area_sqft: Mapped[float | None] = mapped_column(Float, nullable=True)
    num_floors: Mapped[int | None] = mapped_column(Integer, nullable=True)
    num_units: Mapped[int | None] = mapped_column(Integer, nullable=True)
    amenities: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    furnishing_status: Mapped[str | None] = mapped_column(String(30), nullable=True)

    # Cost basis for Phase 8c's investment-intelligence metrics
    # (yield/appreciation/ROI) -- both nullable, every metric derived
    # from them is None until an owner sets them.
    purchase_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    current_market_value: Mapped[float | None] = mapped_column(Float, nullable=True)


class Building(Base, TimestampMixin):
    __tablename__ = "buildings"

    id: Mapped[uuid.UUID] = uuid_pk()
    property_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("properties.id"), index=True)
    name: Mapped[str] = mapped_column(String(255))


class Block(Base, TimestampMixin):
    __tablename__ = "blocks"

    id: Mapped[uuid.UUID] = uuid_pk()
    building_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("buildings.id"), index=True)
    name: Mapped[str] = mapped_column(String(100))


class Floor(Base, TimestampMixin):
    __tablename__ = "floors"

    id: Mapped[uuid.UUID] = uuid_pk()
    block_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("blocks.id"), index=True)
    level: Mapped[int] = mapped_column(Integer)


class Unit(Base, TimestampMixin):
    __tablename__ = "units"

    id: Mapped[uuid.UUID] = uuid_pk()
    floor_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("floors.id"), index=True)
    unit_number: Mapped[str] = mapped_column(String(50))
    area_sqft: Mapped[float | None] = mapped_column(Float, nullable=True)
    status: Mapped[PropertyStatus] = mapped_column(
        str_enum_column(PropertyStatus, "property_status"), default=PropertyStatus.VACANT
    )


class Room(Base, TimestampMixin):
    __tablename__ = "rooms"

    id: Mapped[uuid.UUID] = uuid_pk()
    unit_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("units.id"), index=True)
    name: Mapped[str] = mapped_column(String(100))


class ParkingSpot(Base, TimestampMixin):
    __tablename__ = "parking_spots"

    id: Mapped[uuid.UUID] = uuid_pk()
    property_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("properties.id"), index=True)
    identifier: Mapped[str] = mapped_column(String(50))


class StorageUnit(Base, TimestampMixin):
    __tablename__ = "storage_units"

    id: Mapped[uuid.UUID] = uuid_pk()
    property_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("properties.id"), index=True)
    identifier: Mapped[str] = mapped_column(String(50))


class CommonArea(Base, TimestampMixin):
    __tablename__ = "common_areas"

    id: Mapped[uuid.UUID] = uuid_pk()
    property_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("properties.id"), index=True)
    name: Mapped[str] = mapped_column(String(100))
