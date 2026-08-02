import uuid
from typing import List, Optional, Any, Dict
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session as DbSession
from sqlalchemy import select

from app.database.session import get_db
from app.repositories.session_repository import SessionRepository
from app.repositories.message_repository import MessageRepository
from app.repositories.artifact_repository import ArtifactRepository
from app.database.models import Message, Artifact
from app.schemas.session import SessionCreate, SessionResponse, SessionUpdate
from app.services.session_service import SessionService

router = APIRouter(prefix="/sessions", tags=["sessions"])
artifacts_router = APIRouter(prefix="/artifacts", tags=["artifacts"])


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
    uid = payload.user_id or uuid.uuid4()
    return service.create_session(user_id=uid, title=payload.title)


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


@router.get("/{id}/messages")
def get_session_messages(
    id: UUID,
    db: DbSession = Depends(get_db),
):
    """
    Retrieve message history for a specific session.
    """
    message_repo = MessageRepository(db)
    messages = message_repo.get_session_history(id)
    result = []
    for msg in messages:
        metadata = msg.metadata_json or {}
        citations = metadata.get("citations") or metadata.get("sources") or []
        result.append({
            "id": str(msg.id),
            "session_id": str(msg.session_id),
            "role": msg.role,
            "content": msg.content,
            "created_at": msg.created_at.isoformat() if msg.created_at else "",
            "metadata": metadata,
            "citations": citations,
        })
    return result


@router.get("/{id}/messages/{message_id}/retrieval")
def get_message_retrieval(
    id: UUID,
    message_id: UUID,
    db: DbSession = Depends(get_db),
):
    """
    Retrieve retrieval details for a specific message.
    """
    stmt = select(Message).where(Message.id == message_id, Message.session_id == id)
    msg = db.scalars(stmt).first()
    if not msg or not msg.metadata_json:
        return {
            "chunks": [],
            "sources": [],
            "retrieval_time_ms": 0,
            "confidence_score": 0.0,
            "model": "",
            "provider": "ollama",
        }
    
    metadata = msg.metadata_json
    sources = metadata.get("citations") or metadata.get("sources") or []
    return {
        "chunks": metadata.get("retrieved_chunks", []),
        "sources": sources,
        "retrieval_time_ms": metadata.get("retrieval_time_ms", 0),
        "confidence_score": metadata.get("confidence_score", 0.85),
        "model": metadata.get("model", ""),
        "provider": metadata.get("provider", "ollama"),
        "tokens_used": metadata.get("tokens_used"),
    }


@router.get("/{id}/artifacts")
def get_session_artifacts(
    id: UUID,
    db: DbSession = Depends(get_db),
):
    """
    Retrieve artifacts generated for a session.
    """
    artifact_repo = ArtifactRepository(db)
    artifacts = artifact_repo.get_by_session(id)
    return [
        {
            "id": str(art.id),
            "session_id": str(art.session_id),
            "title": art.title,
            "artifact_type": art.artifact_type,
            "content": art.content,
            "version": art.version,
            "created_at": art.created_at.isoformat() if art.created_at else "",
        }
        for art in artifacts
    ]


@artifacts_router.get("/{id}")
def get_artifact_by_id(
    id: UUID,
    db: DbSession = Depends(get_db),
):
    """
    Retrieve an artifact by ID.
    """
    artifact_repo = ArtifactRepository(db)
    art = artifact_repo.get_by_id(id)
    if not art:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Artifact not found")
    return {
        "id": str(art.id),
        "session_id": str(art.session_id),
        "title": art.title,
        "artifact_type": art.artifact_type,
        "content": art.content,
        "version": art.version,
        "created_at": art.created_at.isoformat() if art.created_at else "",
    }
