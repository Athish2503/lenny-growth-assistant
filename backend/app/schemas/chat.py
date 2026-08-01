from typing import Any, Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class ChatRequest(BaseModel):
    user_id: UUID = Field(..., description="ID of the user making the request")
    session_id: UUID = Field(..., description="ID of the chat session")
    message: str = Field(..., min_length=1, description="User message content")


class MessageSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    session_id: UUID
    role: str
    content: str
    metadata_json: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    session_id: UUID
    intent: str
    response_message: MessageSchema
    history_count: int
    metadata: Optional[Dict[str, Any]] = None
