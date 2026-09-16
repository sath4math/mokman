import enum
import uuid
from datetime import date

from sqlalchemy import Boolean, Date, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, str_enum_column, uuid_pk


class SaleStatus(str, enum.Enum):
    LISTED = "listed"
    UNDER_NEGOTIATION = "under_negotiation"
    AGREEMENT_SIGNED = "agreement_signed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class PropertySale(Base, TimestampMixin):
    """A property sale/exit record, the natural end of the Digital
    Property Passport lifecycle from Phase 1 (Phase 8d).

    Buyer/site-visit coordination reduces to contact fields, not a
    scheduling workflow -- same proportionate cut 8a applied to
    "surveyor coordination". Ownership/utility/society transfer
    reduces to a checklist of booleans, not three separate workflows.
    Settlement stays ledger-isolated like 8a's insurance/compliance --
    a one-off capital sale isn't a recurring operational cost.
    """

    __tablename__ = "property_sales"

    id: Mapped[uuid.UUID] = uuid_pk()
    property_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("properties.id"), index=True)
    status: Mapped[SaleStatus] = mapped_column(str_enum_column(SaleStatus, "sale_status"), default=SaleStatus.LISTED)
    listing_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    sale_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    buyer_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    buyer_contact: Mapped[str | None] = mapped_column(String(255), nullable=True)
    agreement_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    settlement_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    ownership_transferred: Mapped[bool] = mapped_column(Boolean, default=False)
    utilities_transferred: Mapped[bool] = mapped_column(Boolean, default=False)
    society_transferred: Mapped[bool] = mapped_column(Boolean, default=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
