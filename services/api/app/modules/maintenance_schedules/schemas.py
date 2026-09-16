import uuid
from datetime import date

from pydantic import BaseModel


class MaintenanceScheduleCreate(BaseModel):
    property_id: uuid.UUID
    category: str
    frequency_days: int
    last_serviced_on: date | None = None
    warranty_expires_on: date | None = None
    notes: str | None = None


class LogServiceRequest(BaseModel):
    serviced_on: date
    notes: str | None = None


class MaintenanceScheduleOut(BaseModel):
    id: uuid.UUID
    property_id: uuid.UUID
    category: str
    frequency_days: int
    last_serviced_on: date | None
    next_due_on: date
    warranty_expires_on: date | None
    notes: str | None
    is_active: bool

    model_config = {"from_attributes": True}
