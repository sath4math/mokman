import base64
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.common.llm import ask_claude
from app.common.storage import get_object_bytes
from app.models.compliance import ComplianceDue
from app.models.document import Document
from app.models.expense import Expense, ExpenseStatus
from app.models.lease import Lease
from app.models.maintenance import TicketStatus
from app.models.property import Property
from app.models.rent import InvoiceStatus, RentInvoice
from app.modules.documents.service import get_document, list_documents, verify_document_access
from app.modules.finance.service import default_year_month, get_owner_statement
from app.modules.inspections.service import get_inspection
from app.modules.inspections.service import require_party as require_inspection_party
from app.modules.maintenance.service import list_tickets
from app.modules.properties.service import (
    compute_investment_summary,
    get_owned_property,
    list_properties_for_owner,
)
from app.modules.rent.service import recompute_invoice_status

_OWNER_SYSTEM_PROMPT = (
    "You are the Mokman Owner Assistant. Answer the owner's question using "
    "ONLY the portfolio data given below. Never invent numbers or facts not "
    "present in it. If the data doesn't cover what's asked, say so plainly "
    "instead of guessing. Keep answers concise."
)

_DOCUMENT_SYSTEM_PROMPT = (
    "You are the Mokman Document Assistant. Answer the user's question "
    "using ONLY the attached document. If the document doesn't contain the "
    "answer, say so plainly instead of guessing. Keep answers concise."
)

_DAMAGE_ANALYSIS_PROMPT = (
    "You are the Mokman Inspection Assistant. Examine the attached inspection "
    "photos for damage, leaks, cracks, or cleanliness issues. Describe what "
    "you observe per photo. If both a before_photo and an after_photo are "
    "present, explicitly compare them. If nothing concerning is visible, say "
    "so plainly instead of inventing an issue. Keep the analysis concise."
)

_INVESTMENT_RECOMMENDATION_PROMPT = (
    "You are the Mokman Investment Assistant. Give a brief, advisory "
    "hold-or-consider-selling opinion for this property using ONLY the "
    "numbers given below. This is not financial advice -- say so, and "
    "recommend the owner consult a professional before acting. If "
    "purchase_price or current_market_value is missing, say the numbers "
    "aren't complete enough to opine rather than guessing. Keep it concise."
)

_LOOKAHEAD_DAYS = 30
_MAX_ANALYZED_PHOTOS = 6


class UnsupportedDocumentTypeError(Exception):
    pass


class NoInspectionPhotosError(Exception):
    pass


def gather_owner_context(db: Session, owner_id: uuid.UUID) -> str:
    """Plain queries against existing tables -- no new tables, same
    "reporting = queries" precedent as 5c/6c/6d."""
    today = datetime.now(UTC).date()
    lookahead = today + timedelta(days=_LOOKAHEAD_DAYS)

    properties = list_properties_for_owner(db, owner_id)

    year, month = default_year_month()
    statement = get_owner_statement(db, owner_id, year, month)

    open_tickets = [t for t in list_tickets(db, owner_id, "owner", None) if t.status != TicketStatus.CLOSED]

    invoices = db.execute(
        select(RentInvoice).join(Property, RentInvoice.property_id == Property.id).where(Property.owner_id == owner_id)
    ).scalars()
    overdue_invoices = [i for i in invoices if recompute_invoice_status(db, i).status == InvoiceStatus.OVERDUE]

    expiring_leases = list(
        db.execute(
            select(Lease)
            .join(Property, Lease.property_id == Property.id)
            .where(Property.owner_id == owner_id)
            .where(Lease.end_date >= today)
            .where(Lease.end_date <= lookahead)
        ).scalars()
    )

    pending_expenses = list(
        db.execute(
            select(Expense)
            .join(Property, Expense.property_id == Property.id)
            .where(Property.owner_id == owner_id)
            .where(Expense.status == ExpenseStatus.PENDING)
        ).scalars()
    )

    dues_soon = list(
        db.execute(
            select(ComplianceDue)
            .join(Property, ComplianceDue.property_id == Property.id)
            .where(Property.owner_id == owner_id)
            .where(ComplianceDue.paid_at.is_(None))
            .where(ComplianceDue.due_date <= lookahead)
        ).scalars()
    )

    lines = [
        f"Properties ({len(properties)}):",
        *[f"- {p.name} ({p.status.value}), {p.city}" for p in properties],
        "",
        f"This month's finances (property {statement.year}-{statement.month:02d}):",
        f"- Rent collected: {statement.rent_collected}",
        f"- Expenses: {statement.expenses}",
        f"- Mokman fee: {statement.mokman_fee}",
        f"- Net payable to owner: {statement.net_payable}",
        "",
        f"Open maintenance tickets: {len(open_tickets)}",
        *[f"- {t.category} ({t.status.value}), priority {t.priority.value}" for t in open_tickets],
        "",
        f"Overdue rent invoices: {len(overdue_invoices)}",
        *[f"- due {i.due_date}, amount {i.amount_due}" for i in overdue_invoices],
        "",
        f"Leases expiring within {_LOOKAHEAD_DAYS} days: {len(expiring_leases)}",
        *[f"- ends {lease.end_date}, rent {lease.monthly_rent}" for lease in expiring_leases],
        "",
        f"Expenses pending your approval: {len(pending_expenses)}",
        *[f"- {e.category}: {e.amount}" for e in pending_expenses],
        "",
        f"Society/government dues due within {_LOOKAHEAD_DAYS} days: {len(dues_soon)}",
        *[f"- {d.category.value}: {d.amount}, due {d.due_date}" for d in dues_soon],
    ]
    return "\n".join(lines)


def ask_owner_assistant(db: Session, owner_id: uuid.UUID, question: str) -> str:
    context = gather_owner_context(db, owner_id)
    return ask_claude(_OWNER_SYSTEM_PROMPT, f"Portfolio data:\n{context}\n\nQuestion: {question}")


def _document_content_block(document: Document) -> dict[str, Any] | None:
    """Builds a Claude image/PDF content block for a stored document, or
    None if its content-type isn't supported for multimodal Q&A."""
    file_bytes, content_type = get_object_bytes(document.s3_key)
    if content_type.startswith("image/"):
        block_type = "image"
    elif content_type == "application/pdf":
        block_type = "document"
    else:
        return None
    encoded = base64.b64encode(file_bytes).decode("ascii")
    return {"type": block_type, "source": {"type": "base64", "media_type": content_type, "data": encoded}}


def ask_about_document(db: Session, user_id: uuid.UUID, role: str, document_id: uuid.UUID, question: str) -> str:
    document = get_document(db, document_id)
    verify_document_access(db, user_id, role, document.owner_type, document.owner_id)

    block = _document_content_block(document)
    if block is None:
        raise UnsupportedDocumentTypeError

    content: list[dict[str, Any]] = [block, {"type": "text", "text": question}]
    return ask_claude(_DOCUMENT_SYSTEM_PROMPT, content)


def analyze_inspection_photos(db: Session, user_id: uuid.UUID, inspection_id: uuid.UUID) -> str:
    inspection = get_inspection(db, inspection_id)
    require_inspection_party(db, inspection, user_id)

    documents = list_documents(db, "inspection", inspection_id)
    content: list[dict[str, Any]] = []
    for document in documents[:_MAX_ANALYZED_PHOTOS]:
        block = _document_content_block(document)
        if block is not None:
            content.append(block)
            content.append({"type": "text", "text": f"(document_type: {document.document_type})"})

    if not content:
        raise NoInspectionPhotosError

    content.append({"type": "text", "text": "Analyze the photos above."})
    return ask_claude(_DAMAGE_ANALYSIS_PROMPT, content)


def recommend_sell_or_hold(db: Session, owner_id: uuid.UUID, property_id: uuid.UUID) -> str:
    get_owned_property(db, owner_id, property_id)
    summary = compute_investment_summary(db, property_id)

    lines = [
        f"Purchase price: {summary.purchase_price}",
        f"Current market value: {summary.current_market_value}",
        f"Appreciation: {summary.appreciation_percentage}%",
        f"Trailing 12-month rent income: {summary.trailing_12_month_rent_income}",
        f"Gross yield: {summary.gross_yield_percentage}%",
        f"All-time net income: {summary.total_net_income_all_time}",
        f"ROI: {summary.roi_percentage}%",
    ]
    return ask_claude(_INVESTMENT_RECOMMENDATION_PROMPT, "\n".join(lines))
