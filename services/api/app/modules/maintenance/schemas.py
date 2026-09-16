import uuid
from datetime import date, datetime

from pydantic import BaseModel

from app.models.maintenance import TicketPriority, TicketStatus


class TicketCreate(BaseModel):
    property_id: uuid.UUID
    category: str
    description: str
    priority: TicketPriority | None = None


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


class CloseRequest(BaseModel):
    warranty_days: int | None = None


class ServiceCategoryIn(BaseModel):
    name: str
    default_priority: TicketPriority = TicketPriority.MEDIUM
    estimated_completion_hours: int | None = None


class ServiceCategoryUpdate(BaseModel):
    default_priority: TicketPriority | None = None
    estimated_completion_hours: int | None = None
    is_active: bool | None = None


class ServiceCategoryOut(BaseModel):
    id: uuid.UUID
    name: str
    default_priority: TicketPriority
    estimated_completion_hours: int | None
    is_active: bool

    model_config = {"from_attributes": True}


class MaintenanceSummaryOut(BaseModel):
    total_tickets: int
    closed_tickets: int
    repeat_failure_count: int
    active_warranty_count: int
    tickets_with_estimate: int
    total_estimated_cost: float
    total_actual_cost: float
    cost_variance: float


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
    warranty_expires_on: date | None
    is_repeat_failure: bool
    related_ticket_id: uuid.UUID | None

    model_config = {"from_attributes": True}


class FieldStaffOut(BaseModel):
    id: uuid.UUID
    full_name: str | None
    email: str | None

    model_config = {"from_attributes": True}


class SlaCheckResult(BaseModel):
    breached_ticket_ids: list[uuid.UUID]
