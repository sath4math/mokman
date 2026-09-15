import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


def str_enum_column[E: enum.Enum](enum_cls: type[E], name: str) -> SAEnum:
    """A Postgres ENUM column type that stores the member's .value.

    SQLAlchemy's Enum type stores the Python enum member's .name by default,
    but our (str, Enum) members' values are what migrations create the
    Postgres type with — without values_callable, inserts fail with
    "invalid input value for enum ...: 'MEMBER_NAME'".
    """
    return SAEnum(enum_cls, name=name, values_callable=lambda obj: [e.value for e in obj])


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


def uuid_pk() -> Mapped[uuid.UUID]:
    return mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
