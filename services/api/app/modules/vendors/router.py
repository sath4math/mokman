import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.modules.auth.dependencies import CurrentUser, get_current_user
from app.modules.vendors.schemas import VendorIn, VendorOut, VendorUpdate
from app.modules.vendors.service import (
    VendorNotFoundError,
    create_vendor,
    list_vendors,
    update_vendor,
)

router = APIRouter(prefix="/vendors", tags=["vendors"])


def _require_admin(current: CurrentUser) -> None:
    if current.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required")


@router.post("", response_model=VendorOut, status_code=status.HTTP_201_CREATED)
def create(
    data: VendorIn,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> VendorOut:
    _require_admin(current)
    return VendorOut.model_validate(create_vendor(db, data))


@router.get("", response_model=list[VendorOut])
def list_for_viewer(
    active_only: bool = False,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[VendorOut]:
    if current.role not in ("owner", "admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Owner or admin role required")
    return [VendorOut.model_validate(v) for v in list_vendors(db, active_only)]


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
    return VendorOut.model_validate(vendor)
