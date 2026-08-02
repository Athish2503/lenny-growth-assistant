import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Header, Request, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session as DbSession
from pydantic import BaseModel, Field

from app.database.session import get_db
from app.repositories.message_repository import MessageRepository
from app.repositories.session_repository import SessionRepository
from app.repositories.artifact_repository import ArtifactRepository
from app.services.chat_service import ChatService

router = APIRouter(prefix="/chat", tags=["chat"])


class FlexibleChatRequest(BaseModel):
    session_id: uuid.UUID = Field(..., description="ID of the chat session")
    user_id: Optional[uuid.UUID] = Field(default=None, description="Optional user ID")
    message: Optional[str] = Field(default=None, description="User message text")
    content: Optional[str] = Field(default=None, description="Alternative field for message content")
    stream: Optional[bool] = Field(default=False, description="Whether to stream response via SSE")

    @property
    def text(self) -> str:
        t = self.message or self.content or ""
        if not t.strip():
            raise ValueError("Message content cannot be empty")
        return t.strip()


def get_chat_service(db: DbSession = Depends(get_db)) -> ChatService:
    session_repo = SessionRepository(db)
    message_repo = MessageRepository(db)
    artifact_repo = ArtifactRepository(db)
    return ChatService(
        session_repo=session_repo,
        message_repo=message_repo,
        artifact_repo=artifact_repo,
    )


@router.post("")
async def chat_endpoint(
    payload: FlexibleChatRequest,
    request: Request,
    accept: Optional[str] = Header(None),
    service: ChatService = Depends(get_chat_service),
):
    """
    Unified chat endpoint.
    Supports both standard JSON responses and Server Sent Events (SSE) streaming.
    """
    user_uuid = payload.user_id or uuid.uuid4()
    request_id = str(uuid.uuid4())
    is_sse = payload.stream or (accept and "text/event-stream" in accept.lower())

    if is_sse:
        return StreamingResponse(
            service.process_chat_stream(
                user_id=user_uuid,
                session_id=payload.session_id,
                message_text=payload.text,
                request_id=request_id,
            ),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Request-ID": request_id,
            },
        )

    try:
        response_data = await service.process_chat(
            user_id=user_uuid,
            session_id=payload.session_id,
            message_text=payload.text,
            request_id=request_id,
        )
        return response_data
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat processing failed: {str(e)}",
        )
