import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.modules.auth.dependencies import CurrentUser, get_current_user
from app.modules.leases.schemas import LeaseCreate, LeaseOut
from app.modules.leases.service import (
    LeaseNotFoundError,
    NotPartyToLeaseError,
    TenantAccountNotFoundError,
    acknowledge_lease,
    create_lease,
    get_lease,
    list_leases_for_owner,
    list_leases_for_tenant,
    require_party,
    terminate_lease,
)
from app.modules.properties.service import PropertyNotFoundError

router = APIRouter(prefix="/leases", tags=["leases"])


@router.post("", response_model=LeaseOut, status_code=status.HTTP_201_CREATED)
def create(
    data: LeaseCreate,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> LeaseOut:
    if current.role != "owner":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Owner role required")
    try:
        lease = create_lease(db, current.user.id, data)
    except PropertyNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found") from None
    except TenantAccountNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No tenant account found for that email"
        ) from None
    return LeaseOut.model_validate(lease)


@router.get("", response_model=list[LeaseOut])
def list_leases(
    current: CurrentUser = Depends(get_current_user), db: Session = Depends(get_db)
) -> list[LeaseOut]:
    if current.role == "owner":
        leases = list_leases_for_owner(db, current.user.id)
    elif current.role == "tenant":
        leases = list_leases_for_tenant(db, current.user.id)
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Owner or tenant role required")
    return [LeaseOut.model_validate(lease) for lease in leases]


@router.get("/{lease_id}", response_model=LeaseOut)
def read_lease(
    lease_id: uuid.UUID,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> LeaseOut:
    try:
        lease = get_lease(db, lease_id)
        require_party(db, lease, current.user.id)
    except LeaseNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lease not found") from None
    except NotPartyToLeaseError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a party to this lease") from None
    return LeaseOut.model_validate(lease)


@router.post("/{lease_id}/acknowledge", response_model=LeaseOut)
def acknowledge(
    lease_id: uuid.UUID,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> LeaseOut:
    try:
        lease = acknowledge_lease(db, lease_id, current.user.id)
    except LeaseNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lease not found") from None
    except NotPartyToLeaseError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a party to this lease") from None
    return LeaseOut.model_validate(lease)


@router.post("/{lease_id}/terminate", response_model=LeaseOut)
def terminate(
    lease_id: uuid.UUID,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> LeaseOut:
    try:
        lease = terminate_lease(db, lease_id, current.user.id)
    except LeaseNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lease not found") from None
    except NotPartyToLeaseError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a party to this lease") from None
    return LeaseOut.model_validate(lease)
