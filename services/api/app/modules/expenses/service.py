import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.expense import Expense, ExpenseStatus
from app.models.ledger import LedgerEntryType
from app.models.property import Property
from app.models.vendor import Vendor
from app.modules.expenses.schemas import ExpenseCreate
from app.modules.finance.service import record_ledger_entry
from app.modules.properties.service import PropertyNotFoundError, get_property_by_id


class ExpenseNotFoundError(Exception):
    pass


class NotPropertyOwnerError(Exception):
    pass


def _vendor_reference_note(db: Session, vendor_id: uuid.UUID | None) -> str | None:
    if vendor_id is None:
        return None
    vendor = db.get(Vendor, vendor_id)
    return f"vendor:{vendor.name}" if vendor else None


def create_expense(db: Session, user_id: uuid.UUID, role: str, data: ExpenseCreate) -> Expense:
    property_ = get_property_by_id(db, data.property_id)

    is_owner_of_property = role == "owner" and property_.owner_id == user_id
    if not is_owner_of_property and role != "admin":
        raise NotPropertyOwnerError

    expense = Expense(
        property_id=data.property_id,
        category=data.category,
        amount=data.amount,
        description=data.description,
        submitted_by=user_id,
        vendor_id=data.vendor_id,
        ticket_id=data.ticket_id,
        status=ExpenseStatus.APPROVED if is_owner_of_property else ExpenseStatus.PENDING,
    )
    if is_owner_of_property:
        expense.approved_by = user_id
        expense.approved_at = datetime.now(UTC)

    db.add(expense)
    db.commit()
    db.refresh(expense)

    if is_owner_of_property:
        record_ledger_entry(
            db,
            property_id=expense.property_id,
            entry_type=LedgerEntryType.EXPENSE,
            amount=expense.amount,
            recorded_by=user_id,
            expense_id=expense.id,
            reference_note=_vendor_reference_note(db, expense.vendor_id),
        )
    return expense


def list_expenses(db: Session, property_id: uuid.UUID | None) -> list[Expense]:
    stmt = select(Expense)
    if property_id is not None:
        stmt = stmt.where(Expense.property_id == property_id)
    return list(db.execute(stmt.order_by(Expense.created_at.desc())).scalars())


def get_expense(db: Session, expense_id: uuid.UUID) -> Expense:
    expense = db.get(Expense, expense_id)
    if expense is None:
        raise ExpenseNotFoundError
    return expense


def _require_property_owner(db: Session, expense: Expense, user_id: uuid.UUID) -> Property:
    property_ = db.get(Property, expense.property_id)
    if property_ is None:
        raise PropertyNotFoundError
    if property_.owner_id != user_id:
        raise NotPropertyOwnerError
    return property_


def approve_expense(db: Session, expense_id: uuid.UUID, user_id: uuid.UUID) -> Expense:
    expense = get_expense(db, expense_id)
    _require_property_owner(db, expense, user_id)

    if expense.status != ExpenseStatus.APPROVED:
        expense.status = ExpenseStatus.APPROVED
        expense.approved_by = user_id
        expense.approved_at = datetime.now(UTC)
        db.commit()
        db.refresh(expense)
        record_ledger_entry(
            db,
            property_id=expense.property_id,
            entry_type=LedgerEntryType.EXPENSE,
            amount=expense.amount,
            recorded_by=user_id,
            expense_id=expense.id,
            reference_note=_vendor_reference_note(db, expense.vendor_id),
        )
    return expense


def reject_expense(db: Session, expense_id: uuid.UUID, user_id: uuid.UUID) -> Expense:
    expense = get_expense(db, expense_id)
    _require_property_owner(db, expense, user_id)

    expense.status = ExpenseStatus.REJECTED
    expense.approved_by = user_id
    expense.approved_at = datetime.now(UTC)
    db.commit()
    db.refresh(expense)
    return expense
