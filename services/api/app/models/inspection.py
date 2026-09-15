import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, str_enum_column, uuid_pk


class InspectionType(str, enum.Enum):
    MOVE_IN = "move_in"
    MOVE_OUT = "move_out"


class Inspection(Base, TimestampMixin):
    """A property walkthrough record — deliberately generic.

    Move-in/move-out today; Phase 4 formalizes this into the full
    inspection system (scheduled, complaint-triggered, etc.) by adding
    InspectionType values and fields, not by replacing this model.
    """

    __tablename__ = "inspections"

    id: Mapped[uuid.UUID] = uuid_pk()
    property_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("properties.id"), index=True)
    lease_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("leases.id"), nullable=True, index=True
    )
    inspection_type: Mapped[InspectionType] = mapped_column(str_enum_column(InspectionType, "inspection_type"))
    conducted_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))

    checklist: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    meter_readings: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    owner_signed_off_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    tenant_signed_off_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Move-out only. A plain recorded number, not a ledger — the real
    # deposit ledger is Phase 3 (Rent & Financial Management).
    deposit_deduction: Mapped[float | None] = mapped_column(Float, nullable=True)
    deposit_refund: Mapped[float | None] = mapped_column(Float, nullable=True)
