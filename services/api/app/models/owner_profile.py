import enum
import uuid

from sqlalchemy import Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, str_enum_column, uuid_pk


class OwnershipType(str, enum.Enum):
    SINGLE = "single"
    JOINT = "joint"


class KycStatus(str, enum.Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"


class OwnerPackage(str, enum.Enum):
    """The four Owner Package tiers from the product spec (Section 3.1).

    Phase 6a: data only, no enforcement — every feature built in Phases
    1-5 works identically regardless of this value. Eligibility rules
    that actually read it are a later phase's job.
    """

    STARTER = "starter"
    MANAGED = "managed"
    FULL_CARE = "full_care"
    COMPLETE = "complete"


class OwnerProfile(Base, TimestampMixin):
    """KYC, bank, and ownership details for a user with the owner role.

    One-to-one with User via user_id as the primary key. Verification is
    manual/self-reported for now — third-party PAN/Aadhaar verification is a
    vendor-selection decision deferred per the phase-wise plan, not built
    here.
    """

    __tablename__ = "owner_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)

    pan_number: Mapped[str | None] = mapped_column(String(20), nullable=True)
    id_proof_type: Mapped[str | None] = mapped_column(String(20), nullable=True)  # "aadhaar" | "passport"
    id_proof_number: Mapped[str | None] = mapped_column(String(50), nullable=True)

    bank_account_number: Mapped[str | None] = mapped_column(String(50), nullable=True)
    bank_ifsc: Mapped[str | None] = mapped_column(String(20), nullable=True)
    bank_name: Mapped[str | None] = mapped_column(String(255), nullable=True)

    ownership_type: Mapped[OwnershipType] = mapped_column(
        str_enum_column(OwnershipType, "ownership_type"), default=OwnershipType.SINGLE
    )
    ownership_percentage: Mapped[float | None] = mapped_column(Float, nullable=True)

    nominee_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    nominee_relationship: Mapped[str | None] = mapped_column(String(100), nullable=True)
    nominee_phone: Mapped[str | None] = mapped_column(String(20), nullable=True)

    emergency_contact_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    emergency_contact_phone: Mapped[str | None] = mapped_column(String(20), nullable=True)

    kyc_status: Mapped[KycStatus] = mapped_column(str_enum_column(KycStatus, "kyc_status"), default=KycStatus.PENDING)
    package: Mapped[OwnerPackage] = mapped_column(
        str_enum_column(OwnerPackage, "owner_package"), default=OwnerPackage.STARTER
    )


class AuthorizedRepresentative(Base, TimestampMixin):
    """A person the owner authorizes to act on their behalf (multiple allowed)."""

    __tablename__ = "authorized_representatives"

    id: Mapped[uuid.UUID] = uuid_pk()
    owner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    name: Mapped[str] = mapped_column(String(255))
    relationship: Mapped[str | None] = mapped_column(String(100), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
