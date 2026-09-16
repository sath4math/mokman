import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.maintenance import MaintenanceTicket, TicketStatus
from app.models.property import Property
from app.models.rbac import Role, RoleAssignment
from app.models.user import User
from app.models.vendor import Vendor
from app.modules.auth.service import get_user_role
from app.modules.inspections.service import verify_property_access
from app.modules.maintenance.schemas import ResolveRequest, TicketCreate
from app.modules.properties.service import PropertyNotFoundError


class TicketNotFoundError(Exception):
    pass


class NotPartyToTicketError(Exception):
    pass


class InvalidAssigneeError(Exception):
    pass


class InvalidTicketTransitionError(Exception):
    pass


def create_ticket(db: Session, user_id: uuid.UUID, data: TicketCreate) -> MaintenanceTicket:
    verify_property_access(db, data.property_id, user_id)

    ticket = MaintenanceTicket(
        property_id=data.property_id,
        category=data.category,
        description=data.description,
        priority=data.priority,
        raised_by=user_id,
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


def list_tickets(
    db: Session, user_id: uuid.UUID, role: str, property_id: uuid.UUID | None
) -> list[MaintenanceTicket]:
    if property_id is not None:
        verify_property_access(db, property_id, user_id)
        stmt = select(MaintenanceTicket).where(MaintenanceTicket.property_id == property_id)
    elif role == "admin":
        stmt = select(MaintenanceTicket)
    elif role == "owner":
        stmt = select(MaintenanceTicket).join(Property, MaintenanceTicket.property_id == Property.id).where(
            Property.owner_id == user_id
        )
    elif role == "field_staff":
        stmt = select(MaintenanceTicket).where(MaintenanceTicket.assigned_to == user_id)
    elif role == "tenant":
        stmt = select(MaintenanceTicket).where(MaintenanceTicket.raised_by == user_id)
    else:
        return []
    return list(db.execute(stmt.order_by(MaintenanceTicket.created_at.desc())).scalars())


def get_ticket(db: Session, ticket_id: uuid.UUID) -> MaintenanceTicket:
    ticket = db.get(MaintenanceTicket, ticket_id)
    if ticket is None:
        raise TicketNotFoundError
    return ticket


def require_ticket_access(db: Session, ticket: MaintenanceTicket, user_id: uuid.UUID, role: str) -> None:
    if role == "admin":
        return
    if ticket.raised_by == user_id or ticket.assigned_to == user_id:
        return
    property_ = db.get(Property, ticket.property_id)
    if property_ is not None and property_.owner_id == user_id:
        return
    raise NotPartyToTicketError


def _require_owner_or_admin(db: Session, ticket: MaintenanceTicket, user_id: uuid.UUID, role: str) -> None:
    if role == "admin":
        return
    property_ = db.get(Property, ticket.property_id)
    if property_ is None:
        raise PropertyNotFoundError
    if property_.owner_id != user_id:
        raise NotPartyToTicketError


def assign_ticket(
    db: Session,
    ticket_id: uuid.UUID,
    user_id: uuid.UUID,
    role: str,
    assigned_to: uuid.UUID | None,
    assigned_vendor_id: uuid.UUID | None,
) -> MaintenanceTicket:
    ticket = get_ticket(db, ticket_id)
    _require_owner_or_admin(db, ticket, user_id, role)

    if ticket.status not in (TicketStatus.OPEN, TicketStatus.ASSIGNED):
        raise InvalidTicketTransitionError
    if (assigned_to is None) == (assigned_vendor_id is None):
        raise InvalidAssigneeError

    if assigned_to is not None:
        if get_user_role(db, assigned_to) != "field_staff":
            raise InvalidAssigneeError
        ticket.assigned_to = assigned_to
        ticket.assigned_vendor_id = None
    else:
        vendor = db.get(Vendor, assigned_vendor_id)
        if vendor is None or not vendor.is_active:
            raise InvalidAssigneeError
        ticket.assigned_vendor_id = assigned_vendor_id
        ticket.assigned_to = None

    ticket.status = TicketStatus.ASSIGNED
    db.commit()
    db.refresh(ticket)
    return ticket


def start_ticket(db: Session, ticket_id: uuid.UUID, user_id: uuid.UUID, role: str) -> MaintenanceTicket:
    ticket = get_ticket(db, ticket_id)
    if role not in ("admin",) and ticket.assigned_to != user_id:
        _require_owner_or_admin(db, ticket, user_id, role)

    if ticket.status != TicketStatus.ASSIGNED:
        raise InvalidTicketTransitionError

    ticket.status = TicketStatus.IN_PROGRESS
    db.commit()
    db.refresh(ticket)
    return ticket


def resolve_ticket(
    db: Session, ticket_id: uuid.UUID, user_id: uuid.UUID, role: str, data: ResolveRequest
) -> MaintenanceTicket:
    ticket = get_ticket(db, ticket_id)
    if role not in ("admin",) and ticket.assigned_to != user_id:
        _require_owner_or_admin(db, ticket, user_id, role)

    if ticket.status != TicketStatus.IN_PROGRESS:
        raise InvalidTicketTransitionError

    ticket.status = TicketStatus.RESOLVED
    ticket.resolution_notes = data.resolution_notes
    db.commit()
    db.refresh(ticket)
    return ticket


def close_ticket(db: Session, ticket_id: uuid.UUID, user_id: uuid.UUID, role: str) -> MaintenanceTicket:
    ticket = get_ticket(db, ticket_id)
    _require_owner_or_admin(db, ticket, user_id, role)

    if ticket.status != TicketStatus.RESOLVED:
        raise InvalidTicketTransitionError

    ticket.status = TicketStatus.CLOSED
    ticket.closed_at = datetime.now(UTC)
    db.commit()
    db.refresh(ticket)
    return ticket


def reopen_ticket(db: Session, ticket_id: uuid.UUID, user_id: uuid.UUID, role: str) -> MaintenanceTicket:
    ticket = get_ticket(db, ticket_id)
    if role != "admin" and ticket.raised_by != user_id:
        _require_owner_or_admin(db, ticket, user_id, role)

    if ticket.status != TicketStatus.CLOSED:
        raise InvalidTicketTransitionError

    ticket.status = TicketStatus.OPEN
    ticket.closed_at = None
    db.commit()
    db.refresh(ticket)
    return ticket


def list_field_staff(db: Session) -> list[User]:
    return list(
        db.execute(
            select(User)
            .join(RoleAssignment, RoleAssignment.user_id == User.id)
            .join(Role, Role.id == RoleAssignment.role_id)
            .where(Role.name == "field_staff")
        ).scalars()
    )
