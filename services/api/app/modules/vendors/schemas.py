import uuid

from pydantic import BaseModel


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
    is_active: bool | None = None


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

    model_config = {"from_attributes": True}
