import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.modules.auth.dependencies import CurrentUser, get_current_user
from app.modules.properties.service import PropertyNotFoundError
from app.modules.renovation.schemas import (
    MilestoneCreate,
    MilestoneOut,
    ProjectCreate,
    ProjectOut,
    ProjectUpdate,
)
from app.modules.renovation.service import (
    MilestoneAlreadyPaidError,
    MilestoneNotFoundError,
    NotPropertyOwnerError,
    ProjectNotFoundError,
    complete_milestone,
    create_milestone,
    create_project,
    list_milestones,
    list_projects,
    pay_milestone,
    update_project,
)

router = APIRouter(prefix="/renovation", tags=["renovation"])


def _require_owner_or_admin_role(current: CurrentUser) -> None:
    if current.role not in ("owner", "admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Owner or admin role required")


@router.post("/projects", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
def create_project_route(
    data: ProjectCreate,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProjectOut:
    _require_owner_or_admin_role(current)
    try:
        project = create_project(db, current.user.id, current.role, data)
    except PropertyNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found") from None
    except NotPropertyOwnerError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not the owner of this property") from None
    return ProjectOut.model_validate(project)


@router.get("/projects", response_model=list[ProjectOut])
def list_projects_route(
    property_id: uuid.UUID,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ProjectOut]:
    _require_owner_or_admin_role(current)
    return [ProjectOut.model_validate(p) for p in list_projects(db, property_id)]


@router.patch("/projects/{project_id}", response_model=ProjectOut)
def update_project_route(
    project_id: uuid.UUID,
    data: ProjectUpdate,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProjectOut:
    _require_owner_or_admin_role(current)
    try:
        project = update_project(db, project_id, current.user.id, current.role, data)
    except ProjectNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found") from None
    except PropertyNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found") from None
    except NotPropertyOwnerError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not the owner of this property") from None
    return ProjectOut.model_validate(project)


@router.post(
    "/projects/{project_id}/milestones", response_model=MilestoneOut, status_code=status.HTTP_201_CREATED
)
def create_milestone_route(
    project_id: uuid.UUID,
    data: MilestoneCreate,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MilestoneOut:
    _require_owner_or_admin_role(current)
    try:
        milestone = create_milestone(db, project_id, current.user.id, current.role, data)
    except ProjectNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found") from None
    except PropertyNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found") from None
    except NotPropertyOwnerError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not the owner of this property") from None
    return MilestoneOut.model_validate(milestone)


@router.get("/projects/{project_id}/milestones", response_model=list[MilestoneOut])
def list_milestones_route(
    project_id: uuid.UUID,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[MilestoneOut]:
    _require_owner_or_admin_role(current)
    return [MilestoneOut.model_validate(m) for m in list_milestones(db, project_id)]


@router.post("/milestones/{milestone_id}/complete", response_model=MilestoneOut)
def complete_milestone_route(
    milestone_id: uuid.UUID,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MilestoneOut:
    _require_owner_or_admin_role(current)
    try:
        milestone = complete_milestone(db, milestone_id, current.user.id, current.role)
    except MilestoneNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Milestone not found") from None
    except ProjectNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found") from None
    except PropertyNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found") from None
    except NotPropertyOwnerError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not the owner of this property") from None
    return MilestoneOut.model_validate(milestone)


@router.post("/milestones/{milestone_id}/pay", response_model=MilestoneOut)
def pay_milestone_route(
    milestone_id: uuid.UUID,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MilestoneOut:
    _require_owner_or_admin_role(current)
    try:
        milestone = pay_milestone(db, milestone_id, current.user.id, current.role)
    except MilestoneNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Milestone not found") from None
    except ProjectNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found") from None
    except PropertyNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found") from None
    except NotPropertyOwnerError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not the owner of this property") from None
    except MilestoneAlreadyPaidError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Milestone already paid") from None
    return MilestoneOut.model_validate(milestone)
