import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.maintenance import TicketPriority, TicketStatus


class TicketCreate(BaseModel):
    property_id: uuid.UUID
    category: str
    description: str
    priority: TicketPriority = TicketPriority.MEDIUM


class AssignRequest(BaseModel):
    assigned_to: uuid.UUID | None = None
    assigned_vendor_id: uuid.UUID | None = None


class ResolveRequest(BaseModel):
    resolution_notes: str
    latitude: float | None = None
    longitude: float | None = None


class DiagnoseRequest(BaseModel):
    diagnosis_notes: str


class EstimateRequest(BaseModel):
    estimated_cost: float


class StartRequest(BaseModel):
    latitude: float | None = None
    longitude: float | None = None


class ChecklistTemplateIn(BaseModel):
    category: str
    items: list[str]


class ChecklistTemplateUpdate(BaseModel):
    items: list[str] | None = None
    is_active: bool | None = None


class ChecklistTemplateOut(BaseModel):
    id: uuid.UUID
    category: str
    items: list[str]
    is_active: bool

    model_config = {"from_attributes": True}


class ChecklistItemUpdate(BaseModel):
    item: str
    checked: bool


class TicketOut(BaseModel):
    id: uuid.UUID
    property_id: uuid.UUID
    category: str
    description: str
    priority: TicketPriority
    status: TicketStatus
    raised_by: uuid.UUID
    assigned_to: uuid.UUID | None
    assigned_vendor_id: uuid.UUID | None
    resolution_notes: str | None
    closed_at: datetime | None
    created_at: datetime
    sla_due_at: datetime | None
    sla_breached_at: datetime | None
    diagnosis_notes: str | None
    diagnosed_at: datetime | None
    diagnosed_by: uuid.UUID | None
    estimated_cost: float | None
    estimated_at: datetime | None
    estimated_by: uuid.UUID | None
    approved_at: datetime | None
    approved_by: uuid.UUID | None
    checklist: dict[str, bool] | None
    check_in_at: datetime | None
    check_in_latitude: float | None
    check_in_longitude: float | None
    check_out_at: datetime | None
    check_out_latitude: float | None
    check_out_longitude: float | None
    rework_count: int

    model_config = {"from_attributes": True}


class FieldStaffOut(BaseModel):
    id: uuid.UUID
    full_name: str | None
    email: str | None

    model_config = {"from_attributes": True}


class SlaCheckResult(BaseModel):
    breached_ticket_ids: list[uuid.UUID]
