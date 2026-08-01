from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session as DbSession

from app.database.models import Message, Session


class MessageRepository:
    """
    Repository layer for Message operations using SQLAlchemy 2.0.
    """

    def __init__(self, db: DbSession):
        self.db = db

    def get_session_history(self, session_id: UUID) -> List[Message]:
        """
        Retrieves all messages for a session ordered chronologically by created_at.
        """
        stmt = (
            select(Message)
            .where(Message.session_id == session_id)
            .order_by(Message.created_at.asc())
        )
        return list(self.db.scalars(stmt).all())

    def create_message(
        self,
        session_id: UUID,
        role: str,
        content: str,
        metadata_json: Optional[dict] = None,
    ) -> Message:
        """
        Persists a new message in the database.
        """
        message = Message(
            session_id=session_id,
            role=role,
            content=content,
            metadata_json=metadata_json,
        )
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message
