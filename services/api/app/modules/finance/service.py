import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.ledger import LedgerEntry, LedgerEntryType
from app.models.property import Property
from app.modules.finance.schemas import LedgerEntryOut, StatementOut


def record_ledger_entry(
    db: Session,
    *,
    property_id: uuid.UUID,
    entry_type: LedgerEntryType,
    amount: float,
    recorded_by: uuid.UUID,
    lease_id: uuid.UUID | None = None,
    invoice_id: uuid.UUID | None = None,
    expense_id: uuid.UUID | None = None,
    inspection_id: uuid.UUID | None = None,
    method: str | None = None,
    reference_note: str | None = None,
) -> LedgerEntry:
    entry = LedgerEntry(
        property_id=property_id,
        lease_id=lease_id,
        invoice_id=invoice_id,
        expense_id=expense_id,
        inspection_id=inspection_id,
        entry_type=entry_type,
        amount=amount,
        method=method,
        reference_note=reference_note,
        recorded_by=recorded_by,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def _month_bounds(year: int, month: int) -> tuple[datetime, datetime]:
    start = datetime(year, month, 1, tzinfo=UTC)
    end_year, end_month = (year + 1, 1) if month == 12 else (year, month + 1)
    end = datetime(end_year, end_month, 1, tzinfo=UTC)
    return start, end


def _summarize(entries: list[LedgerEntry], year: int, month: int) -> StatementOut:
    rent_collected = sum(e.amount for e in entries if e.entry_type == LedgerEntryType.RENT_PAYMENT)
    expenses = sum(e.amount for e in entries if e.entry_type == LedgerEntryType.EXPENSE)
    mokman_fee = sum(e.amount for e in entries if e.entry_type == LedgerEntryType.MOKMAN_FEE)
    return StatementOut(
        year=year,
        month=month,
        rent_collected=rent_collected,
        expenses=expenses,
        mokman_fee=mokman_fee,
        net_payable=rent_collected - expenses - mokman_fee,
        entries=[LedgerEntryOut.model_validate(e) for e in entries],
    )


def get_property_statement(db: Session, property_id: uuid.UUID, year: int, month: int) -> StatementOut:
    start, end = _month_bounds(year, month)
    entries = list(
        db.execute(
            select(LedgerEntry)
            .where(LedgerEntry.property_id == property_id)
            .where(LedgerEntry.occurred_at >= start)
            .where(LedgerEntry.occurred_at < end)
            .where(
                LedgerEntry.entry_type.in_(
                    [LedgerEntryType.RENT_PAYMENT, LedgerEntryType.EXPENSE, LedgerEntryType.MOKMAN_FEE]
                )
            )
            .order_by(LedgerEntry.occurred_at)
        ).scalars()
    )
    return _summarize(entries, year, month)


def get_owner_statement(db: Session, owner_id: uuid.UUID, year: int, month: int) -> StatementOut:
    start, end = _month_bounds(year, month)
    entries = list(
        db.execute(
            select(LedgerEntry)
            .join(Property, LedgerEntry.property_id == Property.id)
            .where(Property.owner_id == owner_id)
            .where(LedgerEntry.occurred_at >= start)
            .where(LedgerEntry.occurred_at < end)
            .where(
                LedgerEntry.entry_type.in_(
                    [LedgerEntryType.RENT_PAYMENT, LedgerEntryType.EXPENSE, LedgerEntryType.MOKMAN_FEE]
                )
            )
            .order_by(LedgerEntry.occurred_at)
        ).scalars()
    )
    return _summarize(entries, year, month)


def default_year_month() -> tuple[int, int]:
    today = datetime.now(UTC).date()
    return today.year, today.month
