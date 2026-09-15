import enum
import uuid
from datetime import date, datetime

from sqlalchemy import Date as SADate
from sqlalchemy import DateTime, Float, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, str_enum_column, uuid_pk


class LeaseStatus(str, enum.Enum):
    DRAFT = "draft"
    PENDING_ACKNOWLEDGMENT = "pending_acknowledgment"
    ACTIVE = "active"
    TERMINATED = "terminated"
    EXPIRED = "expired"


class Lease(Base, TimestampMixin):
    """A lease between an owner's property and a tenant.

    Append-only in spirit: once acknowledged, terms are not edited in
    place. A renewal creates a new Lease row pointing back via
    previous_lease_id rather than mutating the signed record.
    """

    __tablename__ = "leases"

    id: Mapped[uuid.UUID] = uuid_pk()
    property_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("properties.id"), index=True)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)

    start_date: Mapped[date] = mapped_column(SADate)
    end_date: Mapped[date] = mapped_column(SADate)
    monthly_rent: Mapped[float] = mapped_column(Float)
    security_deposit: Mapped[float] = mapped_column(Float)
    lock_in_period_months: Mapped[int | None] = mapped_column(Integer, nullable=True)
    notice_period_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    annual_escalation_percentage: Mapped[float | None] = mapped_column(Float, nullable=True)
    responsibilities: Mapped[str | None] = mapped_column(Text, nullable=True)

    status: Mapped[LeaseStatus] = mapped_column(
        str_enum_column(LeaseStatus, "lease_status"), default=LeaseStatus.PENDING_ACKNOWLEDGMENT
    )
    owner_acknowledged_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    tenant_acknowledged_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    previous_lease_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("leases.id"), nullable=True
    )
