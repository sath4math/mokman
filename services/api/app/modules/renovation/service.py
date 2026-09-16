import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.expense import Expense, ExpenseStatus
from app.models.ledger import LedgerEntryType
from app.models.renovation import ProjectMilestone, RenovationProject
from app.modules.finance.service import record_ledger_entry
from app.modules.properties.service import get_property_by_id
from app.modules.renovation.schemas import MilestoneCreate, ProjectCreate, ProjectUpdate


class ProjectNotFoundError(Exception):
    pass


class MilestoneNotFoundError(Exception):
    pass


class NotPropertyOwnerError(Exception):
    pass


class MilestoneAlreadyPaidError(Exception):
    pass


def _require_owner_or_admin(db: Session, property_id: uuid.UUID, user_id: uuid.UUID, role: str) -> None:
    property_ = get_property_by_id(db, property_id)
    if role != "admin" and property_.owner_id != user_id:
        raise NotPropertyOwnerError


def create_project(db: Session, user_id: uuid.UUID, role: str, data: ProjectCreate) -> RenovationProject:
    _require_owner_or_admin(db, data.property_id, user_id, role)
    project = RenovationProject(**data.model_dump())
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def list_projects(db: Session, property_id: uuid.UUID) -> list[RenovationProject]:
    return list(db.execute(select(RenovationProject).where(RenovationProject.property_id == property_id)).scalars())


def get_project(db: Session, project_id: uuid.UUID) -> RenovationProject:
    project = db.get(RenovationProject, project_id)
    if project is None:
        raise ProjectNotFoundError
    return project


def update_project(
    db: Session, project_id: uuid.UUID, user_id: uuid.UUID, role: str, data: ProjectUpdate
) -> RenovationProject:
    project = get_project(db, project_id)
    _require_owner_or_admin(db, project.property_id, user_id, role)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(project, field, value)
    db.commit()
    db.refresh(project)
    return project


def create_milestone(
    db: Session, project_id: uuid.UUID, user_id: uuid.UUID, role: str, data: MilestoneCreate
) -> ProjectMilestone:
    project = get_project(db, project_id)
    _require_owner_or_admin(db, project.property_id, user_id, role)
    milestone = ProjectMilestone(project_id=project_id, **data.model_dump())
    db.add(milestone)
    db.commit()
    db.refresh(milestone)
    return milestone


def list_milestones(db: Session, project_id: uuid.UUID) -> list[ProjectMilestone]:
    return list(db.execute(select(ProjectMilestone).where(ProjectMilestone.project_id == project_id)).scalars())


def get_milestone(db: Session, milestone_id: uuid.UUID) -> ProjectMilestone:
    milestone = db.get(ProjectMilestone, milestone_id)
    if milestone is None:
        raise MilestoneNotFoundError
    return milestone


def complete_milestone(db: Session, milestone_id: uuid.UUID, user_id: uuid.UUID, role: str) -> ProjectMilestone:
    milestone = get_milestone(db, milestone_id)
    project = get_project(db, milestone.project_id)
    _require_owner_or_admin(db, project.property_id, user_id, role)
    milestone.completed_at = datetime.now(UTC)
    db.commit()
    db.refresh(milestone)
    return milestone


def pay_milestone(db: Session, milestone_id: uuid.UUID, user_id: uuid.UUID, role: str) -> ProjectMilestone:
    """Reuses the Expense/ledger pipeline directly -- the exact
    construction 6d's log_material_usage billing branch already uses.
    A renovation payment is a real operational cost, not an
    administrative reminder like 8a's insurance/compliance dues."""
    milestone = get_milestone(db, milestone_id)
    project = get_project(db, milestone.project_id)
    _require_owner_or_admin(db, project.property_id, user_id, role)
    if milestone.paid_at is not None:
        raise MilestoneAlreadyPaidError

    expense = Expense(
        property_id=project.property_id,
        category="renovation",
        amount=milestone.payment_amount,
        description=milestone.title,
        submitted_by=user_id,
        vendor_id=project.vendor_id,
        status=ExpenseStatus.APPROVED,
        approved_by=user_id,
        approved_at=datetime.now(UTC),
    )
    db.add(expense)
    db.flush()
    record_ledger_entry(
        db,
        property_id=project.property_id,
        entry_type=LedgerEntryType.EXPENSE,
        amount=expense.amount,
        recorded_by=user_id,
        expense_id=expense.id,
    )
    milestone.paid_at = datetime.now(UTC)
    milestone.expense_id = expense.id
    db.commit()
    db.refresh(milestone)
    return milestone
