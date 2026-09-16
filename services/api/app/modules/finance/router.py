import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.modules.auth.dependencies import CurrentUser, get_current_user
from app.modules.finance.schemas import ExpenseAnomalyOut, PropertyProfitabilityOut, StatementOut
from app.modules.finance.service import (
    compare_profitability,
    default_year_month,
    detect_expense_anomalies,
    get_owner_statement,
    get_property_statement,
)
from app.modules.properties.service import PropertyNotFoundError, get_owned_property

router = APIRouter(prefix="/finance", tags=["finance"])


def _parse_month(month: str | None) -> tuple[int, int]:
    if month is None:
        return default_year_month()
    try:
        year_str, month_str = month.split("-")
        return int(year_str), int(month_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="month must be formatted YYYY-MM"
        ) from None


@router.get("/statement", response_model=StatementOut)
def statement(
    property_id: uuid.UUID | None = None,
    month: str | None = Query(default=None),
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StatementOut:
    year, month_num = _parse_month(month)

    if property_id is not None:
        if current.role == "owner":
            try:
                get_owned_property(db, current.user.id, property_id)
            except PropertyNotFoundError:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found") from None
        elif current.role != "admin":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Owner or admin role required")
        return get_property_statement(db, property_id, year, month_num)

    if current.role != "owner":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="property_id is required")
    return get_owner_statement(db, current.user.id, year, month_num)


@router.get("/profitability", response_model=list[PropertyProfitabilityOut])
def profitability(
    month: str | None = Query(default=None),
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[PropertyProfitabilityOut]:
    if current.role != "owner":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Owner role required")
    year, month_num = _parse_month(month)
    return compare_profitability(db, current.user.id, year, month_num)


@router.get("/anomalies", response_model=list[ExpenseAnomalyOut])
def anomalies(
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ExpenseAnomalyOut]:
    if current.role != "owner":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Owner role required")
    return detect_expense_anomalies(db, current.user.id)
