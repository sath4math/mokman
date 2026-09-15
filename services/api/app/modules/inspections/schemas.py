import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.inspection import InspectionType


class InspectionCreate(BaseModel):
    property_id: uuid.UUID
    lease_id: uuid.UUID | None = None
    inspection_type: InspectionType
    checklist: dict | None = None
    notes: str | None = None
    meter_readings: dict | None = None


class InspectionUpdate(BaseModel):
    checklist: dict | None = None
    notes: str | None = None
    meter_readings: dict | None = None
    deposit_deduction: float | None = None
    deposit_refund: float | None = None


class InspectionOut(BaseModel):
    id: uuid.UUID
    property_id: uuid.UUID
    lease_id: uuid.UUID | None
    inspection_type: InspectionType
    conducted_by: uuid.UUID
    checklist: dict | None
    notes: str | None
    meter_readings: dict | None
    owner_signed_off_at: datetime | None
    tenant_signed_off_at: datetime | None
    deposit_deduction: float | None
    deposit_refund: float | None

    model_config = {"from_attributes": True}
