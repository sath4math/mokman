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


class DiagnoseRequest(BaseModel):
    diagnosis_notes: str


class EstimateRequest(BaseModel):
    estimated_cost: float


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

    model_config = {"from_attributes": True}


class FieldStaffOut(BaseModel):
    id: uuid.UUID
    full_name: str | None
    email: str | None

    model_config = {"from_attributes": True}


class SlaCheckResult(BaseModel):
    breached_ticket_ids: list[uuid.UUID]
