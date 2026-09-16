import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.inspection import Inspection
from app.models.insurance import ClaimStatus, InsuranceClaim, InsurancePolicy
from app.models.lease import Lease, LeaseStatus
from app.models.ledger import LedgerEntry, LedgerEntryType
from app.models.maintenance import MaintenanceSchedule, MaintenanceTicket, TicketStatus
from app.models.property import Property
from app.models.renovation import ProjectStatus, RenovationProject
from app.modules.properties.schemas import (
    InvestmentSummaryOut,
    PropertyCreate,
    PropertyHealthScoreOut,
    PropertyUpdate,
    SaleReadinessOut,
)

_INVESTMENT_TRAILING_DAYS = 365

# Phase 7b: a deterministic 0-100 score, not a trained/ML prediction --
# capped deductions per signal so no single ticket-heavy property can
# swamp the others, and each count is returned alongside the score so
# it's explainable, not a black box.
_OPEN_TICKET_PENALTY = 5
_OPEN_TICKET_CAP = 30
_REPEAT_FAILURE_PENALTY = 10
_REPEAT_FAILURE_CAP = 20
_SLA_BREACH_PENALTY = 10
_SLA_BREACH_CAP = 20
_OVERDUE_PM_PENALTY = 5
_OVERDUE_PM_CAP = 20
_OVERDUE_FOLLOWUP_PENALTY = 10
_OVERDUE_FOLLOWUP_CAP = 20


class PropertyNotFoundError(Exception):
    pass


def create_property(db: Session, owner_id: uuid.UUID, data: PropertyCreate) -> Property:
    property_ = Property(owner_id=owner_id, **data.model_dump())
    db.add(property_)
    db.commit()
    db.refresh(property_)
    return property_


def list_properties_for_owner(db: Session, owner_id: uuid.UUID) -> list[Property]:
    return list(db.execute(select(Property).where(Property.owner_id == owner_id)).scalars())


def list_all_properties(db: Session) -> list[Property]:
    return list(db.execute(select(Property)).scalars())


def get_owned_property(db: Session, owner_id: uuid.UUID, property_id: uuid.UUID) -> Property:
    property_ = db.get(Property, property_id)
    if property_ is None or property_.owner_id != owner_id:
        raise PropertyNotFoundError
    return property_


def get_property_by_id(db: Session, property_id: uuid.UUID) -> Property:
    property_ = db.get(Property, property_id)
    if property_ is None:
        raise PropertyNotFoundError
    return property_


def update_property(db: Session, owner_id: uuid.UUID, property_id: uuid.UUID, data: PropertyUpdate) -> Property:
    property_ = get_owned_property(db, owner_id, property_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(property_, field, value)
    db.commit()
    db.refresh(property_)
    return property_


def compute_health_score(db: Session, property_id: uuid.UUID) -> PropertyHealthScoreOut:
    today = datetime.now(UTC).date()

    open_tickets = db.execute(
        select(func.count())
        .select_from(MaintenanceTicket)
        .where(MaintenanceTicket.property_id == property_id, MaintenanceTicket.status != TicketStatus.CLOSED)
    ).scalar_one()
    repeat_failure_tickets = db.execute(
        select(func.count())
        .select_from(MaintenanceTicket)
        .where(MaintenanceTicket.property_id == property_id, MaintenanceTicket.is_repeat_failure.is_(True))
    ).scalar_one()
    sla_breached_tickets = db.execute(
        select(func.count())
        .select_from(MaintenanceTicket)
        .where(MaintenanceTicket.property_id == property_id, MaintenanceTicket.sla_breached_at.is_not(None))
    ).scalar_one()
    overdue_pm_items = db.execute(
        select(func.count())
        .select_from(MaintenanceSchedule)
        .where(
            MaintenanceSchedule.property_id == property_id,
            MaintenanceSchedule.is_active.is_(True),
            MaintenanceSchedule.next_due_on <= today,
        )
    ).scalar_one()
    overdue_inspection_followups = db.execute(
        select(func.count())
        .select_from(Inspection)
        .where(Inspection.property_id == property_id, Inspection.follow_up_due_on.is_not(None))
        .where(Inspection.follow_up_due_on <= today)
    ).scalar_one()

    deductions = (
        min(open_tickets * _OPEN_TICKET_PENALTY, _OPEN_TICKET_CAP)
        + min(repeat_failure_tickets * _REPEAT_FAILURE_PENALTY, _REPEAT_FAILURE_CAP)
        + min(sla_breached_tickets * _SLA_BREACH_PENALTY, _SLA_BREACH_CAP)
        + min(overdue_pm_items * _OVERDUE_PM_PENALTY, _OVERDUE_PM_CAP)
        + min(overdue_inspection_followups * _OVERDUE_FOLLOWUP_PENALTY, _OVERDUE_FOLLOWUP_CAP)
    )

    return PropertyHealthScoreOut(
        score=max(0, 100 - deductions),
        open_tickets=open_tickets,
        repeat_failure_tickets=repeat_failure_tickets,
        sla_breached_tickets=sla_breached_tickets,
        overdue_pm_items=overdue_pm_items,
        overdue_inspection_followups=overdue_inspection_followups,
    )


def compute_investment_summary(db: Session, property_id: uuid.UUID) -> InvestmentSummaryOut:
    """Deterministic formulas over Property.purchase_price/
    current_market_value plus the existing ledger -- no ML, every
    metric is None when an input it needs is missing (Phase 8c)."""
    property_ = get_property_by_id(db, property_id)
    cutoff = datetime.now(UTC) - timedelta(days=_INVESTMENT_TRAILING_DAYS)

    trailing_12_month_rent_income = db.execute(
        select(func.coalesce(func.sum(LedgerEntry.amount), 0.0)).where(
            LedgerEntry.property_id == property_id,
            LedgerEntry.entry_type == LedgerEntryType.RENT_PAYMENT,
            LedgerEntry.occurred_at >= cutoff,
        )
    ).scalar_one()

    all_time_totals: dict[LedgerEntryType, float] = {}
    for entry_type in (LedgerEntryType.RENT_PAYMENT, LedgerEntryType.EXPENSE, LedgerEntryType.MOKMAN_FEE):
        all_time_totals[entry_type] = db.execute(
            select(func.coalesce(func.sum(LedgerEntry.amount), 0.0)).where(
                LedgerEntry.property_id == property_id, LedgerEntry.entry_type == entry_type
            )
        ).scalar_one()
    total_net_income_all_time = (
        all_time_totals[LedgerEntryType.RENT_PAYMENT]
        - all_time_totals[LedgerEntryType.EXPENSE]
        - all_time_totals[LedgerEntryType.MOKMAN_FEE]
    )

    purchase_price = property_.purchase_price
    current_market_value = property_.current_market_value

    appreciation_percentage = None
    roi_percentage = None
    if purchase_price and current_market_value is not None:
        appreciation_percentage = (current_market_value - purchase_price) / purchase_price * 100
        roi_percentage = (current_market_value - purchase_price + total_net_income_all_time) / purchase_price * 100

    gross_yield_percentage = trailing_12_month_rent_income / purchase_price * 100 if purchase_price else None

    return InvestmentSummaryOut(
        property_id=property_id,
        property_name=property_.name,
        purchase_price=purchase_price,
        current_market_value=current_market_value,
        appreciation_percentage=appreciation_percentage,
        trailing_12_month_rent_income=trailing_12_month_rent_income,
        gross_yield_percentage=gross_yield_percentage,
        total_net_income_all_time=total_net_income_all_time,
        roi_percentage=roi_percentage,
    )


def list_investment_summaries(db: Session, owner_id: uuid.UUID) -> list[InvestmentSummaryOut]:
    return [compute_investment_summary(db, p.id) for p in list_properties_for_owner(db, owner_id)]


def compute_sale_readiness(db: Session, property_id: uuid.UUID) -> SaleReadinessOut:
    """A deterministic readiness checklist (Phase 8d), not a scored
    formula like compute_health_score -- is_ready is True only when
    every signal is clear. Imports InsuranceClaim/RenovationProject as
    models directly (not their service modules, which already import
    this one -- a top-level service import here would cycle)."""
    open_tickets = db.execute(
        select(func.count())
        .select_from(MaintenanceTicket)
        .where(MaintenanceTicket.property_id == property_id, MaintenanceTicket.status != TicketStatus.CLOSED)
    ).scalar_one()

    has_active_lease = (
        db.execute(
            select(func.count())
            .select_from(Lease)
            .where(Lease.property_id == property_id, Lease.status == LeaseStatus.ACTIVE)
        ).scalar_one()
        > 0
    )

    unsettled_insurance_claims = db.execute(
        select(func.count())
        .select_from(InsuranceClaim)
        .join(InsurancePolicy, InsuranceClaim.policy_id == InsurancePolicy.id)
        .where(
            InsurancePolicy.property_id == property_id,
            InsuranceClaim.status.not_in((ClaimStatus.SETTLED, ClaimStatus.REJECTED)),
        )
    ).scalar_one()

    incomplete_renovation_projects = db.execute(
        select(func.count())
        .select_from(RenovationProject)
        .where(
            RenovationProject.property_id == property_id,
            RenovationProject.status.not_in((ProjectStatus.COMPLETED, ProjectStatus.CANCELLED)),
        )
    ).scalar_one()

    is_ready = (
        open_tickets == 0
        and not has_active_lease
        and unsettled_insurance_claims == 0
        and incomplete_renovation_projects == 0
    )

    return SaleReadinessOut(
        property_id=property_id,
        is_ready=is_ready,
        open_tickets=open_tickets,
        has_active_lease=has_active_lease,
        unsettled_insurance_claims=unsettled_insurance_claims,
        incomplete_renovation_projects=incomplete_renovation_projects,
    )
