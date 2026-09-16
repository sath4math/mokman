import uuid
from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, uuid_pk


class Asset(Base, TimestampMixin):
    """A property-scoped physical asset (appliance, furniture, fixture)
    tracked through its full lifecycle (Phase 8a).

    `category` stays free-text, same convention as
    MaintenanceTicket/MaintenanceSchedule's category -- no forced
    catalog. Current depreciated value is computed on read from
    purchase_cost/useful_life_years (see assets/service.py), not
    stored, same "computed on read" precedent as VendorOut.average_rating.
    """

    __tablename__ = "assets"

    id: Mapped[uuid.UUID] = uuid_pk()
    property_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("properties.id"), index=True)
    category: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(255))
    purchase_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    purchase_cost: Mapped[float | None] = mapped_column(Float, nullable=True)
    vendor_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("vendors.id"), nullable=True)
    warranty_expires_on: Mapped[date | None] = mapped_column(Date, nullable=True)
    useful_life_years: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    disposed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    disposed_reason: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Set when this asset was superseded by a newer one (replace_asset) --
    # same "supersedes" convention as Lease.previous_lease_id /
    # MaintenanceTicket.related_ticket_id.
    replaced_by_asset_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("assets.id"), nullable=True
    )
