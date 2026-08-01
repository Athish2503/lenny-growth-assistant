import uuid
from datetime import datetime
from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.types import Uuid


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy 2.0 declarative models in Lenny Growth Assistant.
    """
    pass


class UUIDPrimaryKeyMixin:
    """
    Mixin providing a UUID primary key for database models.
    Generates client-side UUID4 by default while allowing DB-level primary keys.
    """
    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False
    )


class TimestampMixin:
    """
    Mixin providing timezone-aware created_at and updated_at timestamps.
    Automatically managed on creation and update via server defaults and onupdate callbacks.
    """
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
