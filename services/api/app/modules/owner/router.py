import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.modules.auth.dependencies import CurrentUser, get_current_user
from app.modules.owner.schemas import (
    AuthorizedRepresentativeIn,
    AuthorizedRepresentativeOut,
    OwnerProfileIn,
    OwnerProfileOut,
)
from app.modules.owner.service import (
    RepresentativeNotFoundError,
    add_representative,
    get_profile,
    list_representatives,
    remove_representative,
    upsert_profile,
)

router = APIRouter(prefix="/owner", tags=["owner"])


def _require_owner(current: CurrentUser) -> None:
    if current.role != "owner":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Owner role required")


@router.get("/profile", response_model=OwnerProfileOut | None)
def read_profile(
    current: CurrentUser = Depends(get_current_user), db: Session = Depends(get_db)
) -> OwnerProfileOut | None:
    _require_owner(current)
    profile = get_profile(db, current.user.id)
    return OwnerProfileOut.model_validate(profile) if profile else None


@router.put("/profile", response_model=OwnerProfileOut)
def update_profile(
    data: OwnerProfileIn,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> OwnerProfileOut:
    _require_owner(current)
    profile = upsert_profile(db, current.user.id, data)
    return OwnerProfileOut.model_validate(profile)


@router.get("/profile/representatives", response_model=list[AuthorizedRepresentativeOut])
def read_representatives(
    current: CurrentUser = Depends(get_current_user), db: Session = Depends(get_db)
) -> list[AuthorizedRepresentativeOut]:
    _require_owner(current)
    return [
        AuthorizedRepresentativeOut.model_validate(rep)
        for rep in list_representatives(db, current.user.id)
    ]


@router.post(
    "/profile/representatives",
    response_model=AuthorizedRepresentativeOut,
    status_code=status.HTTP_201_CREATED,
)
def create_representative(
    data: AuthorizedRepresentativeIn,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AuthorizedRepresentativeOut:
    _require_owner(current)
    rep = add_representative(db, current.user.id, data)
    return AuthorizedRepresentativeOut.model_validate(rep)


@router.delete("/profile/representatives/{representative_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_representative(
    representative_id: uuid.UUID,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    _require_owner(current)
    try:
        remove_representative(db, current.user.id, representative_id)
    except RepresentativeNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Representative not found") from None
