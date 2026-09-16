import uuid

from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, uuid_pk


class Vendor(Base, TimestampMixin):
    """An external service provider Mokman ops assigns ticket work to.

    Not a `User` — vendors don't log in (internal resource model per the
    phase-wise plan, not a marketplace); admin manages this directory on
    their behalf. `is_active` doubles as this pass's lightweight blacklist
    toggle; a formal blacklist workflow (reason, history) is deferred.
    """

    __tablename__ = "vendors"

    id: Mapped[uuid.UUID] = uuid_pk()
    name: Mapped[str] = mapped_column(String(255))
    service_category: Mapped[str] = mapped_column(String(100))
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    gst_number: Mapped[str | None] = mapped_column(String(20), nullable=True)
    pan_number: Mapped[str | None] = mapped_column(String(20), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
