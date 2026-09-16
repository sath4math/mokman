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
    purchase_price: float | None = None
    current_market_value: float | None = None


class PropertyUpdate(BaseModel):
    name: str | None = None
    status: PropertyStatus | None = None
    area_sqft: float | None = None
    num_floors: int | None = None
    num_units: int | None = None
    amenities: list[str] | None = None
    furnishing_status: str | None = None
    purchase_price: float | None = None
    current_market_value: float | None = None


class PropertyOut(PropertyCreate):
    id: uuid.UUID
    owner_id: uuid.UUID
    status: PropertyStatus

    model_config = {"from_attributes": True}


class PropertyHealthScoreOut(BaseModel):
    score: int
    open_tickets: int
    repeat_failure_tickets: int
    sla_breached_tickets: int
    overdue_pm_items: int
    overdue_inspection_followups: int


class InvestmentSummaryOut(BaseModel):
    property_id: uuid.UUID
    property_name: str
    purchase_price: float | None
    current_market_value: float | None
    appreciation_percentage: float | None
    trailing_12_month_rent_income: float
    gross_yield_percentage: float | None
    total_net_income_all_time: float
    roi_percentage: float | None


class SaleReadinessOut(BaseModel):
    property_id: uuid.UUID
    is_ready: bool
    open_tickets: int
    has_active_lease: bool
    unsettled_insurance_claims: int
    incomplete_renovation_projects: int
