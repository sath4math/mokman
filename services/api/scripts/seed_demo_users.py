"""Seed (or reset) the demo Admin and Field Staff accounts.

These two roles are internally provisioned in the real product (no public
self-registration), so this script stands in for that provisioning during
local development and initial deployment.

Passwords are randomly generated and printed once — never hardcoded, never
stored anywhere but the database (hashed). Save the printed output somewhere
safe; it will not be shown again.

Usage:
    uv run python scripts/seed_demo_users.py            # create if missing
    uv run python scripts/seed_demo_users.py --reset     # also rotate existing accounts' passwords
"""

import secrets
import sys

from sqlalchemy import select

from app.database import SessionLocal
from app.models.rbac import Role, RoleAssignment
from app.models.user import User
from app.modules.auth.security import hash_password

DEMO_ACCOUNTS = [
    ("admin@mokman.com", "admin", "Mokman Admin"),
    ("field@mokman.com", "field_staff", "Mokman Field Staff"),
]


def generate_password() -> str:
    return secrets.token_urlsafe(12)


def seed(reset: bool) -> None:
    with SessionLocal() as db:
        for email, role_name, full_name in DEMO_ACCOUNTS:
            existing = db.execute(select(User).where(User.email == email)).scalar_one_or_none()
            password = generate_password()

            if existing is not None:
                if not reset:
                    print(f"skip (exists, use --reset to rotate): {email}")
                    continue
                existing.hashed_password = hash_password(password)
                db.commit()
                print(f"reset: {email} / {password}")
                continue

            role = db.execute(select(Role).where(Role.name == role_name)).scalar_one_or_none()
            if role is None:
                raise RuntimeError(f"Role '{role_name}' not found — run migrations first.")

            user = User(email=email, full_name=full_name, hashed_password=hash_password(password))
            db.add(user)
            db.flush()
            db.add(RoleAssignment(user_id=user.id, role_id=role.id, property_id=None))
            db.commit()
            print(f"created: {email} / {password}")


if __name__ == "__main__":
    seed(reset="--reset" in sys.argv)
