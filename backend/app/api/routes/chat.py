from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session as DbSession

from app.database.session import get_db
from app.repositories.message_repository import MessageRepository
from app.repositories.session_repository import SessionRepository
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService

router = APIRouter(prefix="/chat", tags=["chat"])


def get_chat_service(db: DbSession = Depends(get_db)) -> ChatService:
    session_repo = SessionRepository(db)
    message_repo = MessageRepository(db)
    return ChatService(session_repo=session_repo, message_repo=message_repo)


@router.post("", response_model=ChatResponse, status_code=status.HTTP_200_OK)
def chat_endpoint(
    payload: ChatRequest,
    service: ChatService = Depends(get_chat_service),
):
    """
    Chat endpoint for sending messages through the chat pipeline.
    """
    try:
        response_data = service.process_chat(
            user_id=payload.user_id,
            session_id=payload.session_id,
            message_text=payload.message,
        )
        return response_data
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        )
