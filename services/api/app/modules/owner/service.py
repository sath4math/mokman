import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.audit import AuditLog
from app.models.document import Document
from app.models.owner_profile import AuthorizedRepresentative, KycStatus, OwnerProfile
from app.models.user import User
from app.modules.owner.schemas import AuthorizedRepresentativeIn, OwnerProfileIn


def get_profile(db: Session, user_id: uuid.UUID) -> OwnerProfile | None:
    return db.get(OwnerProfile, user_id)


class UserNotFoundError(Exception):
    pass


def get_profile_with_user(db: Session, user_id: uuid.UUID) -> tuple[OwnerProfile, User]:
    """For the admin on-behalf-of screen: always returns something to
    render, even before the owner has ever saved a profile -- a transient
    (unsaved) OwnerProfile gets the model's normal column defaults for
    free, so the admin sees the same starting values a fresh self-service
    save would."""
    user = db.get(User, user_id)
    if user is None:
        raise UserNotFoundError
    profile = get_profile(db, user_id) or OwnerProfile(user_id=user_id)
    return profile, user


def list_profiles(db: Session, kyc_status: KycStatus | None = None) -> list[tuple[OwnerProfile, User]]:
    stmt = select(OwnerProfile, User).join(User, User.id == OwnerProfile.user_id)
    if kyc_status is not None:
        stmt = stmt.where(OwnerProfile.kyc_status == kyc_status)
    return [(profile, user) for profile, user in db.execute(stmt).all()]


class ProfileNotFoundError(Exception):
    pass


class OwnerProfileAccessError(Exception):
    pass


def approve_kyc(db: Session, user_id: uuid.UUID, actor_id: uuid.UUID) -> OwnerProfile:
    profile = get_profile(db, user_id)
    if profile is None:
        raise ProfileNotFoundError
    profile.kyc_status = KycStatus.VERIFIED
    db.add(
        AuditLog(
            actor_id=actor_id,
            action="owner_profile.kyc_verified",
            entity_type="owner_profile",
            entity_id=user_id,
        )
    )
    db.commit()
    db.refresh(profile)
    return profile


def reject_kyc(db: Session, user_id: uuid.UUID, actor_id: uuid.UUID, reason: str) -> OwnerProfile:
    profile = get_profile(db, user_id)
    if profile is None:
        raise ProfileNotFoundError
    profile.kyc_status = KycStatus.REJECTED
    db.add(
        AuditLog(
            actor_id=actor_id,
            action="owner_profile.kyc_rejected",
            entity_type="owner_profile",
            entity_id=user_id,
            after={"reason": reason},
        )
    )
    db.commit()
    db.refresh(profile)
    return profile


class MissingKycDocumentError(Exception):
    pass


def upsert_profile(db: Session, user_id: uuid.UUID, data: OwnerProfileIn) -> OwnerProfile:
    has_document = db.execute(
        select(Document.id).where(Document.owner_type == "owner_profile", Document.owner_id == user_id)
    ).first()
    if has_document is None:
        raise MissingKycDocumentError

    profile = db.get(OwnerProfile, user_id)
    if profile is None:
        profile = OwnerProfile(user_id=user_id, **data.model_dump())
        db.add(profile)
    else:
        for field, value in data.model_dump().items():
            setattr(profile, field, value)
        # A rejected owner who fixes and resaves their details is
        # resubmitting -- put them back in the admin's pending queue
        # rather than leaving kyc_status stuck on "rejected" forever.
        if profile.kyc_status == KycStatus.REJECTED:
            profile.kyc_status = KycStatus.PENDING
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
