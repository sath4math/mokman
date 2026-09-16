import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, str_enum_column, uuid_pk


class ExpenseStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class Expense(Base, TimestampMixin):
    """A property expense. Owner-submitted expenses are auto-approved;
    admin-submitted ones need the property owner's approval."""

    __tablename__ = "expenses"

    id: Mapped[uuid.UUID] = uuid_pk()
    property_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("properties.id"), index=True)
    category: Mapped[str] = mapped_column(String(100))
    amount: Mapped[float] = mapped_column(Float)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    status: Mapped[ExpenseStatus] = mapped_column(
        str_enum_column(ExpenseStatus, "expense_status"), default=ExpenseStatus.PENDING
    )
    submitted_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    approved_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    vendor_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("vendors.id"), nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
