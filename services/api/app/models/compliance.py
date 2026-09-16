import enum
import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, str_enum_column, uuid_pk


class ComplianceCategory(str, enum.Enum):
    SOCIETY_MAINTENANCE = "society_maintenance"
    PROPERTY_TAX = "property_tax"
    OTHER = "other"


class ComplianceDue(Base, TimestampMixin):
    """A society or government due for a property (maintenance charge,
    property tax, etc.) — structurally identical for both per the
    phase-wise plan, so one model covers both categories.

    Notices and NOCs aren't modeled here — they're `Document` rows
    (owner_type="property", document_type in "noc"/"society_notice"/
    "tax_receipt"), reusing the existing document vault.
    """

    __tablename__ = "compliance_dues"

    id: Mapped[uuid.UUID] = uuid_pk()
    property_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("properties.id"), index=True)
    category: Mapped[ComplianceCategory] = mapped_column(
        str_enum_column(ComplianceCategory, "compliance_category"), default=ComplianceCategory.OTHER
    )
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    amount: Mapped[float] = mapped_column(Float)
    due_date: Mapped[date] = mapped_column(Date)
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    paid_reference: Mapped[str | None] = mapped_column(String(255), nullable=True)
