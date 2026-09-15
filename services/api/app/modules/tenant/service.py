import uuid

from sqlalchemy.orm import Session

from app.models.tenant_profile import TenantProfile
from app.modules.tenant.schemas import TenantProfileIn


def get_profile(db: Session, user_id: uuid.UUID) -> TenantProfile | None:
    return db.get(TenantProfile, user_id)


def upsert_profile(db: Session, user_id: uuid.UUID, data: TenantProfileIn) -> TenantProfile:
    profile = db.get(TenantProfile, user_id)
    if profile is None:
        profile = TenantProfile(user_id=user_id, **data.model_dump())
        db.add(profile)
    else:
        for field, value in data.model_dump().items():
            setattr(profile, field, value)
    db.commit()
    db.refresh(profile)
    return profile
