import uuid
from datetime import date, datetime

from pydantic import BaseModel

from app.models.compliance import ComplianceCategory


class ComplianceDueCreate(BaseModel):
    property_id: uuid.UUID
    category: ComplianceCategory = ComplianceCategory.OTHER
    description: str | None = None
    amount: float
    due_date: date


class MarkPaidRequest(BaseModel):
    paid_reference: str | None = None


class ComplianceDueOut(BaseModel):
    id: uuid.UUID
    property_id: uuid.UUID
    category: ComplianceCategory
    description: str | None
    amount: float
    due_date: date
    paid_at: datetime | None
    paid_reference: str | None

    model_config = {"from_attributes": True}
