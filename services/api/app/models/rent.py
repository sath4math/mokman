import enum
import uuid
from datetime import date

from sqlalchemy import Date as SADate
from sqlalchemy import Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, str_enum_column, uuid_pk


class InvoiceStatus(str, enum.Enum):
    PENDING = "pending"
    PARTIALLY_PAID = "partially_paid"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class RentInvoice(Base, TimestampMixin):
    """One billing period's rent for a lease. Status is recomputed from
    the immutable ledger on read, not stored as a source of truth."""

    __tablename__ = "rent_invoices"

    id: Mapped[uuid.UUID] = uuid_pk()
    lease_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("leases.id"), index=True)
    property_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("properties.id"), index=True)

    period_start: Mapped[date] = mapped_column(SADate)
    period_end: Mapped[date] = mapped_column(SADate)
    due_date: Mapped[date] = mapped_column(SADate)
    amount_due: Mapped[float] = mapped_column(Float)

    status: Mapped[InvoiceStatus] = mapped_column(
        str_enum_column(InvoiceStatus, "invoice_status"), default=InvoiceStatus.PENDING
    )
