import uuid
from datetime import date, datetime

from pydantic import BaseModel

from app.models.utility import UtilityResponsibility


class UtilityConnectionCreate(BaseModel):
    property_id: uuid.UUID
    utility_type: str
    provider: str | None = None
    account_number: str | None = None
    responsibility: UtilityResponsibility = UtilityResponsibility.OWNER


class UtilityConnectionOut(BaseModel):
    id: uuid.UUID
    property_id: uuid.UUID
    utility_type: str
    provider: str | None
    account_number: str | None
    responsibility: UtilityResponsibility
    is_active: bool

    model_config = {"from_attributes": True}


class UtilityBillCreate(BaseModel):
    billing_period_start: date
    billing_period_end: date
    amount: float
    due_date: date
    meter_reading: float | None = None


class UtilityBillOut(BaseModel):
    id: uuid.UUID
    connection_id: uuid.UUID
    billing_period_start: date
    billing_period_end: date
    amount: float
    due_date: date
    meter_reading: float | None
    paid_at: datetime | None
    paid_by: uuid.UUID | None

    model_config = {"from_attributes": True}
