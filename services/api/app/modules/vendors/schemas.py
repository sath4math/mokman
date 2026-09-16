import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class VendorIn(BaseModel):
    name: str
    service_category: str
    phone: str | None = None
    email: str | None = None
    gst_number: str | None = None
    pan_number: str | None = None
    notes: str | None = None


class VendorUpdate(BaseModel):
    name: str | None = None
    service_category: str | None = None
    phone: str | None = None
    email: str | None = None
    gst_number: str | None = None
    pan_number: str | None = None
    notes: str | None = None


class VendorOut(BaseModel):
    id: uuid.UUID
    name: str
    service_category: str
    phone: str | None
    email: str | None
    gst_number: str | None
    pan_number: str | None
    notes: str | None
    is_active: bool
    average_rating: float | None = None


class BlacklistRequest(BaseModel):
    reason: str


class VendorHistoryEventOut(BaseModel):
    id: uuid.UUID
    actor_id: uuid.UUID | None
    action: str
    after: dict | None
    created_at: datetime

    model_config = {"from_attributes": True}


class VendorRateCardIn(BaseModel):
    service_category: str
    unit: str
    rate: float
    notes: str | None = None


class VendorRateCardOut(BaseModel):
    id: uuid.UUID
    vendor_id: uuid.UUID
    service_category: str
    unit: str
    rate: float
    notes: str | None

    model_config = {"from_attributes": True}


class VendorRatingIn(BaseModel):
    ticket_id: uuid.UUID
    score: int = Field(ge=1, le=5)
    notes: str | None = None


class VendorRatingOut(BaseModel):
    id: uuid.UUID
    vendor_id: uuid.UUID
    ticket_id: uuid.UUID
    rated_by: uuid.UUID
    score: int
    notes: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
