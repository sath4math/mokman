import uuid

from pydantic import BaseModel

from app.models.property import PropertyStatus


class PropertyCreate(BaseModel):
    category: str
    name: str
    address_line: str
    city: str
    state: str
    postal_code: str
    latitude: float | None = None
    longitude: float | None = None
    area_sqft: float | None = None
    num_floors: int | None = None
    num_units: int | None = None
    amenities: list[str] | None = None
    furnishing_status: str | None = None


class PropertyUpdate(BaseModel):
    name: str | None = None
    status: PropertyStatus | None = None
    area_sqft: float | None = None
    num_floors: int | None = None
    num_units: int | None = None
    amenities: list[str] | None = None
    furnishing_status: str | None = None


class PropertyOut(PropertyCreate):
    id: uuid.UUID
    owner_id: uuid.UUID
    status: PropertyStatus

    model_config = {"from_attributes": True}
