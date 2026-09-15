from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.modules.auth.dependencies import CurrentUser, get_current_user
from app.modules.tenant.schemas import TenantProfileIn, TenantProfileOut
from app.modules.tenant.service import get_profile, upsert_profile

router = APIRouter(prefix="/tenant", tags=["tenant"])


def _require_tenant(current: CurrentUser) -> None:
    if current.role != "tenant":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tenant role required")


@router.get("/profile", response_model=TenantProfileOut | None)
def read_profile(
    current: CurrentUser = Depends(get_current_user), db: Session = Depends(get_db)
) -> TenantProfileOut | None:
    _require_tenant(current)
    profile = get_profile(db, current.user.id)
    return TenantProfileOut.model_validate(profile) if profile else None


@router.put("/profile", response_model=TenantProfileOut)
def update_profile(
    data: TenantProfileIn,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TenantProfileOut:
    _require_tenant(current)
    profile = upsert_profile(db, current.user.id, data)
    return TenantProfileOut.model_validate(profile)
