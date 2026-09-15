import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.rent import RentInvoice
from app.modules.auth.dependencies import CurrentUser, get_current_user
from app.modules.leases.service import (
    LeaseNotFoundError,
    NotPartyToLeaseError,
    get_lease,
    require_party,
)
from app.modules.rent.schemas import PaymentCreate, RentInvoiceOut
from app.modules.rent.service import (
    InvoiceNotFoundError,
    get_invoice,
    list_invoices_for_lease,
    record_payment,
)

router = APIRouter(prefix="/rent", tags=["rent"])


def _require_invoice_access(db: Session, current: CurrentUser, invoice: RentInvoice) -> None:
    if current.role == "admin":
        return
    lease = get_lease(db, invoice.lease_id)
    require_party(db, lease, current.user.id)


@router.get("/invoices", response_model=list[RentInvoiceOut])
def list_invoices(
    lease_id: uuid.UUID,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[RentInvoiceOut]:
    try:
        lease = get_lease(db, lease_id)
        if current.role != "admin":
            require_party(db, lease, current.user.id)
    except LeaseNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lease not found") from None
    except NotPartyToLeaseError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a party to this lease") from None
    return [RentInvoiceOut.model_validate(invoice) for invoice in list_invoices_for_lease(db, lease)]


@router.get("/invoices/{invoice_id}", response_model=RentInvoiceOut)
def read_invoice(
    invoice_id: uuid.UUID,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RentInvoiceOut:
    try:
        invoice = get_invoice(db, invoice_id)
        _require_invoice_access(db, current, invoice)
    except InvoiceNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found") from None
    except LeaseNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lease not found") from None
    except NotPartyToLeaseError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a party to this lease") from None
    return RentInvoiceOut.model_validate(invoice)


@router.post("/invoices/{invoice_id}/payments", response_model=RentInvoiceOut)
def pay_invoice(
    invoice_id: uuid.UUID,
    data: PaymentCreate,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RentInvoiceOut:
    try:
        invoice = get_invoice(db, invoice_id)
        _require_invoice_access(db, current, invoice)
    except InvoiceNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found") from None
    except LeaseNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lease not found") from None
    except NotPartyToLeaseError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a party to this lease") from None
    return RentInvoiceOut.model_validate(record_payment(db, invoice, data, current.user.id))
