import uuid
from datetime import date, datetime

from pydantic import BaseModel

from app.models.renovation import ProjectStatus


class ProjectCreate(BaseModel):
    property_id: uuid.UUID
    title: str
    description: str | None = None
    vendor_id: uuid.UUID | None = None
    budget_amount: float | None = None
    start_date: date | None = None
    end_date: date | None = None
    warranty_expires_on: date | None = None


class ProjectUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    vendor_id: uuid.UUID | None = None
    status: ProjectStatus | None = None
    budget_amount: float | None = None
    start_date: date | None = None
    end_date: date | None = None
    warranty_expires_on: date | None = None


class ProjectOut(BaseModel):
    id: uuid.UUID
    property_id: uuid.UUID
    title: str
    description: str | None
    vendor_id: uuid.UUID | None
    status: ProjectStatus
    budget_amount: float | None
    start_date: date | None
    end_date: date | None
    completed_at: datetime | None
    warranty_expires_on: date | None

    model_config = {"from_attributes": True}


class MilestoneCreate(BaseModel):
    title: str
    due_date: date | None = None
    payment_amount: float


class MilestoneOut(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    title: str
    due_date: date | None
    payment_amount: float
    completed_at: datetime | None
    paid_at: datetime | None
    expense_id: uuid.UUID | None

    model_config = {"from_attributes": True}
