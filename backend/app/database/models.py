import uuid
from typing import List, Optional, Any, Dict
from sqlalchemy import String, Text, ForeignKey, Integer, JSON, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid

from app.database.base import Base, UUIDPrimaryKeyMixin, TimestampMixin


class User(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    User model representing registered system users or clients.
    One User has many Sessions.
    """
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Relationships
    sessions: Mapped[List["Session"]] = relationship(
        "Session",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="Session.created_at.desc()"
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email}>"


class Session(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Session model representing a conversation or task context.
    Belongs to one User, has many Messages and Artifacts.
    """
    __tablename__ = "sessions"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="sessions")
    messages: Mapped[List["Message"]] = relationship(
        "Message",
        back_populates="session",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="Message.created_at.asc()"
    )
    artifacts: Mapped[List["Artifact"]] = relationship(
        "Artifact",
        back_populates="session",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="Artifact.created_at.desc()"
    )

    __table_args__ = (
        Index("ix_sessions_user_created", "user_id", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<Session id={self.id} user_id={self.user_id} title={self.title}>"


class Message(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Message model representing user/assistant interaction messages in a session.
    Belongs to one Session.
    """
    __tablename__ = "messages"

    session_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    role: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    # Relationships
    session: Mapped["Session"] = relationship("Session", back_populates="messages")

    __table_args__ = (
        Index("ix_messages_session_created", "session_id", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<Message id={self.id} session_id={self.session_id} role={self.role}>"


class Artifact(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Artifact model representing generated documents, code outputs, or reports tied to a session.
    Belongs to one Session.
    """
    __tablename__ = "artifacts"

    session_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    artifact_type: Mapped[str] = mapped_column(String(100), nullable=False, default="document")
    content: Mapped[str] = mapped_column(Text, nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    # Relationships
    session: Mapped["Session"] = relationship("Session", back_populates="artifacts")

    __table_args__ = (
        Index("ix_artifacts_session_title", "session_id", "title"),
    )

    def __repr__(self) -> str:
        return f"<Artifact id={self.id} session_id={self.session_id} title={self.title} version={self.version}>"
