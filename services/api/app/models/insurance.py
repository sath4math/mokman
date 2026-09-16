import enum
import uuid
from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, str_enum_column, uuid_pk


class ClaimStatus(str, enum.Enum):
    FILED = "filed"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    SETTLED = "settled"


class InsurancePolicy(Base, TimestampMixin):
    """A property insurance policy (Phase 8a).

    `category` stays free-text (e.g. "property", "contents",
    "liability"), same convention as every other free-text category in
    this codebase. Premium tracking is administrative record-keeping
    only, not auto-posted to the ledger -- same "who's responsible" vs
    "what the ledger owes" split 4c already established for
    ComplianceDue.
    """

    __tablename__ = "insurance_policies"

    id: Mapped[uuid.UUID] = uuid_pk()
    property_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("properties.id"), index=True)
    policy_number: Mapped[str] = mapped_column(String(100))
    insurer_name: Mapped[str] = mapped_column(String(255))
    category: Mapped[str] = mapped_column(String(100))
    premium_amount: Mapped[float] = mapped_column(Float)
    premium_due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    coverage_amount: Mapped[float | None] = mapped_column(Float, nullable=True)
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date] = mapped_column(Date)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class InsuranceClaim(Base, TimestampMixin):
    """A claim filed against an InsurancePolicy.

    "Surveyor coordination" reduces to a contact-name field, not a
    scheduling workflow -- same proportionate reduction 4c applied to
    society/government coordination.
    """

    __tablename__ = "insurance_claims"

    id: Mapped[uuid.UUID] = uuid_pk()
    policy_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("insurance_policies.id"), index=True)
    incident_date: Mapped[date] = mapped_column(Date)
    description: Mapped[str] = mapped_column(Text)
    claim_amount: Mapped[float] = mapped_column(Float)
    status: Mapped[ClaimStatus] = mapped_column(str_enum_column(ClaimStatus, "claim_status"), default=ClaimStatus.FILED)
    surveyor_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    settlement_amount: Mapped[float | None] = mapped_column(Float, nullable=True)
    settled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
