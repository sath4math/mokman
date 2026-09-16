import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.vendor import Vendor
from app.modules.vendors.schemas import VendorIn, VendorUpdate


class VendorNotFoundError(Exception):
    pass


def create_vendor(db: Session, data: VendorIn) -> Vendor:
    vendor = Vendor(**data.model_dump())
    db.add(vendor)
    db.commit()
    db.refresh(vendor)
    return vendor


def list_vendors(db: Session, active_only: bool) -> list[Vendor]:
    stmt = select(Vendor)
    if active_only:
        stmt = stmt.where(Vendor.is_active.is_(True))
    return list(db.execute(stmt.order_by(Vendor.name)).scalars())


def get_vendor(db: Session, vendor_id: uuid.UUID) -> Vendor:
    vendor = db.get(Vendor, vendor_id)
    if vendor is None:
        raise VendorNotFoundError
    return vendor


def update_vendor(db: Session, vendor_id: uuid.UUID, data: VendorUpdate) -> Vendor:
    vendor = get_vendor(db, vendor_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(vendor, field, value)
    db.commit()
    db.refresh(vendor)
    return vendor
