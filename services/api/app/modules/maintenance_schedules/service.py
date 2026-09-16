import uuid
from datetime import UTC, date, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.maintenance import MaintenanceSchedule
from app.modules.maintenance_schedules.schemas import LogServiceRequest, MaintenanceScheduleCreate
from app.modules.properties.service import get_property_by_id


class MaintenanceScheduleNotFoundError(Exception):
    pass


class NotPropertyOwnerError(Exception):
    pass


def _require_owner_or_admin(db: Session, property_id: uuid.UUID, user_id: uuid.UUID, role: str) -> None:
    property_ = get_property_by_id(db, property_id)
    if role != "admin" and property_.owner_id != user_id:
        raise NotPropertyOwnerError


def _compute_next_due(base: date, frequency_days: int) -> date:
    return base + timedelta(days=frequency_days)


def create_schedule(
    db: Session, user_id: uuid.UUID, role: str, data: MaintenanceScheduleCreate
) -> MaintenanceSchedule:
    _require_owner_or_admin(db, data.property_id, user_id, role)
    base = data.last_serviced_on or datetime.now(UTC).date()
    schedule = MaintenanceSchedule(
        property_id=data.property_id,
        category=data.category,
        frequency_days=data.frequency_days,
        last_serviced_on=data.last_serviced_on,
        next_due_on=_compute_next_due(base, data.frequency_days),
        warranty_expires_on=data.warranty_expires_on,
        notes=data.notes,
        asset_id=data.asset_id,
    )
    db.add(schedule)
    db.commit()
    db.refresh(schedule)
    return schedule


def list_schedules(db: Session, property_id: uuid.UUID, due_only: bool) -> list[MaintenanceSchedule]:
    stmt = select(MaintenanceSchedule).where(MaintenanceSchedule.property_id == property_id)
    if due_only:
        stmt = stmt.where(MaintenanceSchedule.next_due_on <= datetime.now(UTC).date())
    return list(db.execute(stmt.order_by(MaintenanceSchedule.next_due_on)).scalars())


def get_schedule(db: Session, schedule_id: uuid.UUID) -> MaintenanceSchedule:
    schedule = db.get(MaintenanceSchedule, schedule_id)
    if schedule is None:
        raise MaintenanceScheduleNotFoundError
    return schedule


def log_service(
    db: Session, schedule_id: uuid.UUID, user_id: uuid.UUID, role: str, data: LogServiceRequest
) -> MaintenanceSchedule:
    schedule = get_schedule(db, schedule_id)
    _require_owner_or_admin(db, schedule.property_id, user_id, role)
    schedule.last_serviced_on = data.serviced_on
    schedule.next_due_on = _compute_next_due(data.serviced_on, schedule.frequency_days)
    if data.notes:
        schedule.notes = data.notes
    db.commit()
    db.refresh(schedule)
    return schedule
