import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.owner_profile import AuthorizedRepresentative, OwnerProfile
from app.modules.owner.schemas import AuthorizedRepresentativeIn, OwnerProfileIn


def get_profile(db: Session, user_id: uuid.UUID) -> OwnerProfile | None:
    return db.get(OwnerProfile, user_id)


def upsert_profile(db: Session, user_id: uuid.UUID, data: OwnerProfileIn) -> OwnerProfile:
    profile = db.get(OwnerProfile, user_id)
    if profile is None:
        profile = OwnerProfile(user_id=user_id, **data.model_dump())
        db.add(profile)
    else:
        for field, value in data.model_dump().items():
            setattr(profile, field, value)
    db.commit()
    db.refresh(profile)
    return profile


def list_representatives(db: Session, owner_id: uuid.UUID) -> list[AuthorizedRepresentative]:
    return list(
        db.execute(
            select(AuthorizedRepresentative).where(AuthorizedRepresentative.owner_id == owner_id)
        ).scalars()
    )


def add_representative(
    db: Session, owner_id: uuid.UUID, data: AuthorizedRepresentativeIn
) -> AuthorizedRepresentative:
    rep = AuthorizedRepresentative(owner_id=owner_id, **data.model_dump())
    db.add(rep)
    db.commit()
    db.refresh(rep)
    return rep


class RepresentativeNotFoundError(Exception):
    pass


def remove_representative(db: Session, owner_id: uuid.UUID, representative_id: uuid.UUID) -> None:
    rep = db.get(AuthorizedRepresentative, representative_id)
    if rep is None or rep.owner_id != owner_id:
        raise RepresentativeNotFoundError
    db.delete(rep)
    db.commit()
