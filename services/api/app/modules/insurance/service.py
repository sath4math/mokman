import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.insurance import ClaimStatus, InsuranceClaim, InsurancePolicy
from app.modules.insurance.schemas import (
    InsuranceClaimCreate,
    InsuranceClaimUpdate,
    InsurancePolicyCreate,
    InsurancePolicyUpdate,
)
from app.modules.properties.service import get_property_by_id


class InsurancePolicyNotFoundError(Exception):
    pass


class InsuranceClaimNotFoundError(Exception):
    pass


class NotPropertyOwnerError(Exception):
    pass


def _require_owner_or_admin(db: Session, property_id: uuid.UUID, user_id: uuid.UUID, role: str) -> None:
    property_ = get_property_by_id(db, property_id)
    if role != "admin" and property_.owner_id != user_id:
        raise NotPropertyOwnerError


def create_policy(db: Session, user_id: uuid.UUID, role: str, data: InsurancePolicyCreate) -> InsurancePolicy:
    _require_owner_or_admin(db, data.property_id, user_id, role)
    policy = InsurancePolicy(**data.model_dump())
    db.add(policy)
    db.commit()
    db.refresh(policy)
    return policy


def list_policies(db: Session, property_id: uuid.UUID) -> list[InsurancePolicy]:
    return list(db.execute(select(InsurancePolicy).where(InsurancePolicy.property_id == property_id)).scalars())


def get_policy(db: Session, policy_id: uuid.UUID) -> InsurancePolicy:
    policy = db.get(InsurancePolicy, policy_id)
    if policy is None:
        raise InsurancePolicyNotFoundError
    return policy


def update_policy(
    db: Session, policy_id: uuid.UUID, user_id: uuid.UUID, role: str, data: InsurancePolicyUpdate
) -> InsurancePolicy:
    policy = get_policy(db, policy_id)
    _require_owner_or_admin(db, policy.property_id, user_id, role)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(policy, field, value)
    db.commit()
    db.refresh(policy)
    return policy


def create_claim(
    db: Session, policy_id: uuid.UUID, user_id: uuid.UUID, role: str, data: InsuranceClaimCreate
) -> InsuranceClaim:
    policy = get_policy(db, policy_id)
    _require_owner_or_admin(db, policy.property_id, user_id, role)
    claim = InsuranceClaim(policy_id=policy_id, **data.model_dump())
    db.add(claim)
    db.commit()
    db.refresh(claim)
    return claim


def list_claims(db: Session, policy_id: uuid.UUID) -> list[InsuranceClaim]:
    return list(db.execute(select(InsuranceClaim).where(InsuranceClaim.policy_id == policy_id)).scalars())


def get_claim(db: Session, claim_id: uuid.UUID) -> InsuranceClaim:
    claim = db.get(InsuranceClaim, claim_id)
    if claim is None:
        raise InsuranceClaimNotFoundError
    return claim


def update_claim(
    db: Session, claim_id: uuid.UUID, user_id: uuid.UUID, role: str, data: InsuranceClaimUpdate
) -> InsuranceClaim:
    claim = get_claim(db, claim_id)
    policy = get_policy(db, claim.policy_id)
    _require_owner_or_admin(db, policy.property_id, user_id, role)
    updates = data.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(claim, field, value)
    if updates.get("status") == ClaimStatus.SETTLED and claim.settled_at is None:
        claim.settled_at = datetime.now(UTC)
    db.commit()
    db.refresh(claim)
    return claim
