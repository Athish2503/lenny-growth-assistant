from typing import List, Optional
from uuid import UUID

from app.database.models import Session
from app.repositories.session_repository import SessionRepository


class SessionService:
    """
    Service layer for Session domain logic.
    """

    def __init__(self, session_repo: SessionRepository):
        self.session_repo = session_repo

    def create_session(self, user_id: UUID, title: Optional[str] = None) -> Session:
        return self.session_repo.create(user_id=user_id, title=title)

    def get_session(self, session_id: UUID) -> Optional[Session]:
        return self.session_repo.get_by_id(session_id)

    def list_sessions(
        self, user_id: Optional[UUID] = None, skip: int = 0, limit: int = 100
    ) -> List[Session]:
        return self.session_repo.get_all(user_id=user_id, skip=skip, limit=limit)

    def update_session(self, session_id: UUID, title: Optional[str] = None) -> Optional[Session]:
        return self.session_repo.update(session_id=session_id, title=title)

    def delete_session(self, session_id: UUID) -> bool:
        return self.session_repo.delete(session_id)
