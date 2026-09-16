import enum
import uuid
from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, str_enum_column, uuid_pk


class TicketStatus(str, enum.Enum):
    OPEN = "open"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class TicketPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class MaintenanceTicket(Base, TimestampMixin):
    """A maintenance complaint, from raising through closure.

    States are deliberately simplified from the full doc's
    Complaint->Assessment->Diagnosis->Estimate->Approval->Assignment->
    Work->Inspection->Invoice->Closure chain: open -> assigned ->
    in_progress -> resolved -> closed (+ reopen from closed). Cost
    tracking reuses the Phase 3 Expense/ledger system rather than a
    parallel estimate-approval pipeline.
    """

    __tablename__ = "maintenance_tickets"

    id: Mapped[uuid.UUID] = uuid_pk()
    property_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("properties.id"), index=True)
    category: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(Text)
    priority: Mapped[TicketPriority] = mapped_column(
        str_enum_column(TicketPriority, "ticket_priority"), default=TicketPriority.MEDIUM
    )
    status: Mapped[TicketStatus] = mapped_column(
        str_enum_column(TicketStatus, "ticket_status"), default=TicketStatus.OPEN
    )
    raised_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    assigned_to: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    # Exactly one of assigned_to (field_staff) / assigned_vendor_id is set at a time —
    # a vendor has no login, so only the owner/admin can drive its ticket's lifecycle.
    assigned_vendor_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("vendors.id"), nullable=True
    )
    resolution_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # sla_due_at is set once at creation from PRIORITY_SLA_HOURS and never
    # recomputed; sla_breached_at is set once by the cron-triggered
    # escalation check (POST /internal/maintenance/sla-check) and never
    # cleared, same "write once" spirit as LedgerEntry.
    sla_due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    sla_breached_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class MaintenanceSchedule(Base, TimestampMixin):
    """A recurring preventive-maintenance item for a property/asset.

    `next_due_on` is stored (not computed on read) since it only changes
    when a service is logged, unlike RentInvoice's per-read status —
    reading "is this due" is just `next_due_on <= today`. No scheduler:
    raising an actual ticket off a due schedule is a manual owner/admin
    action via the existing maintenance-tickets flow.
    """

    __tablename__ = "maintenance_schedules"

    id: Mapped[uuid.UUID] = uuid_pk()
    property_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("properties.id"), index=True)
    category: Mapped[str] = mapped_column(String(100))
    frequency_days: Mapped[int] = mapped_column(Integer)
    last_serviced_on: Mapped[date | None] = mapped_column(Date, nullable=True)
    next_due_on: Mapped[date] = mapped_column(Date)
    warranty_expires_on: Mapped[date | None] = mapped_column(Date, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
