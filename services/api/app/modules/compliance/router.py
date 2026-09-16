import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.modules.auth.dependencies import CurrentUser, get_current_user
from app.modules.compliance.schemas import ComplianceDueCreate, ComplianceDueOut, MarkPaidRequest
from app.modules.compliance.service import (
    ComplianceDueNotFoundError,
    NotPropertyOwnerError,
    create_due,
    list_dues,
    mark_due_paid,
)
from app.modules.properties.service import PropertyNotFoundError

router = APIRouter(prefix="/compliance", tags=["compliance"])


def _require_owner_or_admin_role(current: CurrentUser) -> None:
    if current.role not in ("owner", "admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Owner or admin role required")


@router.post("/dues", response_model=ComplianceDueOut, status_code=status.HTTP_201_CREATED)
def create(
    data: ComplianceDueCreate,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ComplianceDueOut:
    _require_owner_or_admin_role(current)
    try:
        due = create_due(db, current.user.id, current.role, data)
    except PropertyNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found") from None
    except NotPropertyOwnerError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not the owner of this property") from None
    return ComplianceDueOut.model_validate(due)


@router.get("/dues", response_model=list[ComplianceDueOut])
def list_for_property(
    property_id: uuid.UUID,
    due_only: bool = False,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ComplianceDueOut]:
    _require_owner_or_admin_role(current)
    return [ComplianceDueOut.model_validate(d) for d in list_dues(db, property_id, due_only)]


@router.post("/dues/{due_id}/mark-paid", response_model=ComplianceDueOut)
def mark_paid(
    due_id: uuid.UUID,
    data: MarkPaidRequest,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ComplianceDueOut:
    _require_owner_or_admin_role(current)
    try:
        due = mark_due_paid(db, due_id, current.user.id, current.role, data)
    except ComplianceDueNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Due not found") from None
    except PropertyNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found") from None
    except NotPropertyOwnerError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not the owner of this property") from None
    return ComplianceDueOut.model_validate(due)
