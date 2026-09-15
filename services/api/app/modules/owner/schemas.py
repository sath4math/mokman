import uuid

from pydantic import BaseModel

from app.models.owner_profile import KycStatus, OwnershipType


class OwnerProfileIn(BaseModel):
    pan_number: str | None = None
    id_proof_type: str | None = None
    id_proof_number: str | None = None
    bank_account_number: str | None = None
    bank_ifsc: str | None = None
    bank_name: str | None = None
    ownership_type: OwnershipType = OwnershipType.SINGLE
    ownership_percentage: float | None = None
    nominee_name: str | None = None
    nominee_relationship: str | None = None
    nominee_phone: str | None = None
    emergency_contact_name: str | None = None
    emergency_contact_phone: str | None = None


class OwnerProfileOut(OwnerProfileIn):
    kyc_status: KycStatus

    model_config = {"from_attributes": True}


class AuthorizedRepresentativeIn(BaseModel):
    name: str
    relationship: str | None = None
    phone: str | None = None
    email: str | None = None


class AuthorizedRepresentativeOut(AuthorizedRepresentativeIn):
    id: uuid.UUID

    model_config = {"from_attributes": True}
