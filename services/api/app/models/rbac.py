import uuid

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, uuid_pk


class Role(Base, TimestampMixin):
    """A named role: owner, tenant, field_staff, admin (extended per-phase)."""

    __tablename__ = "roles"

    id: Mapped[uuid.UUID] = uuid_pk()
    name: Mapped[str] = mapped_column(String(50), unique=True)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)


class Permission(Base, TimestampMixin):
    """A single grantable action, e.g. 'property:read', 'ledger:approve'."""

    __tablename__ = "permissions"

    id: Mapped[uuid.UUID] = uuid_pk()
    code: Mapped[str] = mapped_column(String(100), unique=True)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)


class RoleAssignment(Base, TimestampMixin):
    """Grants a role to a user, optionally scoped to one property.

    A null property_id means the role applies platform-wide (e.g. admin).
    A non-null property_id is how owner/tenant/field-staff data isolation
    is enforced: a query is always filtered by the caller's assignments.
    """

    __tablename__ = "role_assignments"

    id: Mapped[uuid.UUID] = uuid_pk()
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    role_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("roles.id"))
    property_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("properties.id"), nullable=True, index=True
    )
