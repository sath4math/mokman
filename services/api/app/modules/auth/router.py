from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.modules.auth.dependencies import CurrentUser, get_current_user
from app.modules.auth.schemas import LoginRequest, RegisterRequest, TokenResponse, UserOut
from app.modules.auth.security import create_access_token
from app.modules.auth.service import (
    EmailAlreadyRegisteredError,
    UnknownRoleError,
    authenticate_user,
    get_user_role,
    register_user,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(data: RegisterRequest, db: Session = Depends(get_db)) -> TokenResponse:
    try:
        user = register_user(db, data)
    except EmailAlreadyRegisteredError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered") from None
    except UnknownRoleError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unknown role") from None

    token = create_access_token(user.id, data.role)
    return TokenResponse(access_token=token, role=data.role)


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user = authenticate_user(db, data.email, data.password)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")

    role = get_user_role(db, user.id)
    if role is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No role assigned to this account")

    token = create_access_token(user.id, role)
    return TokenResponse(access_token=token, role=role)


@router.get("/me", response_model=UserOut)
def me(current: CurrentUser = Depends(get_current_user)) -> UserOut:
    return UserOut(
        id=current.user.id,
        email=current.user.email,
        full_name=current.user.full_name,
        role=current.role,
    )
