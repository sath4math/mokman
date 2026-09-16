import uuid
from datetime import UTC, date, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.property import PropertyStatus
from app.models.sale import PropertySale, SaleStatus
from app.modules.properties.service import get_property_by_id
from app.modules.sales.schemas import SaleCreate, SaleUpdate


class SaleNotFoundError(Exception):
    pass


class NotPropertyOwnerError(Exception):
    pass


def _require_owner_or_admin(db: Session, property_id: uuid.UUID, user_id: uuid.UUID, role: str) -> None:
    property_ = get_property_by_id(db, property_id)
    if role != "admin" and property_.owner_id != user_id:
        raise NotPropertyOwnerError


def create_sale(db: Session, user_id: uuid.UUID, role: str, data: SaleCreate) -> PropertySale:
    _require_owner_or_admin(db, data.property_id, user_id, role)
    sale = PropertySale(**data.model_dump())
    db.add(sale)
    db.commit()
    db.refresh(sale)
    return sale


def list_sales(db: Session, property_id: uuid.UUID) -> list[PropertySale]:
    return list(db.execute(select(PropertySale).where(PropertySale.property_id == property_id)).scalars())


def get_sale(db: Session, sale_id: uuid.UUID) -> PropertySale:
    sale = db.get(PropertySale, sale_id)
    if sale is None:
        raise SaleNotFoundError
    return sale


def update_sale(db: Session, sale_id: uuid.UUID, user_id: uuid.UUID, role: str, data: SaleUpdate) -> PropertySale:
    sale = get_sale(db, sale_id)
    _require_owner_or_admin(db, sale.property_id, user_id, role)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(sale, field, value)
    db.commit()
    db.refresh(sale)
    return sale


def complete_sale(
    db: Session, sale_id: uuid.UUID, user_id: uuid.UUID, role: str, sale_price: float, settlement_date: date | None
) -> PropertySale:
    """Completes the sale and archives the property via the existing
    PropertyStatus.INACTIVE value (Phase 8d) -- reusing an enum value
    that's existed since Phase 1 rather than adding a new one. Deliberately
    ledger-isolated, unlike 8b's renovation-payment flow: a one-off
    capital sale isn't a recurring operational cost."""
    sale = get_sale(db, sale_id)
    _require_owner_or_admin(db, sale.property_id, user_id, role)

    sale.status = SaleStatus.COMPLETED
    sale.sale_price = sale_price
    sale.settlement_date = settlement_date or datetime.now(UTC).date()

    property_ = get_property_by_id(db, sale.property_id)
    property_.status = PropertyStatus.INACTIVE

    db.commit()
    db.refresh(sale)
    return sale
