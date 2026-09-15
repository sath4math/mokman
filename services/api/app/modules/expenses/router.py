import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.modules.auth.dependencies import CurrentUser, get_current_user
from app.modules.expenses.schemas import ExpenseCreate, ExpenseOut
from app.modules.expenses.service import (
    ExpenseNotFoundError,
    NotPropertyOwnerError,
    approve_expense,
    create_expense,
    list_expenses,
    reject_expense,
)
from app.modules.properties.service import PropertyNotFoundError

router = APIRouter(prefix="/expenses", tags=["expenses"])


@router.post("", response_model=ExpenseOut, status_code=status.HTTP_201_CREATED)
def create(
    data: ExpenseCreate,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ExpenseOut:
    if current.role not in ("owner", "admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Owner or admin role required")
    try:
        expense = create_expense(db, current.user.id, current.role, data)
    except PropertyNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found") from None
    except NotPropertyOwnerError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not the owner of this property") from None
    return ExpenseOut.model_validate(expense)


@router.get("", response_model=list[ExpenseOut])
def list_for_property(
    property_id: uuid.UUID | None = None,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ExpenseOut]:
    if property_id is None:
        if current.role != "admin":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="property_id is required")
    elif current.role not in ("owner", "admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Owner or admin role required")
    return [ExpenseOut.model_validate(e) for e in list_expenses(db, property_id)]


@router.post("/{expense_id}/approve", response_model=ExpenseOut)
def approve(
    expense_id: uuid.UUID,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ExpenseOut:
    try:
        expense = approve_expense(db, expense_id, current.user.id)
    except ExpenseNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found") from None
    except PropertyNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found") from None
    except NotPropertyOwnerError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not the owner of this property") from None
    return ExpenseOut.model_validate(expense)


@router.post("/{expense_id}/reject", response_model=ExpenseOut)
def reject(
    expense_id: uuid.UUID,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ExpenseOut:
    try:
        expense = reject_expense(db, expense_id, current.user.id)
    except ExpenseNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found") from None
    except PropertyNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found") from None
    except NotPropertyOwnerError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not the owner of this property") from None
    return ExpenseOut.model_validate(expense)
