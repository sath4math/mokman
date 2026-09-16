import uuid
from datetime import date

from pydantic import BaseModel

from app.models.sale import SaleStatus


class SaleCreate(BaseModel):
    property_id: uuid.UUID
    listing_price: float | None = None
    buyer_name: str | None = None
    buyer_contact: str | None = None
    notes: str | None = None


class SaleUpdate(BaseModel):
    status: SaleStatus | None = None
    listing_price: float | None = None
    sale_price: float | None = None
    buyer_name: str | None = None
    buyer_contact: str | None = None
    agreement_date: date | None = None
    notes: str | None = None
    ownership_transferred: bool | None = None
    utilities_transferred: bool | None = None
    society_transferred: bool | None = None


class CompleteSaleRequest(BaseModel):
    sale_price: float
    settlement_date: date | None = None


class SaleOut(BaseModel):
    id: uuid.UUID
    property_id: uuid.UUID
    status: SaleStatus
    listing_price: float | None
    sale_price: float | None
    buyer_name: str | None
    buyer_contact: str | None
    agreement_date: date | None
    settlement_date: date | None
    ownership_transferred: bool
    utilities_transferred: bool
    society_transferred: bool
    notes: str | None

    model_config = {"from_attributes": True}
