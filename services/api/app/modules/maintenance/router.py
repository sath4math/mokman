import uuid

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.modules.auth.dependencies import CurrentUser, get_current_user
from app.modules.inspections.service import NotPartyToInspectionError
from app.modules.maintenance.schemas import (
    AssignRequest,
    ChecklistItemUpdate,
    ChecklistTemplateIn,
    ChecklistTemplateOut,
    ChecklistTemplateUpdate,
    CloseRequest,
    DiagnoseRequest,
    EstimateRequest,
    FieldStaffOut,
    MaintenanceSummaryOut,
    MaterialUsageIn,
    MaterialUsageOut,
    ResolveRequest,
    ServiceCategoryIn,
    ServiceCategoryOut,
    ServiceCategoryUpdate,
    ServiceEligibilityRuleIn,
    ServiceEligibilityRuleOut,
    ServiceEligibilityRuleUpdate,
    SlaCheckResult,
    StartRequest,
    TicketCreate,
    TicketOut,
)
from app.modules.maintenance.service import (
    ChecklistIncompleteError,
    ChecklistItemNotFoundError,
    ChecklistTemplateNotFoundError,
    EscalationApprovalRequiredError,
    InvalidAssigneeError,
    InvalidTicketTransitionError,
    MissingEvidenceError,
    NoChecklistError,
    NotPartyToTicketError,
    NotPropertyOwnerError,
    ServiceCategoryInactiveError,
    ServiceCategoryNotFoundError,
    ServiceEligibilityRuleNotFoundError,
    ThirdPartyRequiredError,
    TicketNotFoundError,
    approve_ticket,
    assign_ticket,
    close_ticket,
    create_checklist_template,
    create_eligibility_rule,
    create_service_category,
    create_ticket,
    delete_eligibility_rule,
    diagnose_ticket,
    estimate_ticket,
    get_maintenance_summary,
    get_ticket,
    list_checklist_templates,
    list_eligibility_rules,
    list_field_staff,
    list_material_usage,
    list_service_categories,
    list_tickets,
    log_material_usage,
    reject_estimate_ticket,
    reopen_ticket,
    require_ticket_access,
    resolve_ticket,
    run_sla_check,
    start_ticket,
    update_checklist_item,
    update_checklist_template,
    update_eligibility_rule,
    update_service_category,
)
from app.modules.properties.service import (
    PropertyNotFoundError,
    get_owned_property,
    list_properties_for_owner,
)

router = APIRouter(prefix="/maintenance", tags=["maintenance"])
internal_router = APIRouter(prefix="/internal/maintenance", tags=["internal"])


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
    except ServiceCategoryInactiveError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="This service category is not currently offered"
        ) from None
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


@router.post("/checklist-templates", response_model=ChecklistTemplateOut, status_code=status.HTTP_201_CREATED)
def create_template(
    data: ChecklistTemplateIn,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ChecklistTemplateOut:
    if current.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required")
    return ChecklistTemplateOut.model_validate(create_checklist_template(db, data))


@router.get("/checklist-templates", response_model=list[ChecklistTemplateOut])
def list_templates(
    current: CurrentUser = Depends(get_current_user), db: Session = Depends(get_db)
) -> list[ChecklistTemplateOut]:
    if current.role not in ("owner", "admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Owner or admin role required")
    return [ChecklistTemplateOut.model_validate(t) for t in list_checklist_templates(db)]


@router.patch("/checklist-templates/{template_id}", response_model=ChecklistTemplateOut)
def update_template(
    template_id: uuid.UUID,
    data: ChecklistTemplateUpdate,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ChecklistTemplateOut:
    if current.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required")
    try:
        template = update_checklist_template(db, template_id, data)
    except ChecklistTemplateNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Checklist template not found") from None
    return ChecklistTemplateOut.model_validate(template)


@router.post("/service-categories", response_model=ServiceCategoryOut, status_code=status.HTTP_201_CREATED)
def create_category(
    data: ServiceCategoryIn,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ServiceCategoryOut:
    if current.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required")
    return ServiceCategoryOut.model_validate(create_service_category(db, data))


@router.get("/service-categories", response_model=list[ServiceCategoryOut])
def list_categories(
    active_only: bool = False,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ServiceCategoryOut]:
    # Open to any authenticated role, unlike checklist-templates/vendors —
    # tenants raise tickets too and need this to populate their own
    # category picker.
    return [ServiceCategoryOut.model_validate(c) for c in list_service_categories(db, active_only)]


@router.patch("/service-categories/{category_id}", response_model=ServiceCategoryOut)
def update_category(
    category_id: uuid.UUID,
    data: ServiceCategoryUpdate,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ServiceCategoryOut:
    if current.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required")
    try:
        category = update_service_category(db, category_id, data)
    except ServiceCategoryNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service category not found") from None
    return ServiceCategoryOut.model_validate(category)


@router.post("/eligibility-rules", response_model=ServiceEligibilityRuleOut, status_code=status.HTTP_201_CREATED)
def create_rule(
    data: ServiceEligibilityRuleIn,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ServiceEligibilityRuleOut:
    if current.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required")
    return ServiceEligibilityRuleOut.model_validate(create_eligibility_rule(db, data))


@router.get("/eligibility-rules", response_model=list[ServiceEligibilityRuleOut])
def list_rules(
    service_category_id: uuid.UUID | None = None,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ServiceEligibilityRuleOut]:
    if current.role not in ("owner", "admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Owner or admin role required")
    return [ServiceEligibilityRuleOut.model_validate(r) for r in list_eligibility_rules(db, service_category_id)]


@router.patch("/eligibility-rules/{rule_id}", response_model=ServiceEligibilityRuleOut)
def update_rule(
    rule_id: uuid.UUID,
    data: ServiceEligibilityRuleUpdate,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ServiceEligibilityRuleOut:
    if current.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required")
    try:
        rule = update_eligibility_rule(db, rule_id, data)
    except ServiceEligibilityRuleNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Eligibility rule not found") from None
    return ServiceEligibilityRuleOut.model_validate(rule)


@router.delete("/eligibility-rules/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_rule(
    rule_id: uuid.UUID,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    if current.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required")
    try:
        delete_eligibility_rule(db, rule_id)
    except ServiceEligibilityRuleNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Eligibility rule not found") from None


@router.post("/tickets/{ticket_id}/checklist-item", response_model=TicketOut)
def toggle_checklist_item(
    ticket_id: uuid.UUID,
    data: ChecklistItemUpdate,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TicketOut:
    try:
        ticket = update_checklist_item(db, ticket_id, current.user.id, current.role, data.item, data.checked)
    except TicketNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found") from None
    except PropertyNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found") from None
    except NotPartyToTicketError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Only the assignee, owner, or admin can update the checklist"
        ) from None
    except NoChecklistError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="This ticket has no checklist") from None
    except ChecklistItemNotFoundError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unknown checklist item") from None
    return TicketOut.model_validate(ticket)


@router.post("/tickets/{ticket_id}/diagnose", response_model=TicketOut)
def diagnose(
    ticket_id: uuid.UUID,
    data: DiagnoseRequest,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TicketOut:
    try:
        ticket = diagnose_ticket(db, ticket_id, current.user.id, current.role, data.diagnosis_notes)
    except TicketNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found") from None
    except PropertyNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found") from None
    except NotPartyToTicketError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Owner or admin role required") from None
    except InvalidTicketTransitionError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Ticket must be open to record a diagnosis"
        ) from None
    return TicketOut.model_validate(ticket)


@router.post("/tickets/{ticket_id}/estimate", response_model=TicketOut)
def estimate(
    ticket_id: uuid.UUID,
    data: EstimateRequest,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TicketOut:
    try:
        ticket = estimate_ticket(db, ticket_id, current.user.id, current.role, data.estimated_cost)
    except TicketNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found") from None
    except PropertyNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found") from None
    except NotPartyToTicketError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Owner or admin role required") from None
    except InvalidTicketTransitionError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Ticket must be diagnosed before estimating"
        ) from None
    return TicketOut.model_validate(ticket)


@router.post("/tickets/{ticket_id}/approve", response_model=TicketOut)
def approve(
    ticket_id: uuid.UUID,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TicketOut:
    try:
        ticket = approve_ticket(db, ticket_id, current.user.id, current.role)
    except TicketNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found") from None
    except PropertyNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found") from None
    except NotPropertyOwnerError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the property owner can approve") from None
    except InvalidTicketTransitionError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Ticket must have a pending estimate to approve"
        ) from None
    return TicketOut.model_validate(ticket)


@router.post("/tickets/{ticket_id}/reject-estimate", response_model=TicketOut)
def reject_estimate(
    ticket_id: uuid.UUID,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TicketOut:
    try:
        ticket = reject_estimate_ticket(db, ticket_id, current.user.id, current.role)
    except TicketNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found") from None
    except PropertyNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found") from None
    except NotPropertyOwnerError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the property owner can reject") from None
    except InvalidTicketTransitionError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Ticket must have a pending estimate to reject"
        ) from None
    return TicketOut.model_validate(ticket)


@router.post("/tickets/{ticket_id}/assign", response_model=TicketOut)
def assign(
    ticket_id: uuid.UUID,
    data: AssignRequest,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TicketOut:
    try:
        ticket = assign_ticket(
            db, ticket_id, current.user.id, current.role, data.assigned_to, data.assigned_vendor_id
        )
    except TicketNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found") from None
    except PropertyNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found") from None
    except NotPartyToTicketError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Owner or admin role required") from None
    except InvalidAssigneeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide exactly one of assigned_to (a field_staff account) "
            "or assigned_vendor_id (an active vendor)",
        ) from None
    except InvalidTicketTransitionError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Ticket cannot be assigned in its current status"
        ) from None
    except EscalationApprovalRequiredError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This ticket requires owner approval before assignment — diagnose, estimate, and approve it first",
        ) from None
    except ThirdPartyRequiredError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This service must be assigned to a vendor, not internal field staff, under the owner's plan",
        ) from None
    return TicketOut.model_validate(ticket)


@router.post("/tickets/{ticket_id}/start", response_model=TicketOut)
def start(
    ticket_id: uuid.UUID,
    data: StartRequest = StartRequest(),
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TicketOut:
    try:
        ticket = start_ticket(db, ticket_id, current.user.id, current.role, data.latitude, data.longitude)
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
    except ChecklistIncompleteError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="All checklist items must be checked before resolving"
        ) from None
    except MissingEvidenceError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An after_photo document must be uploaded before resolving",
        ) from None
    return TicketOut.model_validate(ticket)


@router.post(
    "/tickets/{ticket_id}/materials", response_model=MaterialUsageOut, status_code=status.HTTP_201_CREATED
)
def log_materials(
    ticket_id: uuid.UUID,
    data: MaterialUsageIn,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MaterialUsageOut:
    try:
        usage = log_material_usage(db, ticket_id, current.user.id, current.role, data)
    except TicketNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found") from None
    except PropertyNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found") from None
    except NotPartyToTicketError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Only the assignee, owner, or admin can log materials"
        ) from None
    return MaterialUsageOut.model_validate(usage)


@router.get("/tickets/{ticket_id}/materials", response_model=list[MaterialUsageOut])
def list_materials(
    ticket_id: uuid.UUID,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[MaterialUsageOut]:
    try:
        ticket = get_ticket(db, ticket_id)
        require_ticket_access(db, ticket, current.user.id, current.role)
    except TicketNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found") from None
    except NotPartyToTicketError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a party to this ticket") from None
    return [MaterialUsageOut.model_validate(m) for m in list_material_usage(db, ticket_id)]


@router.post("/tickets/{ticket_id}/close", response_model=TicketOut)
def close(
    ticket_id: uuid.UUID,
    data: CloseRequest = CloseRequest(),
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TicketOut:
    try:
        ticket = close_ticket(db, ticket_id, current.user.id, current.role, data.warranty_days)
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


@router.get("/reports/summary", response_model=MaintenanceSummaryOut)
def maintenance_summary(
    property_id: uuid.UUID | None = None,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MaintenanceSummaryOut:
    if current.role not in ("owner", "admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Owner or admin role required")

    property_ids: list[uuid.UUID] | None
    if property_id is not None:
        if current.role == "owner":
            try:
                get_owned_property(db, current.user.id, property_id)
            except PropertyNotFoundError:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found") from None
        property_ids = [property_id]
    elif current.role == "owner":
        property_ids = [p.id for p in list_properties_for_owner(db, current.user.id)]
    else:
        property_ids = None

    return get_maintenance_summary(db, property_ids)


@internal_router.post("/sla-check", response_model=SlaCheckResult)
def sla_check(
    db: Session = Depends(get_db),
    x_cron_secret: str | None = Header(default=None),
) -> SlaCheckResult:
    if not x_cron_secret or x_cron_secret != settings.sla_cron_secret:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid cron secret")
    return SlaCheckResult(breached_ticket_ids=run_sla_check(db))
