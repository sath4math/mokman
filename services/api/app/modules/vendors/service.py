import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.audit import AuditLog
from app.models.maintenance import MaintenanceTicket, TicketStatus
from app.models.vendor import Vendor, VendorRateCard, VendorRating
from app.modules.vendors.schemas import VendorIn, VendorRateCardIn, VendorRatingIn, VendorUpdate


class VendorNotFoundError(Exception):
    pass


class RateCardNotFoundError(Exception):
    pass


class TicketNotFoundError(Exception):
    pass


class InvalidRatingError(Exception):
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


def get_average_rating(db: Session, vendor_id: uuid.UUID) -> float | None:
    return db.execute(select(func.avg(VendorRating.score)).where(VendorRating.vendor_id == vendor_id)).scalar()


def blacklist_vendor(db: Session, vendor_id: uuid.UUID, actor_id: uuid.UUID, reason: str) -> Vendor:
    vendor = get_vendor(db, vendor_id)
    vendor.is_active = False
    db.add(
        AuditLog(
            actor_id=actor_id,
            action="vendor.blacklisted",
            entity_type="vendor",
            entity_id=vendor_id,
            after={"reason": reason},
        )
    )
    db.commit()
    db.refresh(vendor)
    return vendor


def reinstate_vendor(db: Session, vendor_id: uuid.UUID, actor_id: uuid.UUID) -> Vendor:
    vendor = get_vendor(db, vendor_id)
    vendor.is_active = True
    db.add(
        AuditLog(
            actor_id=actor_id,
            action="vendor.reinstated",
            entity_type="vendor",
            entity_id=vendor_id,
        )
    )
    db.commit()
    db.refresh(vendor)
    return vendor


def list_vendor_history(db: Session, vendor_id: uuid.UUID) -> list[AuditLog]:
    return list(
        db.execute(
            select(AuditLog)
            .where(AuditLog.entity_type == "vendor")
            .where(AuditLog.entity_id == vendor_id)
            .order_by(AuditLog.created_at.desc())
        ).scalars()
    )


def create_rate_card(db: Session, vendor_id: uuid.UUID, data: VendorRateCardIn) -> VendorRateCard:
    get_vendor(db, vendor_id)
    rate_card = VendorRateCard(vendor_id=vendor_id, **data.model_dump())
    db.add(rate_card)
    db.commit()
    db.refresh(rate_card)
    return rate_card


def list_rate_cards(db: Session, vendor_id: uuid.UUID) -> list[VendorRateCard]:
    return list(db.execute(select(VendorRateCard).where(VendorRateCard.vendor_id == vendor_id)).scalars())


def delete_rate_card(db: Session, vendor_id: uuid.UUID, rate_card_id: uuid.UUID) -> None:
    rate_card = db.get(VendorRateCard, rate_card_id)
    if rate_card is None or rate_card.vendor_id != vendor_id:
        raise RateCardNotFoundError
    db.delete(rate_card)
    db.commit()


def create_rating(db: Session, vendor_id: uuid.UUID, rated_by: uuid.UUID, data: VendorRatingIn) -> VendorRating:
    get_vendor(db, vendor_id)
    ticket = db.get(MaintenanceTicket, data.ticket_id)
    if ticket is None:
        raise TicketNotFoundError
    if ticket.assigned_vendor_id != vendor_id or ticket.status != TicketStatus.CLOSED:
        raise InvalidRatingError

    rating = VendorRating(vendor_id=vendor_id, rated_by=rated_by, **data.model_dump())
    db.add(rating)
    db.commit()
    db.refresh(rating)
    return rating


def list_ratings(db: Session, vendor_id: uuid.UUID) -> list[VendorRating]:
    return list(
        db.execute(
            select(VendorRating).where(VendorRating.vendor_id == vendor_id).order_by(VendorRating.created_at.desc())
        ).scalars()
    )
