import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.compliance import ComplianceDue
from app.modules.compliance.schemas import ComplianceDueCreate, MarkPaidRequest
from app.modules.properties.service import get_property_by_id


class ComplianceDueNotFoundError(Exception):
    pass


class NotPropertyOwnerError(Exception):
    pass


def _require_owner_or_admin(db: Session, property_id: uuid.UUID, user_id: uuid.UUID, role: str) -> None:
    property_ = get_property_by_id(db, property_id)
    if role != "admin" and property_.owner_id != user_id:
        raise NotPropertyOwnerError


def create_due(db: Session, user_id: uuid.UUID, role: str, data: ComplianceDueCreate) -> ComplianceDue:
    _require_owner_or_admin(db, data.property_id, user_id, role)
    due = ComplianceDue(**data.model_dump())
    db.add(due)
    db.commit()
    db.refresh(due)
    return due


def list_dues(db: Session, property_id: uuid.UUID, due_only: bool) -> list[ComplianceDue]:
    stmt = select(ComplianceDue).where(ComplianceDue.property_id == property_id)
    if due_only:
        stmt = stmt.where(ComplianceDue.paid_at.is_(None)).where(
            ComplianceDue.due_date <= datetime.now(UTC).date()
        )
    return list(db.execute(stmt.order_by(ComplianceDue.due_date)).scalars())


def get_due(db: Session, due_id: uuid.UUID) -> ComplianceDue:
    due = db.get(ComplianceDue, due_id)
    if due is None:
        raise ComplianceDueNotFoundError
    return due


def mark_due_paid(
    db: Session, due_id: uuid.UUID, user_id: uuid.UUID, role: str, data: MarkPaidRequest
) -> ComplianceDue:
    due = get_due(db, due_id)
    _require_owner_or_admin(db, due.property_id, user_id, role)
    due.paid_at = datetime.now(UTC)
    due.paid_reference = data.paid_reference
    db.commit()
    db.refresh(due)
    return due
