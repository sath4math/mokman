import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from app.models.audit import AuditLog
from app.models.expense import Expense
from app.models.maintenance import (
    ChecklistTemplate,
    EligibilityOutcome,
    MaintenanceTicket,
    ServiceCategory,
    ServiceEligibilityRule,
    TicketPriority,
    TicketStatus,
)
from app.models.owner_profile import OwnerPackage, OwnerProfile
from app.models.property import Property
from app.models.rbac import Role, RoleAssignment
from app.models.user import User
from app.models.vendor import Vendor
from app.modules.auth.service import get_user_role
from app.modules.documents.service import list_documents
from app.modules.inspections.service import verify_property_access
from app.modules.maintenance.schemas import (
    ChecklistTemplateIn,
    ChecklistTemplateUpdate,
    MaintenanceSummaryOut,
    ResolveRequest,
    ServiceCategoryIn,
    ServiceCategoryUpdate,
    ServiceEligibilityRuleIn,
    ServiceEligibilityRuleUpdate,
    TicketCreate,
)
from app.modules.properties.service import PropertyNotFoundError

# Doc's exit gate calls for tickets "routed with SLA" — these are the
# per-priority response windows the escalation check compares against.
PRIORITY_SLA_HOURS: dict[TicketPriority, int] = {
    TicketPriority.URGENT: 4,
    TicketPriority.HIGH: 24,
    TicketPriority.MEDIUM: 72,
    TicketPriority.LOW: 168,
}


class TicketNotFoundError(Exception):
    pass


class NotPartyToTicketError(Exception):
    pass


class InvalidAssigneeError(Exception):
    pass


class InvalidTicketTransitionError(Exception):
    pass


class NotPropertyOwnerError(Exception):
    pass


class ChecklistTemplateNotFoundError(Exception):
    pass


class NoChecklistError(Exception):
    pass


class ChecklistItemNotFoundError(Exception):
    pass


class ChecklistIncompleteError(Exception):
    pass


class MissingEvidenceError(Exception):
    pass


class ServiceCategoryNotFoundError(Exception):
    pass


class ServiceCategoryInactiveError(Exception):
    pass


class ServiceEligibilityRuleNotFoundError(Exception):
    pass


class EscalationApprovalRequiredError(Exception):
    pass


class ThirdPartyRequiredError(Exception):
    pass


def _resolve_eligibility_rule(
    db: Session, service_category_id: uuid.UUID, package: OwnerPackage
) -> ServiceEligibilityRule | None:
    return db.execute(
        select(ServiceEligibilityRule).where(
            ServiceEligibilityRule.service_category_id == service_category_id,
            ServiceEligibilityRule.package == package,
        )
    ).scalar_one_or_none()


def _owner_package_for_property(db: Session, property_id: uuid.UUID) -> OwnerPackage:
    property_ = db.get(Property, property_id)
    owner_profile = db.get(OwnerProfile, property_.owner_id) if property_ else None
    return owner_profile.package if owner_profile else OwnerPackage.STARTER


def _exceeds_frequency_limit(
    db: Session, owner_id: uuid.UUID, category: str, max_occurrences: int, period_days: int
) -> bool:
    cutoff = datetime.now(UTC) - timedelta(days=period_days)
    count = db.execute(
        select(func.count())
        .select_from(MaintenanceTicket)
        .join(Property, Property.id == MaintenanceTicket.property_id)
        .where(
            Property.owner_id == owner_id,
            MaintenanceTicket.category == category,
            MaintenanceTicket.created_at >= cutoff,
        )
    ).scalar_one()
    return count >= max_occurrences


def create_ticket(db: Session, user_id: uuid.UUID, data: TicketCreate) -> MaintenanceTicket:
    verify_property_access(db, data.property_id, user_id)

    service_category = db.execute(
        select(ServiceCategory).where(ServiceCategory.name == data.category)
    ).scalar_one_or_none()
    if service_category is not None and not service_category.is_active:
        raise ServiceCategoryInactiveError

    priority = data.priority
    if priority is None:
        priority = service_category.default_priority if service_category else TicketPriority.MEDIUM

    if service_category is not None and service_category.estimated_completion_hours is not None:
        sla_hours = service_category.estimated_completion_hours
    else:
        sla_hours = PRIORITY_SLA_HOURS[priority]

    eligibility_outcome = None
    fair_use_breached = False
    if service_category is not None:
        property_ = db.get(Property, data.property_id)
        owner_package = _owner_package_for_property(db, data.property_id)
        rule = _resolve_eligibility_rule(db, service_category.id, owner_package)
        if rule is not None:
            eligibility_outcome = rule.outcome
            if rule.max_occurrences is not None and rule.period_days is not None and property_ is not None:
                fair_use_breached = _exceeds_frequency_limit(
                    db, property_.owner_id, data.category, rule.max_occurrences, rule.period_days
                )

    now = datetime.now(UTC)
    ticket = MaintenanceTicket(
        property_id=data.property_id,
        category=data.category,
        description=data.description,
        priority=priority,
        raised_by=user_id,
        sla_due_at=now + timedelta(hours=sla_hours),
        eligibility_outcome=eligibility_outcome,
        fair_use_breached=fair_use_breached,
    )

    # Repeat-failure detection: a prior closed ticket on the same
    # property+category whose warranty is still active means this is
    # likely the same issue recurring, not a new one.
    prior = db.execute(
        select(MaintenanceTicket)
        .where(MaintenanceTicket.property_id == data.property_id)
        .where(MaintenanceTicket.category == data.category)
        .where(MaintenanceTicket.status == TicketStatus.CLOSED)
        .where(MaintenanceTicket.warranty_expires_on.is_not(None))
        .where(MaintenanceTicket.warranty_expires_on >= now.date())
        .order_by(MaintenanceTicket.closed_at.desc())
    ).scalars().first()
    if prior is not None:
        ticket.is_repeat_failure = True
        ticket.related_ticket_id = prior.id

    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


def run_sla_check(db: Session) -> list[uuid.UUID]:
    """Flags newly-SLA-breached tickets. Called by an external cron
    against POST /internal/maintenance/sla-check, not from user traffic.

    The single UPDATE...RETURNING is naturally safe against overlapping
    cron runs (each row can only be claimed once, no lock needed).
    """
    now = datetime.now(UTC)
    stmt = (
        update(MaintenanceTicket)
        .where(MaintenanceTicket.sla_breached_at.is_(None))
        .where(MaintenanceTicket.sla_due_at.is_not(None))
        .where(MaintenanceTicket.sla_due_at < now)
        .where(MaintenanceTicket.status != TicketStatus.CLOSED)
        .values(sla_breached_at=now)
        .returning(MaintenanceTicket.id)
    )
    breached_ids = list(db.execute(stmt).scalars())
    for ticket_id in breached_ids:
        db.add(
            AuditLog(
                actor_id=None,
                action="ticket.sla_breached",
                entity_type="maintenance_ticket",
                entity_id=ticket_id,
            )
        )
    db.commit()
    return breached_ids


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


def diagnose_ticket(
    db: Session, ticket_id: uuid.UUID, user_id: uuid.UUID, role: str, diagnosis_notes: str
) -> MaintenanceTicket:
    ticket = get_ticket(db, ticket_id)
    _require_owner_or_admin(db, ticket, user_id, role)

    if ticket.status != TicketStatus.OPEN:
        raise InvalidTicketTransitionError

    ticket.status = TicketStatus.DIAGNOSED
    ticket.diagnosis_notes = diagnosis_notes
    ticket.diagnosed_at = datetime.now(UTC)
    ticket.diagnosed_by = user_id
    db.commit()
    db.refresh(ticket)
    return ticket


def estimate_ticket(
    db: Session, ticket_id: uuid.UUID, user_id: uuid.UUID, role: str, estimated_cost: float
) -> MaintenanceTicket:
    ticket = get_ticket(db, ticket_id)
    _require_owner_or_admin(db, ticket, user_id, role)

    if ticket.status != TicketStatus.DIAGNOSED:
        raise InvalidTicketTransitionError

    now = datetime.now(UTC)
    ticket.estimated_cost = estimated_cost
    ticket.estimated_at = now
    ticket.estimated_by = user_id

    property_ = db.get(Property, ticket.property_id)

    # A value breach (Phase 6c) always requires an explicit approve call,
    # even from the property owner -- it's no longer a routine self-quote
    # within the owner's plan entitlement. A frequency breach flagged
    # earlier at creation is untouched by this check.
    service_category = db.execute(
        select(ServiceCategory).where(ServiceCategory.name == ticket.category)
    ).scalar_one_or_none()
    if service_category is not None and property_ is not None:
        owner_package = _owner_package_for_property(db, property_.id)
        rule = _resolve_eligibility_rule(db, service_category.id, owner_package)
        if rule is not None and rule.max_value is not None and estimated_cost > rule.max_value:
            ticket.fair_use_breached = True

    is_owner_of_property = role == "owner" and property_ is not None and property_.owner_id == user_id
    if is_owner_of_property and not ticket.fair_use_breached:
        # No one else to approve from — the owner quoting their own
        # ticket is self-evidently approved, same as create_expense's
        # owner-auto-approve branch.
        ticket.status = TicketStatus.APPROVED
        ticket.approved_at = now
        ticket.approved_by = user_id
    else:
        ticket.status = TicketStatus.ESTIMATED

    db.commit()
    db.refresh(ticket)
    return ticket


def _require_property_owner(db: Session, ticket: MaintenanceTicket, user_id: uuid.UUID) -> None:
    property_ = db.get(Property, ticket.property_id)
    if property_ is None:
        raise PropertyNotFoundError
    if property_.owner_id != user_id:
        raise NotPropertyOwnerError


def approve_ticket(db: Session, ticket_id: uuid.UUID, user_id: uuid.UUID, role: str) -> MaintenanceTicket:
    ticket = get_ticket(db, ticket_id)
    _require_property_owner(db, ticket, user_id)

    if ticket.status != TicketStatus.ESTIMATED:
        raise InvalidTicketTransitionError

    ticket.status = TicketStatus.APPROVED
    ticket.approved_at = datetime.now(UTC)
    ticket.approved_by = user_id
    db.commit()
    db.refresh(ticket)
    return ticket


def reject_estimate_ticket(db: Session, ticket_id: uuid.UUID, user_id: uuid.UUID, role: str) -> MaintenanceTicket:
    ticket = get_ticket(db, ticket_id)
    _require_property_owner(db, ticket, user_id)

    if ticket.status != TicketStatus.ESTIMATED:
        raise InvalidTicketTransitionError

    ticket.status = TicketStatus.OPEN
    db.commit()
    db.refresh(ticket)
    return ticket


def create_checklist_template(db: Session, data: ChecklistTemplateIn) -> ChecklistTemplate:
    template = ChecklistTemplate(category=data.category, items=data.items)
    db.add(template)
    db.commit()
    db.refresh(template)
    return template


def list_checklist_templates(db: Session) -> list[ChecklistTemplate]:
    return list(db.execute(select(ChecklistTemplate).order_by(ChecklistTemplate.category)).scalars())


def update_checklist_template(
    db: Session, template_id: uuid.UUID, data: ChecklistTemplateUpdate
) -> ChecklistTemplate:
    template = db.get(ChecklistTemplate, template_id)
    if template is None:
        raise ChecklistTemplateNotFoundError
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(template, field, value)
    db.commit()
    db.refresh(template)
    return template


def create_service_category(db: Session, data: ServiceCategoryIn) -> ServiceCategory:
    category = ServiceCategory(**data.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def list_service_categories(db: Session, active_only: bool) -> list[ServiceCategory]:
    stmt = select(ServiceCategory)
    if active_only:
        stmt = stmt.where(ServiceCategory.is_active.is_(True))
    return list(db.execute(stmt.order_by(ServiceCategory.name)).scalars())


def update_service_category(
    db: Session, category_id: uuid.UUID, data: ServiceCategoryUpdate
) -> ServiceCategory:
    category = db.get(ServiceCategory, category_id)
    if category is None:
        raise ServiceCategoryNotFoundError
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(category, field, value)
    db.commit()
    db.refresh(category)
    return category


def create_eligibility_rule(db: Session, data: ServiceEligibilityRuleIn) -> ServiceEligibilityRule:
    rule = ServiceEligibilityRule(**data.model_dump())
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


def list_eligibility_rules(
    db: Session, service_category_id: uuid.UUID | None
) -> list[ServiceEligibilityRule]:
    stmt = select(ServiceEligibilityRule)
    if service_category_id is not None:
        stmt = stmt.where(ServiceEligibilityRule.service_category_id == service_category_id)
    return list(db.execute(stmt).scalars())


def update_eligibility_rule(
    db: Session, rule_id: uuid.UUID, data: ServiceEligibilityRuleUpdate
) -> ServiceEligibilityRule:
    rule = db.get(ServiceEligibilityRule, rule_id)
    if rule is None:
        raise ServiceEligibilityRuleNotFoundError
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(rule, field, value)
    db.commit()
    db.refresh(rule)
    return rule


def delete_eligibility_rule(db: Session, rule_id: uuid.UUID) -> None:
    rule = db.get(ServiceEligibilityRule, rule_id)
    if rule is None:
        raise ServiceEligibilityRuleNotFoundError
    db.delete(rule)
    db.commit()


def update_checklist_item(
    db: Session, ticket_id: uuid.UUID, user_id: uuid.UUID, role: str, item: str, checked: bool
) -> MaintenanceTicket:
    ticket = get_ticket(db, ticket_id)
    if role not in ("admin",) and ticket.assigned_to != user_id:
        _require_owner_or_admin(db, ticket, user_id, role)

    if ticket.checklist is None:
        raise NoChecklistError
    if item not in ticket.checklist:
        raise ChecklistItemNotFoundError

    checklist = dict(ticket.checklist)
    checklist[item] = checked
    ticket.checklist = checklist
    db.commit()
    db.refresh(ticket)
    return ticket


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

    if ticket.status not in (TicketStatus.OPEN, TicketStatus.APPROVED, TicketStatus.ASSIGNED):
        raise InvalidTicketTransitionError
    # A ticket needing escalation can't take the direct open->assigned
    # shortcut — it has to go through 5a's diagnose->estimate->approve
    # chain first. APPROVED/ASSIGNED are unaffected, so a ticket that
    # already went through that chain assigns exactly as it does today.
    # A fair-use breach (Phase 6c) is treated the same way as an escalate
    # rule for this guard — either reason forces the same approval gate.
    needs_escalation = ticket.eligibility_outcome == EligibilityOutcome.ESCALATE or ticket.fair_use_breached
    if needs_escalation and ticket.status == TicketStatus.OPEN:
        raise EscalationApprovalRequiredError
    if (assigned_to is None) == (assigned_vendor_id is None):
        raise InvalidAssigneeError

    if assigned_to is not None:
        if get_user_role(db, assigned_to) != "field_staff":
            raise InvalidAssigneeError
        if ticket.eligibility_outcome == EligibilityOutcome.THIRD_PARTY:
            raise ThirdPartyRequiredError
        ticket.assigned_to = assigned_to
        ticket.assigned_vendor_id = None
    else:
        vendor = db.get(Vendor, assigned_vendor_id)
        if vendor is None or not vendor.is_active:
            raise InvalidAssigneeError
        ticket.assigned_vendor_id = assigned_vendor_id
        ticket.assigned_to = None

    # Auto-attach the SOP checklist for this category, if one exists.
    # Absence is normal — most categories won't have one, and that's
    # what keeps the resolve-time quality gate optional.
    template = db.execute(
        select(ChecklistTemplate).where(
            ChecklistTemplate.category == ticket.category, ChecklistTemplate.is_active.is_(True)
        )
    ).scalar_one_or_none()
    if template is not None:
        ticket.checklist = {item: False for item in template.items}

    ticket.status = TicketStatus.ASSIGNED
    db.commit()
    db.refresh(ticket)
    return ticket


def start_ticket(
    db: Session,
    ticket_id: uuid.UUID,
    user_id: uuid.UUID,
    role: str,
    latitude: float | None = None,
    longitude: float | None = None,
) -> MaintenanceTicket:
    ticket = get_ticket(db, ticket_id)
    if role not in ("admin",) and ticket.assigned_to != user_id:
        _require_owner_or_admin(db, ticket, user_id, role)

    if ticket.status != TicketStatus.ASSIGNED:
        raise InvalidTicketTransitionError

    ticket.status = TicketStatus.IN_PROGRESS
    ticket.check_in_at = datetime.now(UTC)
    ticket.check_in_latitude = latitude
    ticket.check_in_longitude = longitude
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

    if ticket.checklist is not None and not all(ticket.checklist.values()):
        raise ChecklistIncompleteError

    after_photos = list_documents(db, "ticket", ticket.id)
    if ticket.checklist is not None and not any(d.document_type == "after_photo" for d in after_photos):
        raise MissingEvidenceError

    ticket.status = TicketStatus.RESOLVED
    ticket.resolution_notes = data.resolution_notes
    ticket.check_out_at = datetime.now(UTC)
    ticket.check_out_latitude = data.latitude
    ticket.check_out_longitude = data.longitude
    db.commit()
    db.refresh(ticket)
    return ticket


def close_ticket(
    db: Session, ticket_id: uuid.UUID, user_id: uuid.UUID, role: str, warranty_days: int | None = None
) -> MaintenanceTicket:
    ticket = get_ticket(db, ticket_id)
    _require_owner_or_admin(db, ticket, user_id, role)

    if ticket.status != TicketStatus.RESOLVED:
        raise InvalidTicketTransitionError

    ticket.status = TicketStatus.CLOSED
    ticket.closed_at = datetime.now(UTC)
    if warranty_days is not None:
        ticket.warranty_expires_on = ticket.closed_at.date() + timedelta(days=warranty_days)
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
    ticket.rework_count += 1
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


def get_maintenance_summary(db: Session, property_ids: list[uuid.UUID] | None) -> MaintenanceSummaryOut:
    """Aggregate ticket/cost stats for the reports endpoint.

    `property_ids=None` means "all properties" (admin, no scope). Same
    read-time-aggregation approach as finance/service.py's _summarize —
    a report endpoint, not a new denormalized analytics table.
    """
    ticket_stmt = select(MaintenanceTicket)
    if property_ids is not None:
        ticket_stmt = ticket_stmt.where(MaintenanceTicket.property_id.in_(property_ids))
    tickets = list(db.execute(ticket_stmt).scalars())

    today = datetime.now(UTC).date()
    with_estimate = [t for t in tickets if t.estimated_cost is not None]
    total_estimated_cost = sum(t.estimated_cost for t in with_estimate if t.estimated_cost is not None)

    ticket_ids = [t.id for t in tickets]
    total_actual_cost = 0.0
    if ticket_ids:
        total_actual_cost = db.execute(
            select(func.coalesce(func.sum(Expense.amount), 0.0)).where(Expense.ticket_id.in_(ticket_ids))
        ).scalar_one()

    return MaintenanceSummaryOut(
        total_tickets=len(tickets),
        closed_tickets=sum(1 for t in tickets if t.status == TicketStatus.CLOSED),
        repeat_failure_count=sum(1 for t in tickets if t.is_repeat_failure),
        active_warranty_count=sum(
            1 for t in tickets if t.warranty_expires_on is not None and t.warranty_expires_on >= today
        ),
        tickets_with_estimate=len(with_estimate),
        total_estimated_cost=total_estimated_cost,
        total_actual_cost=total_actual_cost,
        cost_variance=total_actual_cost - total_estimated_cost,
    )
