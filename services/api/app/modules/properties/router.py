import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.modules.auth.dependencies import CurrentUser, get_current_user
from app.modules.inspections.service import NotPartyToInspectionError, verify_property_access
from app.modules.properties.schemas import (
    InvestmentSummaryOut,
    PropertyCreate,
    PropertyHealthScoreOut,
    PropertyOut,
    PropertyUpdate,
    SaleReadinessOut,
)
from app.modules.properties.service import (
    PropertyNotFoundError,
    compute_health_score,
    compute_investment_summary,
    compute_sale_readiness,
    create_property,
    get_owned_property,
    get_property_by_id,
    list_all_properties,
    list_investment_summaries,
    list_properties_for_owner,
    update_property,
    update_property_admin,
)

router = APIRouter(prefix="/properties", tags=["properties"])


def _require_owner(current: CurrentUser) -> None:
    if current.role != "owner":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Owner role required")


def _require_admin(current: CurrentUser) -> None:
    if current.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required")


@router.post("", response_model=PropertyOut, status_code=status.HTTP_201_CREATED)
def create(
    data: PropertyCreate,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PropertyOut:
    _require_owner(current)
    return PropertyOut.model_validate(create_property(db, current.user.id, data))


@router.post("/on-behalf/{owner_id}", response_model=PropertyOut, status_code=status.HTTP_201_CREATED)
def create_on_behalf(
    owner_id: uuid.UUID,
    data: PropertyCreate,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PropertyOut:
    """Admin registers a property for an owner during onboarding, when the
    owner has provided the details/photos but isn't entering them
    themselves."""
    _require_admin(current)
    return PropertyOut.model_validate(create_property(db, owner_id, data))


@router.get("", response_model=list[PropertyOut])
def list_mine(
    owner_id: uuid.UUID | None = None,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[PropertyOut]:
    if current.role == "admin":
        # Admin on-behalf-of screen filters to one owner; the global
        # admin property list (no filter) is unchanged.
        if owner_id is not None:
            return [PropertyOut.model_validate(p) for p in list_properties_for_owner(db, owner_id)]
        return [PropertyOut.model_validate(p) for p in list_all_properties(db)]
    _require_owner(current)
    return [PropertyOut.model_validate(p) for p in list_properties_for_owner(db, current.user.id)]


@router.get("/investment-portfolio", response_model=list[InvestmentSummaryOut])
def investment_portfolio(
    current: CurrentUser = Depends(get_current_user), db: Session = Depends(get_db)
) -> list[InvestmentSummaryOut]:
    _require_owner(current)
    return list_investment_summaries(db, current.user.id)


@router.get("/{property_id}", response_model=PropertyOut)
def read(
    property_id: uuid.UUID,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PropertyOut:
    try:
        if current.role == "admin":
            return PropertyOut.model_validate(get_property_by_id(db, property_id))
        if current.role == "tenant":
            verify_property_access(db, property_id, current.user.id)
            return PropertyOut.model_validate(get_property_by_id(db, property_id))
        _require_owner(current)
        return PropertyOut.model_validate(get_owned_property(db, current.user.id, property_id))
    except PropertyNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found") from None
    except NotPartyToInspectionError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a party to this property") from None


@router.patch("/{property_id}", response_model=PropertyOut)
def update(
    property_id: uuid.UUID,
    data: PropertyUpdate,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PropertyOut:
    try:
        if current.role == "admin":
            return PropertyOut.model_validate(update_property_admin(db, property_id, data))
        _require_owner(current)
        return PropertyOut.model_validate(update_property(db, current.user.id, property_id, data))
    except PropertyNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found") from None


@router.get("/{property_id}/health-score", response_model=PropertyHealthScoreOut)
def health_score(
    property_id: uuid.UUID,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PropertyHealthScoreOut:
    try:
        if current.role == "admin":
            get_property_by_id(db, property_id)
        else:
            _require_owner(current)
            get_owned_property(db, current.user.id, property_id)
    except PropertyNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found") from None
    return compute_health_score(db, property_id)


@router.get("/{property_id}/investment-summary", response_model=InvestmentSummaryOut)
def investment_summary(
    property_id: uuid.UUID,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> InvestmentSummaryOut:
    try:
        if current.role == "admin":
            get_property_by_id(db, property_id)
        else:
            _require_owner(current)
            get_owned_property(db, current.user.id, property_id)
    except PropertyNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found") from None
    return compute_investment_summary(db, property_id)


@router.get("/{property_id}/sale-readiness", response_model=SaleReadinessOut)
def sale_readiness(
    property_id: uuid.UUID,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SaleReadinessOut:
    try:
        if current.role == "admin":
            get_property_by_id(db, property_id)
        else:
            _require_owner(current)
            get_owned_property(db, current.user.id, property_id)
    except PropertyNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found") from None
    return compute_sale_readiness(db, property_id)
