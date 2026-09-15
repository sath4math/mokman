import uuid
from datetime import date, datetime

from pydantic import BaseModel, EmailStr

from app.models.lease import LeaseStatus


class LeaseCreate(BaseModel):
    property_id: uuid.UUID
    tenant_email: EmailStr
    start_date: date
    end_date: date
    monthly_rent: float
    security_deposit: float
    lock_in_period_months: int | None = None
    notice_period_days: int | None = None
    annual_escalation_percentage: float | None = None
    responsibilities: str | None = None


class LeaseOut(BaseModel):
    id: uuid.UUID
    property_id: uuid.UUID
    tenant_id: uuid.UUID
    start_date: date
    end_date: date
    monthly_rent: float
    security_deposit: float
    lock_in_period_months: int | None
    notice_period_days: int | None
    annual_escalation_percentage: float | None
    responsibilities: str | None
    status: LeaseStatus
    owner_acknowledged_at: datetime | None
    tenant_acknowledged_at: datetime | None
    previous_lease_id: uuid.UUID | None

    model_config = {"from_attributes": True}
