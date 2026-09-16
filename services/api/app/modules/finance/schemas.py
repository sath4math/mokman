import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.ledger import LedgerEntryType


class LedgerEntryOut(BaseModel):
    id: uuid.UUID
    property_id: uuid.UUID
    lease_id: uuid.UUID | None
    invoice_id: uuid.UUID | None
    expense_id: uuid.UUID | None
    inspection_id: uuid.UUID | None
    entry_type: LedgerEntryType
    amount: float
    method: str | None
    reference_note: str | None
    recorded_by: uuid.UUID
    occurred_at: datetime

    model_config = {"from_attributes": True}


class StatementOut(BaseModel):
    year: int
    month: int
    rent_collected: float
    expenses: float
    mokman_fee: float
    net_payable: float
    entries: list[LedgerEntryOut]


class PropertyProfitabilityOut(BaseModel):
    property_id: uuid.UUID
    property_name: str
    year: int
    month: int
    net_payable: float


class ExpenseAnomalyOut(BaseModel):
    expense_id: uuid.UUID
    property_id: uuid.UUID
    category: str
    amount: float
    reason: str
