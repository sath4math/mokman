import uuid
from datetime import date

from pydantic import BaseModel

from app.models.rent import InvoiceStatus


class RentInvoiceOut(BaseModel):
    id: uuid.UUID
    lease_id: uuid.UUID
    property_id: uuid.UUID
    period_start: date
    period_end: date
    due_date: date
    amount_due: float
    status: InvoiceStatus

    model_config = {"from_attributes": True}


class PaymentCreate(BaseModel):
    amount: float
    method: str
    reference_note: str | None = None
