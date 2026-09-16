import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.asset import Asset
from app.modules.assets.schemas import AssetCreate, AssetOut, AssetUpdate, DisposeRequest
from app.modules.assets.service import (
    AssetNotFoundError,
    NotPropertyOwnerError,
    compute_current_value,
    create_asset,
    dispose_asset,
    get_asset,
    list_assets,
    replace_asset,
    update_asset,
)
from app.modules.auth.dependencies import CurrentUser, get_current_user
from app.modules.properties.service import PropertyNotFoundError

router = APIRouter(prefix="/assets", tags=["assets"])


def _require_owner_or_admin_role(current: CurrentUser) -> None:
    if current.role not in ("owner", "admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Owner or admin role required")


def _to_asset_out(asset: Asset) -> AssetOut:
    return AssetOut(
        id=asset.id,
        property_id=asset.property_id,
        category=asset.category,
        name=asset.name,
        purchase_date=asset.purchase_date,
        purchase_cost=asset.purchase_cost,
        vendor_id=asset.vendor_id,
        warranty_expires_on=asset.warranty_expires_on,
        useful_life_years=asset.useful_life_years,
        is_active=asset.is_active,
        disposed_reason=asset.disposed_reason,
        replaced_by_asset_id=asset.replaced_by_asset_id,
        current_value=compute_current_value(asset),
    )


@router.post("", response_model=AssetOut, status_code=status.HTTP_201_CREATED)
def create(
    data: AssetCreate,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AssetOut:
    _require_owner_or_admin_role(current)
    try:
        asset = create_asset(db, current.user.id, current.role, data)
    except PropertyNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found") from None
    except NotPropertyOwnerError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not the owner of this property") from None
    return _to_asset_out(asset)


@router.get("", response_model=list[AssetOut])
def list_for_property(
    property_id: uuid.UUID,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[AssetOut]:
    _require_owner_or_admin_role(current)
    return [_to_asset_out(a) for a in list_assets(db, property_id)]


@router.patch("/{asset_id}", response_model=AssetOut)
def update(
    asset_id: uuid.UUID,
    data: AssetUpdate,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AssetOut:
    _require_owner_or_admin_role(current)
    try:
        asset = update_asset(db, asset_id, current.user.id, current.role, data)
    except AssetNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found") from None
    except PropertyNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found") from None
    except NotPropertyOwnerError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not the owner of this property") from None
    return _to_asset_out(asset)


@router.post("/{asset_id}/dispose", response_model=AssetOut)
def dispose(
    asset_id: uuid.UUID,
    data: DisposeRequest,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AssetOut:
    _require_owner_or_admin_role(current)
    try:
        asset = dispose_asset(db, asset_id, current.user.id, current.role, data.reason)
    except AssetNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found") from None
    except PropertyNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found") from None
    except NotPropertyOwnerError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not the owner of this property") from None
    return _to_asset_out(asset)


@router.post("/{asset_id}/replace", response_model=AssetOut, status_code=status.HTTP_201_CREATED)
def replace(
    asset_id: uuid.UUID,
    data: AssetCreate,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AssetOut:
    _require_owner_or_admin_role(current)
    try:
        new_asset = replace_asset(db, asset_id, current.user.id, current.role, data)
    except AssetNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found") from None
    except PropertyNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found") from None
    except NotPropertyOwnerError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not the owner of this property") from None
    return _to_asset_out(new_asset)


@router.get("/{asset_id}", response_model=AssetOut)
def read(
    asset_id: uuid.UUID,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AssetOut:
    _require_owner_or_admin_role(current)
    try:
        asset = get_asset(db, asset_id)
    except AssetNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found") from None
    return _to_asset_out(asset)
