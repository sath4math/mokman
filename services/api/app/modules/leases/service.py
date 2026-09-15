import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.lease import Lease, LeaseStatus
from app.models.property import Property, PropertyStatus
from app.models.user import User
from app.modules.auth.service import get_user_role
from app.modules.leases.schemas import LeaseCreate
from app.modules.properties.service import get_owned_property


class LeaseNotFoundError(Exception):
    pass


class TenantAccountNotFoundError(Exception):
    pass


class NotPartyToLeaseError(Exception):
    pass


def create_lease(db: Session, owner_id: uuid.UUID, data: LeaseCreate) -> Lease:
    get_owned_property(db, owner_id, data.property_id)

    tenant = db.execute(select(User).where(User.email == data.tenant_email)).scalar_one_or_none()
    if tenant is None or get_user_role(db, tenant.id) != "tenant":
        raise TenantAccountNotFoundError

    lease = Lease(
        property_id=data.property_id,
        tenant_id=tenant.id,
        start_date=data.start_date,
        end_date=data.end_date,
        monthly_rent=data.monthly_rent,
        security_deposit=data.security_deposit,
        lock_in_period_months=data.lock_in_period_months,
        notice_period_days=data.notice_period_days,
        annual_escalation_percentage=data.annual_escalation_percentage,
        responsibilities=data.responsibilities,
    )
    db.add(lease)
    db.commit()
    db.refresh(lease)
    return lease


def list_leases_for_owner(db: Session, owner_id: uuid.UUID) -> list[Lease]:
    return list(
        db.execute(
            select(Lease).join(Property, Lease.property_id == Property.id).where(Property.owner_id == owner_id)
        ).scalars()
    )


def list_leases_for_tenant(db: Session, tenant_id: uuid.UUID) -> list[Lease]:
    return list(db.execute(select(Lease).where(Lease.tenant_id == tenant_id)).scalars())


def get_lease(db: Session, lease_id: uuid.UUID) -> Lease:
    lease = db.get(Lease, lease_id)
    if lease is None:
        raise LeaseNotFoundError
    return lease


def role_for_lease(db: Session, lease: Lease, user_id: uuid.UUID) -> str | None:
    """Returns 'owner', 'tenant', or None if the user has no relation to this lease."""
    if lease.tenant_id == user_id:
        return "tenant"
    property_ = db.get(Property, lease.property_id)
    if property_ is not None and property_.owner_id == user_id:
        return "owner"
    return None


def require_party(db: Session, lease: Lease, user_id: uuid.UUID) -> str:
    role = role_for_lease(db, lease, user_id)
    if role is None:
        raise NotPartyToLeaseError
    return role


def acknowledge_lease(db: Session, lease_id: uuid.UUID, user_id: uuid.UUID) -> Lease:
    lease = get_lease(db, lease_id)
    role = require_party(db, lease, user_id)

    now = datetime.now(UTC)
    if role == "owner":
        lease.owner_acknowledged_at = now
    else:
        lease.tenant_acknowledged_at = now

    if lease.owner_acknowledged_at and lease.tenant_acknowledged_at and lease.status == LeaseStatus.PENDING_ACKNOWLEDGMENT:
        lease.status = LeaseStatus.ACTIVE
        property_ = db.get(Property, lease.property_id)
        if property_ is not None:
            property_.status = PropertyStatus.OCCUPIED

    db.commit()
    db.refresh(lease)
    return lease


def terminate_lease(db: Session, lease_id: uuid.UUID, user_id: uuid.UUID) -> Lease:
    lease = get_lease(db, lease_id)
    require_party(db, lease, user_id)

    lease.status = LeaseStatus.TERMINATED
    property_ = db.get(Property, lease.property_id)
    if property_ is not None:
        property_.status = PropertyStatus.VACANT

    db.commit()
    db.refresh(lease)
    return lease
