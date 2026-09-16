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

    model_config = {"from_attributes": True}


class FieldStaffOut(BaseModel):
    id: uuid.UUID
    full_name: str | None
    email: str | None

    model_config = {"from_attributes": True}
