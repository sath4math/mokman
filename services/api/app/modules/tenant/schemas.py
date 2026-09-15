from pydantic import BaseModel

from app.models.tenant_profile import TenantVerificationStatus


class TenantProfileIn(BaseModel):
    id_proof_type: str | None = None
    id_proof_number: str | None = None
    occupants_count: int | None = None
    vehicles: list[str] | None = None
    pets: list[str] | None = None
    emergency_contact_name: str | None = None
    emergency_contact_phone: str | None = None


class TenantProfileOut(TenantProfileIn):
    verification_status: TenantVerificationStatus

    model_config = {"from_attributes": True}
