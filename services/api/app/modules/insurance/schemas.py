import uuid
from datetime import date, datetime

from pydantic import BaseModel

from app.models.insurance import ClaimStatus


class InsurancePolicyCreate(BaseModel):
    property_id: uuid.UUID
    policy_number: str
    insurer_name: str
    category: str
    premium_amount: float
    premium_due_date: date | None = None
    coverage_amount: float | None = None
    start_date: date
    end_date: date


class InsurancePolicyUpdate(BaseModel):
    policy_number: str | None = None
    insurer_name: str | None = None
    category: str | None = None
    premium_amount: float | None = None
    premium_due_date: date | None = None
    coverage_amount: float | None = None
    start_date: date | None = None
    end_date: date | None = None
    is_active: bool | None = None


class InsurancePolicyOut(BaseModel):
    id: uuid.UUID
    property_id: uuid.UUID
    policy_number: str
    insurer_name: str
    category: str
    premium_amount: float
    premium_due_date: date | None
    coverage_amount: float | None
    start_date: date
    end_date: date
    is_active: bool

    model_config = {"from_attributes": True}


class InsuranceClaimCreate(BaseModel):
    incident_date: date
    description: str
    claim_amount: float
    surveyor_name: str | None = None


class InsuranceClaimUpdate(BaseModel):
    status: ClaimStatus | None = None
    surveyor_name: str | None = None
    settlement_amount: float | None = None


class InsuranceClaimOut(BaseModel):
    id: uuid.UUID
    policy_id: uuid.UUID
    incident_date: date
    description: str
    claim_amount: float
    status: ClaimStatus
    surveyor_name: str | None
    settlement_amount: float | None
    settled_at: datetime | None

    model_config = {"from_attributes": True}
