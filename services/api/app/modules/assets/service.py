import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.asset import Asset
from app.modules.assets.schemas import AssetCreate, AssetUpdate
from app.modules.properties.service import get_property_by_id


class AssetNotFoundError(Exception):
    pass


class NotPropertyOwnerError(Exception):
    pass


def _require_owner_or_admin(db: Session, property_id: uuid.UUID, user_id: uuid.UUID, role: str) -> None:
    property_ = get_property_by_id(db, property_id)
    if role != "admin" and property_.owner_id != user_id:
        raise NotPropertyOwnerError


def create_asset(db: Session, user_id: uuid.UUID, role: str, data: AssetCreate) -> Asset:
    _require_owner_or_admin(db, data.property_id, user_id, role)
    asset = Asset(**data.model_dump())
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return asset


def list_assets(db: Session, property_id: uuid.UUID) -> list[Asset]:
    return list(db.execute(select(Asset).where(Asset.property_id == property_id)).scalars())


def get_asset(db: Session, asset_id: uuid.UUID) -> Asset:
    asset = db.get(Asset, asset_id)
    if asset is None:
        raise AssetNotFoundError
    return asset


def update_asset(db: Session, asset_id: uuid.UUID, user_id: uuid.UUID, role: str, data: AssetUpdate) -> Asset:
    asset = get_asset(db, asset_id)
    _require_owner_or_admin(db, asset.property_id, user_id, role)
    updates = data.model_dump(exclude_unset=True)
    if "property_id" in updates:
        # A "transfer" is just re-pointing property_id -- re-validate
        # against the destination property too.
        _require_owner_or_admin(db, updates["property_id"], user_id, role)
    for field, value in updates.items():
        setattr(asset, field, value)
    db.commit()
    db.refresh(asset)
    return asset


def dispose_asset(db: Session, asset_id: uuid.UUID, user_id: uuid.UUID, role: str, reason: str) -> Asset:
    asset = get_asset(db, asset_id)
    _require_owner_or_admin(db, asset.property_id, user_id, role)
    asset.is_active = False
    asset.disposed_at = datetime.now(UTC)
    asset.disposed_reason = reason
    db.commit()
    db.refresh(asset)
    return asset


def replace_asset(
    db: Session, asset_id: uuid.UUID, user_id: uuid.UUID, role: str, new_asset_data: AssetCreate
) -> Asset:
    """Creates the replacement asset and retires the old one, linked
    together -- composes create + dispose into the doc's single
    "replacement" lifecycle action."""
    old_asset = get_asset(db, asset_id)
    _require_owner_or_admin(db, old_asset.property_id, user_id, role)

    new_asset = create_asset(db, user_id, role, new_asset_data)

    old_asset.is_active = False
    old_asset.disposed_at = datetime.now(UTC)
    old_asset.disposed_reason = "replaced"
    old_asset.replaced_by_asset_id = new_asset.id
    db.commit()
    db.refresh(new_asset)
    return new_asset


def compute_current_value(asset: Asset) -> float | None:
    """Straight-line depreciation, computed on read -- same "computed,
    not stored" precedent as VendorOut.average_rating. None when either
    input needed for the calculation is missing."""
    if asset.purchase_cost is None or not asset.useful_life_years or asset.purchase_date is None:
        return None
    years_elapsed = (datetime.now(UTC).date() - asset.purchase_date).days / 365.25
    remaining_fraction = max(0.0, 1 - years_elapsed / asset.useful_life_years)
    return asset.purchase_cost * remaining_fraction
