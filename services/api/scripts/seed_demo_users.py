"""Seed the demo Admin and Field Staff accounts (idempotent).

These two roles are internally provisioned in the real product (no public
self-registration), so this script stands in for that provisioning during
local development. Run with: uv run python scripts/seed_demo_users.py
"""

from sqlalchemy import select

from app.database import SessionLocal
from app.models.rbac import Role, RoleAssignment
from app.models.user import User
from app.modules.auth.security import hash_password

DEMO_ACCOUNTS = [
    ("admin@mokman.com", "admin", "Mokman Admin"),
    ("field@mokman.com", "field_staff", "Mokman Field Staff"),
]
DEMO_PASSWORD = "ChangeMe123!"


def seed() -> None:
    with SessionLocal() as db:
        for email, role_name, full_name in DEMO_ACCOUNTS:
            if db.execute(select(User).where(User.email == email)).scalar_one_or_none():
                print(f"skip (exists): {email}")
                continue

            role = db.execute(select(Role).where(Role.name == role_name)).scalar_one_or_none()
            if role is None:
                raise RuntimeError(f"Role '{role_name}' not found — run migrations first.")

            user = User(email=email, full_name=full_name, hashed_password=hash_password(DEMO_PASSWORD))
            db.add(user)
            db.flush()
            db.add(RoleAssignment(user_id=user.id, role_id=role.id, property_id=None))
            db.commit()
            print(f"created: {email} / {DEMO_PASSWORD}")


if __name__ == "__main__":
    seed()
