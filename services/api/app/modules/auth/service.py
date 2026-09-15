from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.rbac import Role, RoleAssignment
from app.models.user import User
from app.modules.auth.schemas import RegisterRequest
from app.modules.auth.security import hash_password, verify_password


class EmailAlreadyRegisteredError(Exception):
    pass


class UnknownRoleError(Exception):
    pass


def get_user_role(db: Session, user_id: object) -> str | None:
    row = (
        db.execute(
            select(Role.name)
            .join(RoleAssignment, RoleAssignment.role_id == Role.id)
            .where(RoleAssignment.user_id == user_id)
        )
        .scalars()
        .first()
    )
    return row


def register_user(db: Session, data: RegisterRequest) -> User:
    existing = db.execute(select(User).where(User.email == data.email)).scalar_one_or_none()
    if existing is not None:
        raise EmailAlreadyRegisteredError

    role = db.execute(select(Role).where(Role.name == data.role)).scalar_one_or_none()
    if role is None:
        raise UnknownRoleError

    user = User(
        email=data.email,
        full_name=data.full_name,
        hashed_password=hash_password(data.password),
    )
    db.add(user)
    db.flush()

    db.add(RoleAssignment(user_id=user.id, role_id=role.id, property_id=None))
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = db.execute(select(User).where(User.email == email)).scalar_one_or_none()
    if user is None or not verify_password(password, user.hashed_password):
        return None
    return user
