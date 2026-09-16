import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.expense import ExpenseStatus


class ExpenseCreate(BaseModel):
    property_id: uuid.UUID
    category: str
    amount: float
    description: str | None = None
    vendor_id: uuid.UUID | None = None


class ExpenseOut(BaseModel):
    id: uuid.UUID
    property_id: uuid.UUID
    category: str
    amount: float
    description: str | None
    status: ExpenseStatus
    submitted_by: uuid.UUID
    approved_by: uuid.UUID | None
    approved_at: datetime | None
    vendor_id: uuid.UUID | None

    model_config = {"from_attributes": True}
