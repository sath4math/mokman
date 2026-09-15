import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, str_enum_column, uuid_pk


class LedgerEntryType(str, enum.Enum):
    RENT_PAYMENT = "rent_payment"
    MOKMAN_FEE = "mokman_fee"
    DEPOSIT_COLLECTED = "deposit_collected"
    DEPOSIT_DEDUCTION = "deposit_deduction"
    DEPOSIT_REFUND = "deposit_refund"
    EXPENSE = "expense"


class LedgerEntry(Base):
    """An immutable, append-only financial transaction log.

    Never updated or deleted once written — corrections are made by
    writing an offsetting entry, not editing this row. A single entry
    belongs to exactly one of lease/invoice/expense/inspection,
    depending on entry_type.
    """

    __tablename__ = "ledger_entries"

    id: Mapped[uuid.UUID] = uuid_pk()
    property_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("properties.id"), index=True)
    lease_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("leases.id"), nullable=True, index=True
    )
    invoice_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("rent_invoices.id"), nullable=True, index=True
    )
    expense_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("expenses.id"), nullable=True, index=True
    )
    inspection_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("inspections.id"), nullable=True, index=True
    )

    entry_type: Mapped[LedgerEntryType] = mapped_column(str_enum_column(LedgerEntryType, "ledger_entry_type"))
    amount: Mapped[float] = mapped_column(Float)
    method: Mapped[str | None] = mapped_column(String(30), nullable=True)
    reference_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    recorded_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
