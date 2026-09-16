import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.modules.auth.dependencies import CurrentUser, get_current_user
from app.modules.inspections.schemas import InspectionCreate, InspectionOut, InspectionUpdate
from app.modules.inspections.service import (
    DepositMismatchError,
    InspectionAlreadySignedError,
    InspectionNotFoundError,
    InspectionNotReadyForSettlementError,
    NotPartyToInspectionError,
    create_inspection,
    list_inspections,
    settle_deposit,
    sign_off_inspection,
    update_inspection,
    verify_property_access,
)
from app.modules.properties.service import PropertyNotFoundError

router = APIRouter(prefix="/inspections", tags=["inspections"])


@router.post("", response_model=InspectionOut, status_code=status.HTTP_201_CREATED)
def create(
    data: InspectionCreate,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> InspectionOut:
    try:
        inspection = create_inspection(db, current.user.id, data)
    except PropertyNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found") from None
    except NotPartyToInspectionError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not a party to this property"
        ) from None
    return InspectionOut.model_validate(inspection)


@router.get("", response_model=list[InspectionOut])
def list_for_property(
    property_id: uuid.UUID,
    lease_id: uuid.UUID | None = None,
    upcoming_only: bool = False,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[InspectionOut]:
    try:
        verify_property_access(db, property_id, current.user.id)
    except PropertyNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found") from None
    except NotPartyToInspectionError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not a party to this property"
        ) from None
    return [
        InspectionOut.model_validate(i) for i in list_inspections(db, property_id, lease_id, upcoming_only)
    ]


@router.patch("/{inspection_id}", response_model=InspectionOut)
def update(
    inspection_id: uuid.UUID,
    data: InspectionUpdate,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> InspectionOut:
    try:
        inspection = update_inspection(db, inspection_id, current.user.id, data)
    except InspectionNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inspection not found") from None
    except NotPartyToInspectionError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not a party to this inspection"
        ) from None
    except InspectionAlreadySignedError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Inspection already signed off by both parties"
        ) from None
    return InspectionOut.model_validate(inspection)


@router.post("/{inspection_id}/sign-off", response_model=InspectionOut)
def sign_off(
    inspection_id: uuid.UUID,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> InspectionOut:
    try:
        inspection = sign_off_inspection(db, inspection_id, current.user.id)
    except InspectionNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inspection not found") from None
    except NotPartyToInspectionError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not a party to this inspection"
        ) from None
    return InspectionOut.model_validate(inspection)


@router.post("/{inspection_id}/settle-deposit", response_model=InspectionOut)
def settle(
    inspection_id: uuid.UUID,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> InspectionOut:
    try:
        inspection = settle_deposit(db, inspection_id, current.user.id)
    except InspectionNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inspection not found") from None
    except NotPartyToInspectionError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not a party to this inspection"
        ) from None
    except InspectionNotReadyForSettlementError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Inspection is not a fully signed-off, unsettled move-out with deposit numbers set",
        ) from None
    except DepositMismatchError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Deposit deduction + refund must equal the original security deposit",
        ) from None
    return InspectionOut.model_validate(inspection)
