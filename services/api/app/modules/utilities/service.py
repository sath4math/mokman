import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.utility import UtilityBill, UtilityConnection
from app.modules.properties.service import get_property_by_id
from app.modules.utilities.schemas import UtilityBillCreate, UtilityConnectionCreate


class UtilityConnectionNotFoundError(Exception):
    pass


class UtilityBillNotFoundError(Exception):
    pass


class NotPropertyOwnerError(Exception):
    pass


def _require_owner_or_admin(db: Session, property_id: uuid.UUID, user_id: uuid.UUID, role: str) -> None:
    property_ = get_property_by_id(db, property_id)
    if role != "admin" and property_.owner_id != user_id:
        raise NotPropertyOwnerError


def create_connection(
    db: Session, user_id: uuid.UUID, role: str, data: UtilityConnectionCreate
) -> UtilityConnection:
    _require_owner_or_admin(db, data.property_id, user_id, role)
    connection = UtilityConnection(**data.model_dump())
    db.add(connection)
    db.commit()
    db.refresh(connection)
    return connection


def list_connections(db: Session, property_id: uuid.UUID) -> list[UtilityConnection]:
    return list(
        db.execute(select(UtilityConnection).where(UtilityConnection.property_id == property_id)).scalars()
    )


def get_connection(db: Session, connection_id: uuid.UUID) -> UtilityConnection:
    connection = db.get(UtilityConnection, connection_id)
    if connection is None:
        raise UtilityConnectionNotFoundError
    return connection


def create_bill(
    db: Session, connection_id: uuid.UUID, user_id: uuid.UUID, role: str, data: UtilityBillCreate
) -> UtilityBill:
    connection = get_connection(db, connection_id)
    _require_owner_or_admin(db, connection.property_id, user_id, role)
    bill = UtilityBill(connection_id=connection_id, **data.model_dump())
    db.add(bill)
    db.commit()
    db.refresh(bill)
    return bill


def list_bills(db: Session, connection_id: uuid.UUID) -> list[UtilityBill]:
    return list(
        db.execute(
            select(UtilityBill).where(UtilityBill.connection_id == connection_id).order_by(UtilityBill.due_date.desc())
        ).scalars()
    )


def get_bill(db: Session, bill_id: uuid.UUID) -> UtilityBill:
    bill = db.get(UtilityBill, bill_id)
    if bill is None:
        raise UtilityBillNotFoundError
    return bill


def mark_bill_paid(db: Session, bill_id: uuid.UUID, user_id: uuid.UUID, role: str) -> UtilityBill:
    bill = get_bill(db, bill_id)
    connection = get_connection(db, bill.connection_id)
    _require_owner_or_admin(db, connection.property_id, user_id, role)
    bill.paid_at = datetime.now(UTC)
    bill.paid_by = user_id
    db.commit()
    db.refresh(bill)
    return bill
