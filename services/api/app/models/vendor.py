import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, uuid_pk


class Vendor(Base, TimestampMixin):
    """An external service provider Mokman ops assigns ticket work to.

    Not a `User` — vendors don't log in (internal resource model per the
    phase-wise plan, not a marketplace); admin manages this directory on
    their behalf. `is_active` is only ever flipped via the blacklist/
    reinstate service functions (never a plain field edit), which log an
    `AuditLog` row so there's always a reason on record for a deactivation.
    """

    __tablename__ = "vendors"

    id: Mapped[uuid.UUID] = uuid_pk()
    name: Mapped[str] = mapped_column(String(255))
    service_category: Mapped[str] = mapped_column(String(100))
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    gst_number: Mapped[str | None] = mapped_column(String(20), nullable=True)
    pan_number: Mapped[str | None] = mapped_column(String(20), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class VendorRateCard(Base, TimestampMixin):
    """Reference pricing for a vendor's service — informational only this
    pass, not auto-applied to an Expense amount."""

    __tablename__ = "vendor_rate_cards"

    id: Mapped[uuid.UUID] = uuid_pk()
    vendor_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("vendors.id"), index=True)
    service_category: Mapped[str] = mapped_column(String(100))
    unit: Mapped[str] = mapped_column(String(50))
    rate: Mapped[float] = mapped_column(Float)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)


class VendorRating(Base):
    """An owner/admin's immutable rating of a vendor's work on one closed
    ticket — never updated or deleted, same convention as LedgerEntry."""

    __tablename__ = "vendor_ratings"

    id: Mapped[uuid.UUID] = uuid_pk()
    vendor_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("vendors.id"), index=True)
    ticket_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("maintenance_tickets.id"), index=True
    )
    rated_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    score: Mapped[int] = mapped_column(Integer)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
