import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.modules.auth.dependencies import CurrentUser, get_current_user
from app.modules.properties.service import PropertyNotFoundError
from app.modules.utilities.schemas import (
    UtilityBillCreate,
    UtilityBillOut,
    UtilityConnectionCreate,
    UtilityConnectionOut,
)
from app.modules.utilities.service import (
    NotPropertyOwnerError,
    UtilityBillNotFoundError,
    UtilityConnectionNotFoundError,
    create_bill,
    create_connection,
    list_bills,
    list_connections,
    mark_bill_paid,
)

router = APIRouter(prefix="/utilities", tags=["utilities"])


def _require_owner_or_admin_role(current: CurrentUser) -> None:
    if current.role not in ("owner", "admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Owner or admin role required")


@router.post("/connections", response_model=UtilityConnectionOut, status_code=status.HTTP_201_CREATED)
def create_connection_route(
    data: UtilityConnectionCreate,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UtilityConnectionOut:
    _require_owner_or_admin_role(current)
    try:
        connection = create_connection(db, current.user.id, current.role, data)
    except PropertyNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found") from None
    except NotPropertyOwnerError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not the owner of this property") from None
    return UtilityConnectionOut.model_validate(connection)


@router.get("/connections", response_model=list[UtilityConnectionOut])
def list_connections_route(
    property_id: uuid.UUID,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[UtilityConnectionOut]:
    _require_owner_or_admin_role(current)
    return [UtilityConnectionOut.model_validate(c) for c in list_connections(db, property_id)]


@router.post(
    "/connections/{connection_id}/bills", response_model=UtilityBillOut, status_code=status.HTTP_201_CREATED
)
def create_bill_route(
    connection_id: uuid.UUID,
    data: UtilityBillCreate,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UtilityBillOut:
    _require_owner_or_admin_role(current)
    try:
        bill = create_bill(db, connection_id, current.user.id, current.role, data)
    except UtilityConnectionNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Connection not found") from None
    except PropertyNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found") from None
    except NotPropertyOwnerError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not the owner of this property") from None
    return UtilityBillOut.model_validate(bill)


@router.get("/connections/{connection_id}/bills", response_model=list[UtilityBillOut])
def list_bills_route(
    connection_id: uuid.UUID,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[UtilityBillOut]:
    _require_owner_or_admin_role(current)
    return [UtilityBillOut.model_validate(b) for b in list_bills(db, connection_id)]


@router.post("/bills/{bill_id}/mark-paid", response_model=UtilityBillOut)
def mark_paid_route(
    bill_id: uuid.UUID,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UtilityBillOut:
    _require_owner_or_admin_role(current)
    try:
        bill = mark_bill_paid(db, bill_id, current.user.id, current.role)
    except UtilityBillNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bill not found") from None
    except UtilityConnectionNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Connection not found") from None
    except PropertyNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found") from None
    except NotPropertyOwnerError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not the owner of this property") from None
    return UtilityBillOut.model_validate(bill)
