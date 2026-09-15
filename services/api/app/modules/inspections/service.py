import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.inspection import Inspection
from app.models.lease import Lease
from app.models.property import Property
from app.modules.inspections.schemas import InspectionCreate, InspectionUpdate
from app.modules.properties.service import PropertyNotFoundError


class InspectionNotFoundError(Exception):
    pass


class NotPartyToInspectionError(Exception):
    pass


class InspectionAlreadySignedError(Exception):
    pass


def verify_property_access(db: Session, property_id: uuid.UUID, user_id: uuid.UUID) -> None:
    property_ = db.get(Property, property_id)
    if property_ is None:
        raise PropertyNotFoundError
    if property_.owner_id == user_id:
        return
    has_lease = db.execute(
        select(Lease.id).where(Lease.property_id == property_id, Lease.tenant_id == user_id)
    ).first()
    if has_lease is None:
        raise NotPartyToInspectionError


def role_for_inspection(db: Session, inspection: Inspection, user_id: uuid.UUID) -> str | None:
    property_ = db.get(Property, inspection.property_id)
    if property_ is not None and property_.owner_id == user_id:
        return "owner"
    has_lease = db.execute(
        select(Lease.id).where(Lease.property_id == inspection.property_id, Lease.tenant_id == user_id)
    ).first()
    if has_lease is not None:
        return "tenant"
    return None


def require_party(db: Session, inspection: Inspection, user_id: uuid.UUID) -> str:
    role = role_for_inspection(db, inspection, user_id)
    if role is None:
        raise NotPartyToInspectionError
    return role


def create_inspection(db: Session, user_id: uuid.UUID, data: InspectionCreate) -> Inspection:
    verify_property_access(db, data.property_id, user_id)

    inspection = Inspection(
        property_id=data.property_id,
        lease_id=data.lease_id,
        inspection_type=data.inspection_type,
        conducted_by=user_id,
        checklist=data.checklist,
        notes=data.notes,
        meter_readings=data.meter_readings,
    )
    db.add(inspection)
    db.commit()
    db.refresh(inspection)
    return inspection


def list_inspections(
    db: Session, property_id: uuid.UUID, lease_id: uuid.UUID | None
) -> list[Inspection]:
    stmt = select(Inspection).where(Inspection.property_id == property_id)
    if lease_id is not None:
        stmt = stmt.where(Inspection.lease_id == lease_id)
    return list(db.execute(stmt).scalars())


def get_inspection(db: Session, inspection_id: uuid.UUID) -> Inspection:
    inspection = db.get(Inspection, inspection_id)
    if inspection is None:
        raise InspectionNotFoundError
    return inspection


def update_inspection(
    db: Session, inspection_id: uuid.UUID, user_id: uuid.UUID, data: InspectionUpdate
) -> Inspection:
    inspection = get_inspection(db, inspection_id)
    require_party(db, inspection, user_id)
    if inspection.owner_signed_off_at and inspection.tenant_signed_off_at:
        raise InspectionAlreadySignedError

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(inspection, field, value)

    db.commit()
    db.refresh(inspection)
    return inspection


def sign_off_inspection(db: Session, inspection_id: uuid.UUID, user_id: uuid.UUID) -> Inspection:
    inspection = get_inspection(db, inspection_id)
    role = require_party(db, inspection, user_id)

    now = datetime.now(UTC)
    if role == "owner":
        inspection.owner_signed_off_at = now
    else:
        inspection.tenant_signed_off_at = now

    db.commit()
    db.refresh(inspection)
    return inspection
