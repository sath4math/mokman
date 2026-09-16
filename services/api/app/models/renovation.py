import enum
import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, str_enum_column, uuid_pk


class ProjectStatus(str, enum.Enum):
    REQUESTED = "requested"
    APPROVED = "approved"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class RenovationProject(Base, TimestampMixin):
    """A property renovation/project, request through handover (Phase 8b).

    Contractor assignment reuses the existing Vendor directory rather
    than a new concept. Progress tracking is just the milestone list
    below (each with its own completed_at) plus this row's own status
    -- no separate progress-percentage field to keep in sync.
    """

    __tablename__ = "renovation_projects"

    id: Mapped[uuid.UUID] = uuid_pk()
    property_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("properties.id"), index=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    vendor_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("vendors.id"), nullable=True)
    status: Mapped[ProjectStatus] = mapped_column(
        str_enum_column(ProjectStatus, "project_status"), default=ProjectStatus.REQUESTED
    )
    budget_amount: Mapped[float | None] = mapped_column(Float, nullable=True)
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    warranty_expires_on: Mapped[date | None] = mapped_column(Date, nullable=True)


class ProjectMilestone(Base, TimestampMixin):
    """A payment/progress milestone within a RenovationProject.

    Unlike 8a's insurance/compliance dues, paying a milestone reuses
    the Expense/ledger pipeline directly (see renovation/service.py's
    pay_milestone) -- a renovation payment is a real operational cost,
    the same as a vendor invoice, not an administrative reminder.
    """

    __tablename__ = "project_milestones"

    id: Mapped[uuid.UUID] = uuid_pk()
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("renovation_projects.id"), index=True
    )
    title: Mapped[str] = mapped_column(String(255))
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    payment_amount: Mapped[float] = mapped_column(Float)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    expense_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("expenses.id"), nullable=True
    )
