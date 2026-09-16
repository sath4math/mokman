import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.modules.auth.dependencies import CurrentUser, get_current_user
from app.modules.properties.service import PropertyNotFoundError
from app.modules.sales.schemas import CompleteSaleRequest, SaleCreate, SaleOut, SaleUpdate
from app.modules.sales.service import (
    NotPropertyOwnerError,
    SaleNotFoundError,
    complete_sale,
    create_sale,
    list_sales,
    update_sale,
)

router = APIRouter(prefix="/sales", tags=["sales"])


def _require_owner_or_admin_role(current: CurrentUser) -> None:
    if current.role not in ("owner", "admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Owner or admin role required")


@router.post("", response_model=SaleOut, status_code=status.HTTP_201_CREATED)
def create_sale_route(
    data: SaleCreate,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SaleOut:
    _require_owner_or_admin_role(current)
    try:
        sale = create_sale(db, current.user.id, current.role, data)
    except PropertyNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found") from None
    except NotPropertyOwnerError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not the owner of this property") from None
    return SaleOut.model_validate(sale)


@router.get("", response_model=list[SaleOut])
def list_sales_route(
    property_id: uuid.UUID,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[SaleOut]:
    _require_owner_or_admin_role(current)
    return [SaleOut.model_validate(s) for s in list_sales(db, property_id)]


@router.patch("/{sale_id}", response_model=SaleOut)
def update_sale_route(
    sale_id: uuid.UUID,
    data: SaleUpdate,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SaleOut:
    _require_owner_or_admin_role(current)
    try:
        sale = update_sale(db, sale_id, current.user.id, current.role, data)
    except SaleNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sale not found") from None
    except PropertyNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found") from None
    except NotPropertyOwnerError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not the owner of this property") from None
    return SaleOut.model_validate(sale)


@router.post("/{sale_id}/complete", response_model=SaleOut)
def complete_sale_route(
    sale_id: uuid.UUID,
    data: CompleteSaleRequest,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SaleOut:
    _require_owner_or_admin_role(current)
    try:
        sale = complete_sale(db, sale_id, current.user.id, current.role, data.sale_price, data.settlement_date)
    except SaleNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sale not found") from None
    except PropertyNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found") from None
    except NotPropertyOwnerError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not the owner of this property") from None
    return SaleOut.model_validate(sale)
