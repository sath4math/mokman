import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.vendor import Vendor
from app.modules.auth.dependencies import CurrentUser, get_current_user
from app.modules.vendors.schemas import (
    BlacklistRequest,
    VendorHistoryEventOut,
    VendorIn,
    VendorOut,
    VendorRateCardIn,
    VendorRateCardOut,
    VendorRatingIn,
    VendorRatingOut,
    VendorUpdate,
)
from app.modules.vendors.service import (
    InvalidRatingError,
    RateCardNotFoundError,
    TicketNotFoundError,
    VendorNotFoundError,
    blacklist_vendor,
    create_rate_card,
    create_rating,
    create_vendor,
    delete_rate_card,
    get_average_rating,
    list_rate_cards,
    list_ratings,
    list_vendor_history,
    list_vendors,
    reinstate_vendor,
    update_vendor,
)

router = APIRouter(prefix="/vendors", tags=["vendors"])


def _require_admin(current: CurrentUser) -> None:
    if current.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required")


def _to_vendor_out(db: Session, vendor: Vendor) -> VendorOut:
    return VendorOut(
        id=vendor.id,
        name=vendor.name,
        service_category=vendor.service_category,
        phone=vendor.phone,
        email=vendor.email,
        gst_number=vendor.gst_number,
        pan_number=vendor.pan_number,
        notes=vendor.notes,
        is_active=vendor.is_active,
        average_rating=get_average_rating(db, vendor.id),
    )


@router.post("", response_model=VendorOut, status_code=status.HTTP_201_CREATED)
def create(
    data: VendorIn,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> VendorOut:
    _require_admin(current)
    return _to_vendor_out(db, create_vendor(db, data))


@router.get("", response_model=list[VendorOut])
def list_for_viewer(
    active_only: bool = False,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[VendorOut]:
    if current.role not in ("owner", "admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Owner or admin role required")
    return [_to_vendor_out(db, v) for v in list_vendors(db, active_only)]


@router.patch("/{vendor_id}", response_model=VendorOut)
def update(
    vendor_id: uuid.UUID,
    data: VendorUpdate,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> VendorOut:
    _require_admin(current)
    try:
        vendor = update_vendor(db, vendor_id, data)
    except VendorNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vendor not found") from None
    return _to_vendor_out(db, vendor)


@router.post("/{vendor_id}/blacklist", response_model=VendorOut)
def blacklist(
    vendor_id: uuid.UUID,
    data: BlacklistRequest,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> VendorOut:
    _require_admin(current)
    try:
        vendor = blacklist_vendor(db, vendor_id, current.user.id, data.reason)
    except VendorNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vendor not found") from None
    return _to_vendor_out(db, vendor)


@router.post("/{vendor_id}/reinstate", response_model=VendorOut)
def reinstate(
    vendor_id: uuid.UUID,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> VendorOut:
    _require_admin(current)
    try:
        vendor = reinstate_vendor(db, vendor_id, current.user.id)
    except VendorNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vendor not found") from None
    return _to_vendor_out(db, vendor)


@router.get("/{vendor_id}/history", response_model=list[VendorHistoryEventOut])
def history(
    vendor_id: uuid.UUID,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[VendorHistoryEventOut]:
    _require_admin(current)
    return [VendorHistoryEventOut.model_validate(e) for e in list_vendor_history(db, vendor_id)]


@router.post("/{vendor_id}/rate-cards", response_model=VendorRateCardOut, status_code=status.HTTP_201_CREATED)
def add_rate_card(
    vendor_id: uuid.UUID,
    data: VendorRateCardIn,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> VendorRateCardOut:
    _require_admin(current)
    try:
        rate_card = create_rate_card(db, vendor_id, data)
    except VendorNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vendor not found") from None
    return VendorRateCardOut.model_validate(rate_card)


@router.get("/{vendor_id}/rate-cards", response_model=list[VendorRateCardOut])
def get_rate_cards(
    vendor_id: uuid.UUID,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[VendorRateCardOut]:
    if current.role not in ("owner", "admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Owner or admin role required")
    return [VendorRateCardOut.model_validate(r) for r in list_rate_cards(db, vendor_id)]


@router.delete("/{vendor_id}/rate-cards/{rate_card_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_rate_card(
    vendor_id: uuid.UUID,
    rate_card_id: uuid.UUID,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    _require_admin(current)
    try:
        delete_rate_card(db, vendor_id, rate_card_id)
    except RateCardNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rate card not found") from None


@router.post("/{vendor_id}/ratings", response_model=VendorRatingOut, status_code=status.HTTP_201_CREATED)
def add_rating(
    vendor_id: uuid.UUID,
    data: VendorRatingIn,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> VendorRatingOut:
    if current.role not in ("owner", "admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Owner or admin role required")
    try:
        rating = create_rating(db, vendor_id, current.user.id, data)
    except VendorNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vendor not found") from None
    except TicketNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found") from None
    except InvalidRatingError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ticket must be closed and assigned to this vendor to be rated",
        ) from None
    return VendorRatingOut.model_validate(rating)


@router.get("/{vendor_id}/ratings", response_model=list[VendorRatingOut])
def get_ratings(
    vendor_id: uuid.UUID,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[VendorRatingOut]:
    if current.role not in ("owner", "admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Owner or admin role required")
    return [VendorRatingOut.model_validate(r) for r in list_ratings(db, vendor_id)]
