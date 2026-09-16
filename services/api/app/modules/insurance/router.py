import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.modules.auth.dependencies import CurrentUser, get_current_user
from app.modules.insurance.schemas import (
    InsuranceClaimCreate,
    InsuranceClaimOut,
    InsuranceClaimUpdate,
    InsurancePolicyCreate,
    InsurancePolicyOut,
    InsurancePolicyUpdate,
)
from app.modules.insurance.service import (
    InsuranceClaimNotFoundError,
    InsurancePolicyNotFoundError,
    NotPropertyOwnerError,
    create_claim,
    create_policy,
    list_claims,
    list_policies,
    update_claim,
    update_policy,
)
from app.modules.properties.service import PropertyNotFoundError

router = APIRouter(prefix="/insurance", tags=["insurance"])


def _require_owner_or_admin_role(current: CurrentUser) -> None:
    if current.role not in ("owner", "admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Owner or admin role required")


@router.post("/policies", response_model=InsurancePolicyOut, status_code=status.HTTP_201_CREATED)
def create_policy_route(
    data: InsurancePolicyCreate,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> InsurancePolicyOut:
    _require_owner_or_admin_role(current)
    try:
        policy = create_policy(db, current.user.id, current.role, data)
    except PropertyNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found") from None
    except NotPropertyOwnerError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not the owner of this property") from None
    return InsurancePolicyOut.model_validate(policy)


@router.get("/policies", response_model=list[InsurancePolicyOut])
def list_policies_route(
    property_id: uuid.UUID,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[InsurancePolicyOut]:
    _require_owner_or_admin_role(current)
    return [InsurancePolicyOut.model_validate(p) for p in list_policies(db, property_id)]


@router.patch("/policies/{policy_id}", response_model=InsurancePolicyOut)
def update_policy_route(
    policy_id: uuid.UUID,
    data: InsurancePolicyUpdate,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> InsurancePolicyOut:
    _require_owner_or_admin_role(current)
    try:
        policy = update_policy(db, policy_id, current.user.id, current.role, data)
    except InsurancePolicyNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Policy not found") from None
    except PropertyNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found") from None
    except NotPropertyOwnerError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not the owner of this property") from None
    return InsurancePolicyOut.model_validate(policy)


@router.post(
    "/policies/{policy_id}/claims", response_model=InsuranceClaimOut, status_code=status.HTTP_201_CREATED
)
def create_claim_route(
    policy_id: uuid.UUID,
    data: InsuranceClaimCreate,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> InsuranceClaimOut:
    _require_owner_or_admin_role(current)
    try:
        claim = create_claim(db, policy_id, current.user.id, current.role, data)
    except InsurancePolicyNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Policy not found") from None
    except PropertyNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found") from None
    except NotPropertyOwnerError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not the owner of this property") from None
    return InsuranceClaimOut.model_validate(claim)


@router.get("/policies/{policy_id}/claims", response_model=list[InsuranceClaimOut])
def list_claims_route(
    policy_id: uuid.UUID,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[InsuranceClaimOut]:
    _require_owner_or_admin_role(current)
    return [InsuranceClaimOut.model_validate(c) for c in list_claims(db, policy_id)]


@router.patch("/claims/{claim_id}", response_model=InsuranceClaimOut)
def update_claim_route(
    claim_id: uuid.UUID,
    data: InsuranceClaimUpdate,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> InsuranceClaimOut:
    _require_owner_or_admin_role(current)
    try:
        claim = update_claim(db, claim_id, current.user.id, current.role, data)
    except InsuranceClaimNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Claim not found") from None
    except InsurancePolicyNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Policy not found") from None
    except PropertyNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found") from None
    except NotPropertyOwnerError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not the owner of this property") from None
    return InsuranceClaimOut.model_validate(claim)
