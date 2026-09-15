import enum
import uuid

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, str_enum_column


class TenantVerificationStatus(str, enum.Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"


class TenantProfile(Base, TimestampMixin):
    """Verification and household details for a user with the tenant role.

    One-to-one with User via user_id as the primary key. Verification is
    manual/self-reported for now — same deferral as OwnerProfile.kyc_status.
    """

    __tablename__ = "tenant_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)

    id_proof_type: Mapped[str | None] = mapped_column(String(20), nullable=True)
    id_proof_number: Mapped[str | None] = mapped_column(String(50), nullable=True)
    occupants_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    vehicles: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    pets: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    emergency_contact_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    emergency_contact_phone: Mapped[str | None] = mapped_column(String(20), nullable=True)

    verification_status: Mapped[TenantVerificationStatus] = mapped_column(
        str_enum_column(TenantVerificationStatus, "tenant_verification_status"),
        default=TenantVerificationStatus.PENDING,
    )
