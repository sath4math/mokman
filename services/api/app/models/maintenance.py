import enum
import uuid
from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, str_enum_column, uuid_pk


class TicketStatus(str, enum.Enum):
    OPEN = "open"
    DIAGNOSED = "diagnosed"
    ESTIMATED = "estimated"
    APPROVED = "approved"
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

    States: open -> [diagnosed -> estimated -> approved] -> assigned ->
    in_progress -> resolved -> closed (+ reopen from closed). The
    diagnosed/estimated/approved chain (Phase 5a) is optional, not
    mandatory — assignment still accepts a ticket straight from `open`
    for simple jobs that don't need a cost gate; `estimated_cost` is an
    informational quote gating assignment, not a financial transaction.
    Cost tracking still reuses the Phase 3 Expense/ledger system
    post-hoc rather than a parallel accounting pipeline.
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

    diagnosis_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    diagnosed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    diagnosed_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    estimated_cost: Mapped[float | None] = mapped_column(Float, nullable=True)
    estimated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    estimated_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    approved_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # sla_due_at is set once at creation from PRIORITY_SLA_HOURS and never
    # recomputed; sla_breached_at is set once by the cron-triggered
    # escalation check (POST /internal/maintenance/sla-check) and never
    # cleared, same "write once" spirit as LedgerEntry.
    sla_due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    sla_breached_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Auto-populated from a matching ChecklistTemplate at assignment time
    # (Phase 5b); None means no template exists for this category, which
    # is what keeps the quality gate on resolve optional rather than
    # mandatory for every ticket.
    checklist: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    check_in_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    check_in_latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    check_in_longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    check_out_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    check_out_latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    check_out_longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    rework_count: Mapped[int] = mapped_column(Integer, default=0)

    # Set optionally at close_ticket; a repeat within this window on the
    # same property+category auto-flags the new ticket below. No warranty
    # set on the prior job means repeat-failure detection never fires —
    # optional, same as every other gate introduced in 5a/5b.
    warranty_expires_on: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_repeat_failure: Mapped[bool] = mapped_column(Boolean, default=False)
    related_ticket_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("maintenance_tickets.id"), nullable=True
    )


class ServiceCategory(Base, TimestampMixin):
    """An admin-managed reference entry for a ticket `category` string.

    Additive, not enforced: `MaintenanceTicket.category` stays free-text.
    A category with no matching row here behaves exactly as before this
    model existed (MEDIUM priority, PRIORITY_SLA_HOURS-only SLA). A match
    only ever supplies defaults/gates, never forces every category
    through this catalog.
    """

    __tablename__ = "service_categories"

    id: Mapped[uuid.UUID] = uuid_pk()
    name: Mapped[str] = mapped_column(String(100), unique=True)
    default_priority: Mapped[TicketPriority] = mapped_column(
        str_enum_column(TicketPriority, "ticket_priority"), default=TicketPriority.MEDIUM
    )
    estimated_completion_hours: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class ChecklistTemplate(Base, TimestampMixin):
    """An admin-managed SOP checklist, one per ticket category.

    Auto-attached to a ticket's `checklist` at assignment time — not a
    per-ticket resource, so there's no ticket_id here.
    """

    __tablename__ = "checklist_templates"

    id: Mapped[uuid.UUID] = uuid_pk()
    category: Mapped[str] = mapped_column(String(100), unique=True)
    items: Mapped[list] = mapped_column(JSONB)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


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
