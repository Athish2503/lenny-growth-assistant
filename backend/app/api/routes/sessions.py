from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session as DbSession

from app.database.session import get_db
from app.repositories.session_repository import SessionRepository
from app.schemas.session import SessionCreate, SessionResponse, SessionUpdate
from app.services.session_service import SessionService

router = APIRouter(prefix="/sessions", tags=["sessions"])


def get_session_service(db: DbSession = Depends(get_db)) -> SessionService:
    repo = SessionRepository(db)
    return SessionService(repo)


@router.post("", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
def create_session(
    payload: SessionCreate,
    service: SessionService = Depends(get_session_service),
):
    """
    Create a new session context.
    """
    return service.create_session(user_id=payload.user_id, title=payload.title)


@router.get("", response_model=List[SessionResponse])
def get_sessions(
    user_id: Optional[UUID] = Query(None, description="Filter sessions by user ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    service: SessionService = Depends(get_session_service),
):
    """
    Retrieve all sessions, optionally filtered by user ID.
    """
    return service.list_sessions(user_id=user_id, skip=skip, limit=limit)


@router.get("/{id}", response_model=SessionResponse)
def get_session(
    id: UUID,
    service: SessionService = Depends(get_session_service),
):
    """
    Retrieve a session by ID.
    """
    session = service.get_session(id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
        )
    return session


@router.patch("/{id}", response_model=SessionResponse)
def update_session(
    id: UUID,
    payload: SessionUpdate,
    service: SessionService = Depends(get_session_service),
):
    """
    Update a session title by ID.
    """
    session = service.update_session(id, title=payload.title)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
        )
    return session


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(
    id: UUID,
    service: SessionService = Depends(get_session_service),
):
    """
    Delete a session by ID.
    """
    success = service.delete_session(id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
        )
    return None
