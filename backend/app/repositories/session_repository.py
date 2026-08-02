from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session as DbSession

from app.database.models import Session, User


class SessionRepository:
    """
    Repository layer for Session database operations using SQLAlchemy 2.0.
    """

    def __init__(self, db: DbSession):
        self.db = db

    def create(self, user_id: UUID, title: Optional[str] = None) -> Session:
        # Guarantee user exists in database to satisfy FK constraint
        stmt = select(User).where(User.id == user_id)
        user = self.db.scalars(stmt).first()
        if not user:
            user = User(
                id=user_id,
                email=f"user_{str(user_id)[:8]}@lenny.ai",
                full_name="Growth Analyst User"
            )
            self.db.add(user)
            self.db.commit()

        session = Session(user_id=user_id, title=title)
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def get_by_id(self, session_id: UUID) -> Optional[Session]:
        stmt = select(Session).where(Session.id == session_id)
        return self.db.scalars(stmt).first()

    def get_all(
        self, user_id: Optional[UUID] = None, skip: int = 0, limit: int = 100
    ) -> List[Session]:
        stmt = select(Session)
        if user_id is not None:
            stmt = stmt.where(Session.user_id == user_id)
        stmt = stmt.order_by(Session.created_at.desc()).offset(skip).limit(limit)
        return list(self.db.scalars(stmt).all())

    def update(self, session_id: UUID, title: Optional[str] = None) -> Optional[Session]:
        session = self.get_by_id(session_id)
        if not session:
            return None
        if title is not None:
            session.title = title
        self.db.commit()
        self.db.refresh(session)
        return session

    def delete(self, session_id: UUID) -> bool:
        session = self.get_by_id(session_id)
        if not session:
            return False
        self.db.delete(session)
        self.db.commit()
        return True
