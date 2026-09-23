import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.owner_profile import KycStatus
from app.modules.auth.dependencies import CurrentUser, get_current_user
from app.modules.owner.schemas import (
    AuthorizedRepresentativeIn,
    AuthorizedRepresentativeOut,
    KycRejectRequest,
    OwnerProfileAdminOut,
    OwnerProfileIn,
    OwnerProfileOut,
)
from app.modules.owner.service import (
    MissingKycDocumentError,
    ProfileNotFoundError,
    RepresentativeNotFoundError,
    UserNotFoundError,
    add_representative,
    approve_kyc,
    get_profile,
    get_profile_with_user,
    list_profiles,
    list_representatives,
    reject_kyc,
    remove_representative,
    upsert_profile,
)

router = APIRouter(prefix="/owner", tags=["owner"])


def _require_owner(current: CurrentUser) -> None:
    if current.role != "owner":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Owner role required")


def _require_admin(current: CurrentUser) -> None:
    if current.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required")


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
    try:
        profile = upsert_profile(db, current.user.id, data)
    except MissingKycDocumentError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Upload at least one KYC document (PAN card or ID proof) before saving your profile",
        ) from None
    return OwnerProfileOut.model_validate(profile)


@router.get("/profiles/{user_id}", response_model=OwnerProfileAdminOut)
def read_profile_for_admin(
    user_id: uuid.UUID,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> OwnerProfileAdminOut:
    _require_admin(current)
    try:
        profile, user = get_profile_with_user(db, user_id)
    except UserNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Owner not found") from None
    return OwnerProfileAdminOut(
        **OwnerProfileOut.model_validate(profile).model_dump(),
        user_id=user.id,
        full_name=user.full_name,
        email=user.email,
    )


@router.put("/profiles/{user_id}", response_model=OwnerProfileOut)
def update_profile_on_behalf(
    user_id: uuid.UUID,
    data: OwnerProfileIn,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> OwnerProfileOut:
    """Admin fills in and submits an owner's KYC on their behalf -- same
    validation (mandatory fields, at least one document) as the owner's
    own self-service PUT, just targeting a specified user_id instead of
    the caller."""
    _require_admin(current)
    try:
        profile = upsert_profile(db, user_id, data)
    except MissingKycDocumentError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Upload at least one KYC document (PAN card or ID proof) for this owner before saving",
        ) from None
    return OwnerProfileOut.model_validate(profile)


@router.get("/profiles", response_model=list[OwnerProfileAdminOut])
def list_profiles_for_admin(
    kyc_status: KycStatus | None = None,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[OwnerProfileAdminOut]:
    _require_admin(current)
    return [
        OwnerProfileAdminOut(
            **OwnerProfileOut.model_validate(profile).model_dump(),
            user_id=user.id,
            full_name=user.full_name,
            email=user.email,
        )
        for profile, user in list_profiles(db, kyc_status)
    ]


@router.post("/profiles/{user_id}/kyc/approve", response_model=OwnerProfileOut)
def approve_profile_kyc(
    user_id: uuid.UUID,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> OwnerProfileOut:
    _require_admin(current)
    try:
        profile = approve_kyc(db, user_id, current.user.id)
    except ProfileNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Owner profile not found") from None
    return OwnerProfileOut.model_validate(profile)


@router.post("/profiles/{user_id}/kyc/reject", response_model=OwnerProfileOut)
def reject_profile_kyc(
    user_id: uuid.UUID,
    data: KycRejectRequest,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> OwnerProfileOut:
    _require_admin(current)
    try:
        profile = reject_kyc(db, user_id, current.user.id, data.reason)
    except ProfileNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Owner profile not found") from None
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
