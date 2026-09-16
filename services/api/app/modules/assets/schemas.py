import uuid
from datetime import date

from pydantic import BaseModel


class AssetCreate(BaseModel):
    property_id: uuid.UUID
    category: str
    name: str
    purchase_date: date | None = None
    purchase_cost: float | None = None
    vendor_id: uuid.UUID | None = None
    warranty_expires_on: date | None = None
    useful_life_years: int | None = None


class AssetUpdate(BaseModel):
    property_id: uuid.UUID | None = None
    category: str | None = None
    name: str | None = None
    purchase_date: date | None = None
    purchase_cost: float | None = None
    vendor_id: uuid.UUID | None = None
    warranty_expires_on: date | None = None
    useful_life_years: int | None = None


class DisposeRequest(BaseModel):
    reason: str


class AssetOut(BaseModel):
    id: uuid.UUID
    property_id: uuid.UUID
    category: str
    name: str
    purchase_date: date | None
    purchase_cost: float | None
    vendor_id: uuid.UUID | None
    warranty_expires_on: date | None
    useful_life_years: int | None
    is_active: bool
    disposed_reason: str | None
    replaced_by_asset_id: uuid.UUID | None
    current_value: float | None

    model_config = {"from_attributes": True}
