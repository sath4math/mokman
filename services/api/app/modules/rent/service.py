import calendar
import uuid
from datetime import UTC, date, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.lease import Lease, LeaseStatus
from app.models.ledger import LedgerEntry, LedgerEntryType
from app.models.rent import InvoiceStatus, RentInvoice
from app.modules.finance.service import record_ledger_entry
from app.modules.rent.schemas import PaymentCreate

# Flat platform fee on collected rent. Becomes configurable per-plan
# pricing in a later phase; a single constant is proportionate for now.
MOKMAN_FEE_PERCENTAGE = 8.0


class InvoiceNotFoundError(Exception):
    pass


def _add_months(d: date, months: int) -> date:
    month_index = d.month - 1 + months
    year = d.year + month_index // 12
    month = month_index % 12 + 1
    day = min(d.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def _period_index_for(start_date: date, today: date) -> int:
    if today < start_date:
        return 0
    index = 0
    while _add_months(start_date, index + 1) <= today:
        index += 1
    return index


def _amount_for_period(lease: Lease, period_index: int) -> float:
    if not lease.annual_escalation_percentage:
        return lease.monthly_rent
    years_elapsed = period_index // 12
    return lease.monthly_rent * (1 + lease.annual_escalation_percentage / 100) ** years_elapsed


def ensure_current_invoice(db: Session, lease: Lease) -> RentInvoice | None:
    """Lazily creates the invoice for the billing period containing today,
    if the lease is active and it doesn't exist yet. No scheduler needed —
    called on every read path instead."""
    if lease.status != LeaseStatus.ACTIVE:
        return None

    today = datetime.now(UTC).date()
    index = _period_index_for(lease.start_date, today)
    period_start = _add_months(lease.start_date, index)
    if period_start > lease.end_date:
        return None
    period_end = min(_add_months(lease.start_date, index + 1) - timedelta(days=1), lease.end_date)

    existing = db.execute(
        select(RentInvoice).where(RentInvoice.lease_id == lease.id, RentInvoice.period_start == period_start)
    ).scalar_one_or_none()
    if existing is not None:
        return existing

    invoice = RentInvoice(
        lease_id=lease.id,
        property_id=lease.property_id,
        period_start=period_start,
        period_end=period_end,
        due_date=period_start,
        amount_due=_amount_for_period(lease, index),
        status=InvoiceStatus.PENDING,
    )
    db.add(invoice)
    db.commit()
    db.refresh(invoice)
    return invoice


def recompute_invoice_status(db: Session, invoice: RentInvoice) -> RentInvoice:
    if invoice.status == InvoiceStatus.CANCELLED:
        return invoice

    total_paid = db.execute(
        select(func.coalesce(func.sum(LedgerEntry.amount), 0.0)).where(
            LedgerEntry.invoice_id == invoice.id, LedgerEntry.entry_type == LedgerEntryType.RENT_PAYMENT
        )
    ).scalar_one()

    if total_paid >= invoice.amount_due:
        new_status = InvoiceStatus.PAID
    elif total_paid > 0:
        new_status = InvoiceStatus.PARTIALLY_PAID
    elif datetime.now(UTC).date() > invoice.due_date:
        new_status = InvoiceStatus.OVERDUE
    else:
        new_status = InvoiceStatus.PENDING

    if new_status != invoice.status:
        invoice.status = new_status
        db.commit()
        db.refresh(invoice)
    return invoice


def get_invoice(db: Session, invoice_id: uuid.UUID) -> RentInvoice:
    invoice = db.get(RentInvoice, invoice_id)
    if invoice is None:
        raise InvoiceNotFoundError
    return invoice


def list_invoices_for_lease(db: Session, lease: Lease) -> list[RentInvoice]:
    ensure_current_invoice(db, lease)
    invoices = list(
        db.execute(
            select(RentInvoice).where(RentInvoice.lease_id == lease.id).order_by(RentInvoice.period_start)
        ).scalars()
    )
    return [recompute_invoice_status(db, invoice) for invoice in invoices]


def record_payment(db: Session, invoice: RentInvoice, data: PaymentCreate, user_id: uuid.UUID) -> RentInvoice:
    record_ledger_entry(
        db,
        property_id=invoice.property_id,
        entry_type=LedgerEntryType.RENT_PAYMENT,
        amount=data.amount,
        recorded_by=user_id,
        lease_id=invoice.lease_id,
        invoice_id=invoice.id,
        method=data.method,
        reference_note=data.reference_note,
    )
    fee = round(data.amount * MOKMAN_FEE_PERCENTAGE / 100, 2)
    record_ledger_entry(
        db,
        property_id=invoice.property_id,
        entry_type=LedgerEntryType.MOKMAN_FEE,
        amount=fee,
        recorded_by=user_id,
        lease_id=invoice.lease_id,
        invoice_id=invoice.id,
    )
    return recompute_invoice_status(db, invoice)
