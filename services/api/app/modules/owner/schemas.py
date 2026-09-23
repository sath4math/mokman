import uuid

from pydantic import BaseModel, Field, model_validator

from app.models.owner_profile import KycStatus, OwnerPackage, OwnershipType


class OwnerProfileIn(BaseModel):
    """Full KYC submission -- every identity/bank/nominee/emergency-contact
    field is mandatory (product decision: KYC review needs the complete
    picture, not a partial one). ownership_percentage is conditionally
    required, checked below, since it only makes sense for joint ownership."""

    pan_number: str = Field(min_length=1)
    id_proof_type: str = Field(min_length=1)
    id_proof_number: str = Field(min_length=1)
    bank_account_number: str = Field(min_length=1)
    bank_ifsc: str = Field(min_length=1)
    bank_name: str = Field(min_length=1)
    ownership_type: OwnershipType = OwnershipType.SINGLE
    ownership_percentage: float | None = None
    nominee_name: str = Field(min_length=1)
    nominee_relationship: str = Field(min_length=1)
    nominee_phone: str = Field(min_length=1)
    emergency_contact_name: str = Field(min_length=1)
    emergency_contact_phone: str = Field(min_length=1)
    package: OwnerPackage = OwnerPackage.STARTER

    @model_validator(mode="after")
    def _require_percentage_for_joint_ownership(self) -> "OwnerProfileIn":
        if self.ownership_type == OwnershipType.JOINT and self.ownership_percentage is None:
            raise ValueError("ownership_percentage is required when ownership_type is joint")
        return self


class OwnerProfileOut(BaseModel):
    """Read shape stays fully nullable -- existing profiles saved before
    KYC fields became mandatory (or ones with a document but no saved
    profile yet) must still read back without validation errors."""

    pan_number: str | None
    id_proof_type: str | None
    id_proof_number: str | None
    bank_account_number: str | None
    bank_ifsc: str | None
    bank_name: str | None
    ownership_type: OwnershipType
    ownership_percentage: float | None
    nominee_name: str | None
    nominee_relationship: str | None
    nominee_phone: str | None
    emergency_contact_name: str | None
    emergency_contact_phone: str | None
    kyc_status: KycStatus
    package: OwnerPackage

    model_config = {"from_attributes": True}


class KycRejectRequest(BaseModel):
    reason: str


class OwnerProfileAdminOut(OwnerProfileOut):
    user_id: uuid.UUID
    full_name: str | None
    email: str | None


class AuthorizedRepresentativeIn(BaseModel):
    name: str
    relationship: str | None = None
    phone: str | None = None
    email: str | None = None


class AuthorizedRepresentativeOut(AuthorizedRepresentativeIn):
    id: uuid.UUID

    model_config = {"from_attributes": True}
