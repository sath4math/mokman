import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.property import Property
from app.modules.properties.schemas import PropertyCreate, PropertyUpdate


class PropertyNotFoundError(Exception):
    pass


def create_property(db: Session, owner_id: uuid.UUID, data: PropertyCreate) -> Property:
    property_ = Property(owner_id=owner_id, **data.model_dump())
    db.add(property_)
    db.commit()
    db.refresh(property_)
    return property_


def list_properties_for_owner(db: Session, owner_id: uuid.UUID) -> list[Property]:
    return list(db.execute(select(Property).where(Property.owner_id == owner_id)).scalars())


def list_all_properties(db: Session) -> list[Property]:
    return list(db.execute(select(Property)).scalars())


def get_owned_property(db: Session, owner_id: uuid.UUID, property_id: uuid.UUID) -> Property:
    property_ = db.get(Property, property_id)
    if property_ is None or property_.owner_id != owner_id:
        raise PropertyNotFoundError
    return property_


def get_property_by_id(db: Session, property_id: uuid.UUID) -> Property:
    property_ = db.get(Property, property_id)
    if property_ is None:
        raise PropertyNotFoundError
    return property_


def update_property(db: Session, owner_id: uuid.UUID, property_id: uuid.UUID, data: PropertyUpdate) -> Property:
    property_ = get_owned_property(db, owner_id, property_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(property_, field, value)
    db.commit()
    db.refresh(property_)
    return property_
