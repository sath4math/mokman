import enum
import uuid
from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, str_enum_column, uuid_pk


class UtilityResponsibility(str, enum.Enum):
    OWNER = "owner"
    TENANT = "tenant"


class UtilityConnection(Base, TimestampMixin):
    """A utility connection at a property (electricity/water/gas/...).

    `responsibility` records who is expected to pay — it doesn't wire into
    the ledger; if the owner wants a bill reflected financially they still
    log it through the existing Expense flow (see UtilityBill docstring).
    """

    __tablename__ = "utility_connections"

    id: Mapped[uuid.UUID] = uuid_pk()
    property_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("properties.id"), index=True)
    utility_type: Mapped[str] = mapped_column(String(50))
    provider: Mapped[str | None] = mapped_column(String(255), nullable=True)
    account_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    responsibility: Mapped[UtilityResponsibility] = mapped_column(
        str_enum_column(UtilityResponsibility, "utility_responsibility"), default=UtilityResponsibility.OWNER
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class UtilityBill(Base, TimestampMixin):
    """A recorded bill for a utility connection.

    `paid_at` is administrative record-keeping only — deliberately not an
    Expense/ledger entry, since "who's responsible" (owner vs tenant) and
    "what the owner's ledger owes" are different questions this pass
    doesn't try to auto-reconcile.
    """

    __tablename__ = "utility_bills"

    id: Mapped[uuid.UUID] = uuid_pk()
    connection_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("utility_connections.id"), index=True
    )
    billing_period_start: Mapped[date] = mapped_column(Date)
    billing_period_end: Mapped[date] = mapped_column(Date)
    amount: Mapped[float] = mapped_column(Float)
    due_date: Mapped[date] = mapped_column(Date)
    meter_reading: Mapped[float | None] = mapped_column(Float, nullable=True)
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    paid_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
