import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.modules.auth.dependencies import CurrentUser, get_current_user
from app.modules.inspections.service import NotPartyToInspectionError
from app.modules.maintenance.schemas import (
    AssignRequest,
    FieldStaffOut,
    ResolveRequest,
    TicketCreate,
    TicketOut,
)
from app.modules.maintenance.service import (
    InvalidAssigneeError,
    InvalidTicketTransitionError,
    NotPartyToTicketError,
    TicketNotFoundError,
    assign_ticket,
    close_ticket,
    create_ticket,
    get_ticket,
    list_field_staff,
    list_tickets,
    reopen_ticket,
    require_ticket_access,
    resolve_ticket,
    start_ticket,
)
from app.modules.properties.service import PropertyNotFoundError

router = APIRouter(prefix="/maintenance", tags=["maintenance"])


@router.post("/tickets", response_model=TicketOut, status_code=status.HTTP_201_CREATED)
def create(
    data: TicketCreate,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TicketOut:
    if current.role not in ("tenant", "owner", "admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tenant, owner, or admin role required")
    try:
        ticket = create_ticket(db, current.user.id, data)
    except PropertyNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found") from None
    except NotPartyToInspectionError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a party to this property") from None
    return TicketOut.model_validate(ticket)


@router.get("/tickets", response_model=list[TicketOut])
def list_for_viewer(
    property_id: uuid.UUID | None = None,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[TicketOut]:
    try:
        tickets = list_tickets(db, current.user.id, current.role, property_id)
    except PropertyNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found") from None
    except NotPartyToInspectionError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a party to this property") from None
    return [TicketOut.model_validate(t) for t in tickets]


@router.get("/staff", response_model=list[FieldStaffOut])
def staff(
    current: CurrentUser = Depends(get_current_user), db: Session = Depends(get_db)
) -> list[FieldStaffOut]:
    if current.role not in ("owner", "admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Owner or admin role required")
    return [FieldStaffOut.model_validate(u) for u in list_field_staff(db)]


@router.get("/tickets/{ticket_id}", response_model=TicketOut)
def read(
    ticket_id: uuid.UUID,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TicketOut:
    try:
        ticket = get_ticket(db, ticket_id)
        require_ticket_access(db, ticket, current.user.id, current.role)
    except TicketNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found") from None
    except NotPartyToTicketError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a party to this ticket") from None
    return TicketOut.model_validate(ticket)


@router.post("/tickets/{ticket_id}/assign", response_model=TicketOut)
def assign(
    ticket_id: uuid.UUID,
    data: AssignRequest,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TicketOut:
    try:
        ticket = assign_ticket(db, ticket_id, current.user.id, current.role, data.assigned_to)
    except TicketNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found") from None
    except PropertyNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found") from None
    except NotPartyToTicketError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Owner or admin role required") from None
    except InvalidAssigneeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Assignee must be a field_staff account"
        ) from None
    except InvalidTicketTransitionError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Ticket cannot be assigned in its current status"
        ) from None
    return TicketOut.model_validate(ticket)


@router.post("/tickets/{ticket_id}/start", response_model=TicketOut)
def start(
    ticket_id: uuid.UUID,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TicketOut:
    try:
        ticket = start_ticket(db, ticket_id, current.user.id, current.role)
    except TicketNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found") from None
    except PropertyNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found") from None
    except NotPartyToTicketError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Only the assignee, owner, or admin can start work"
        ) from None
    except InvalidTicketTransitionError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Ticket must be assigned before work can start"
        ) from None
    return TicketOut.model_validate(ticket)


@router.post("/tickets/{ticket_id}/resolve", response_model=TicketOut)
def resolve(
    ticket_id: uuid.UUID,
    data: ResolveRequest,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TicketOut:
    try:
        ticket = resolve_ticket(db, ticket_id, current.user.id, current.role, data)
    except TicketNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found") from None
    except PropertyNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found") from None
    except NotPartyToTicketError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Only the assignee, owner, or admin can resolve"
        ) from None
    except InvalidTicketTransitionError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Ticket must be in progress to resolve"
        ) from None
    return TicketOut.model_validate(ticket)


@router.post("/tickets/{ticket_id}/close", response_model=TicketOut)
def close(
    ticket_id: uuid.UUID,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TicketOut:
    try:
        ticket = close_ticket(db, ticket_id, current.user.id, current.role)
    except TicketNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found") from None
    except PropertyNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found") from None
    except NotPartyToTicketError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Owner or admin role required") from None
    except InvalidTicketTransitionError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Ticket must be resolved before closing"
        ) from None
    return TicketOut.model_validate(ticket)


@router.post("/tickets/{ticket_id}/reopen", response_model=TicketOut)
def reopen(
    ticket_id: uuid.UUID,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TicketOut:
    try:
        ticket = reopen_ticket(db, ticket_id, current.user.id, current.role)
    except TicketNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found") from None
    except PropertyNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found") from None
    except NotPartyToTicketError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Only the raiser, owner, or admin can reopen"
        ) from None
    except InvalidTicketTransitionError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Only a closed ticket can be reopened") from None
    return TicketOut.model_validate(ticket)
