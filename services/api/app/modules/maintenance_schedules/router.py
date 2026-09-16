import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.modules.auth.dependencies import CurrentUser, get_current_user
from app.modules.maintenance_schedules.schemas import (
    LogServiceRequest,
    MaintenanceScheduleCreate,
    MaintenanceScheduleOut,
)
from app.modules.maintenance_schedules.service import (
    MaintenanceScheduleNotFoundError,
    NotPropertyOwnerError,
    create_schedule,
    list_schedules,
    log_service,
)
from app.modules.properties.service import PropertyNotFoundError

router = APIRouter(prefix="/maintenance-schedules", tags=["maintenance-schedules"])


def _require_owner_or_admin_role(current: CurrentUser) -> None:
    if current.role not in ("owner", "admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Owner or admin role required")


@router.post("", response_model=MaintenanceScheduleOut, status_code=status.HTTP_201_CREATED)
def create(
    data: MaintenanceScheduleCreate,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MaintenanceScheduleOut:
    _require_owner_or_admin_role(current)
    try:
        schedule = create_schedule(db, current.user.id, current.role, data)
    except PropertyNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found") from None
    except NotPropertyOwnerError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not the owner of this property") from None
    return MaintenanceScheduleOut.model_validate(schedule)


@router.get("", response_model=list[MaintenanceScheduleOut])
def list_for_property(
    property_id: uuid.UUID,
    due_only: bool = False,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[MaintenanceScheduleOut]:
    _require_owner_or_admin_role(current)
    return [MaintenanceScheduleOut.model_validate(s) for s in list_schedules(db, property_id, due_only)]


@router.post("/{schedule_id}/log-service", response_model=MaintenanceScheduleOut)
def log(
    schedule_id: uuid.UUID,
    data: LogServiceRequest,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MaintenanceScheduleOut:
    try:
        schedule = log_service(db, schedule_id, current.user.id, current.role, data)
    except MaintenanceScheduleNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Schedule not found") from None
    except PropertyNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found") from None
    except NotPropertyOwnerError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not the owner of this property") from None
    return MaintenanceScheduleOut.model_validate(schedule)
