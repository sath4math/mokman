import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.inspection import Inspection
from app.models.maintenance import MaintenanceSchedule, MaintenanceTicket, TicketStatus
from app.models.property import Property
from app.modules.properties.schemas import PropertyCreate, PropertyHealthScoreOut, PropertyUpdate

# Phase 7b: a deterministic 0-100 score, not a trained/ML prediction --
# capped deductions per signal so no single ticket-heavy property can
# swamp the others, and each count is returned alongside the score so
# it's explainable, not a black box.
_OPEN_TICKET_PENALTY = 5
_OPEN_TICKET_CAP = 30
_REPEAT_FAILURE_PENALTY = 10
_REPEAT_FAILURE_CAP = 20
_SLA_BREACH_PENALTY = 10
_SLA_BREACH_CAP = 20
_OVERDUE_PM_PENALTY = 5
_OVERDUE_PM_CAP = 20
_OVERDUE_FOLLOWUP_PENALTY = 10
_OVERDUE_FOLLOWUP_CAP = 20


class PropertyNotFoundError(Exception):
    pass


def create_property(db: Session, owner_id: uuid.UUID, data: PropertyCreate) -> Property:
    property_ = Property(owner_id=owner_id, **data.model_dump())
    db.add(property_)
    db.commit()
    db.refresh(property_)
    return property_


def list_properties_for_owner(db: Session, owner_id: uuid.UUID) -> list[Property]:
    return list(db.execute(select(Property).where(Property.owner_id == owner_id)).scalars())


def list_all_properties(db: Session) -> list[Property]:
    return list(db.execute(select(Property)).scalars())


def get_owned_property(db: Session, owner_id: uuid.UUID, property_id: uuid.UUID) -> Property:
    property_ = db.get(Property, property_id)
    if property_ is None or property_.owner_id != owner_id:
        raise PropertyNotFoundError
    return property_


def get_property_by_id(db: Session, property_id: uuid.UUID) -> Property:
    property_ = db.get(Property, property_id)
    if property_ is None:
        raise PropertyNotFoundError
    return property_


def update_property(db: Session, owner_id: uuid.UUID, property_id: uuid.UUID, data: PropertyUpdate) -> Property:
    property_ = get_owned_property(db, owner_id, property_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(property_, field, value)
    db.commit()
    db.refresh(property_)
    return property_


def compute_health_score(db: Session, property_id: uuid.UUID) -> PropertyHealthScoreOut:
    today = datetime.now(UTC).date()

    open_tickets = db.execute(
        select(func.count())
        .select_from(MaintenanceTicket)
        .where(MaintenanceTicket.property_id == property_id, MaintenanceTicket.status != TicketStatus.CLOSED)
    ).scalar_one()
    repeat_failure_tickets = db.execute(
        select(func.count())
        .select_from(MaintenanceTicket)
        .where(MaintenanceTicket.property_id == property_id, MaintenanceTicket.is_repeat_failure.is_(True))
    ).scalar_one()
    sla_breached_tickets = db.execute(
        select(func.count())
        .select_from(MaintenanceTicket)
        .where(MaintenanceTicket.property_id == property_id, MaintenanceTicket.sla_breached_at.is_not(None))
    ).scalar_one()
    overdue_pm_items = db.execute(
        select(func.count())
        .select_from(MaintenanceSchedule)
        .where(
            MaintenanceSchedule.property_id == property_id,
            MaintenanceSchedule.is_active.is_(True),
            MaintenanceSchedule.next_due_on <= today,
        )
    ).scalar_one()
    overdue_inspection_followups = db.execute(
        select(func.count())
        .select_from(Inspection)
        .where(Inspection.property_id == property_id, Inspection.follow_up_due_on.is_not(None))
        .where(Inspection.follow_up_due_on <= today)
    ).scalar_one()

    deductions = (
        min(open_tickets * _OPEN_TICKET_PENALTY, _OPEN_TICKET_CAP)
        + min(repeat_failure_tickets * _REPEAT_FAILURE_PENALTY, _REPEAT_FAILURE_CAP)
        + min(sla_breached_tickets * _SLA_BREACH_PENALTY, _SLA_BREACH_CAP)
        + min(overdue_pm_items * _OVERDUE_PM_PENALTY, _OVERDUE_PM_CAP)
        + min(overdue_inspection_followups * _OVERDUE_FOLLOWUP_PENALTY, _OVERDUE_FOLLOWUP_CAP)
    )

    return PropertyHealthScoreOut(
        score=max(0, 100 - deductions),
        open_tickets=open_tickets,
        repeat_failure_tickets=repeat_failure_tickets,
        sla_breached_tickets=sla_breached_tickets,
        overdue_pm_items=overdue_pm_items,
        overdue_inspection_followups=overdue_inspection_followups,
    )
