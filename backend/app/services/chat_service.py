from typing import Optional
from uuid import UUID

from app.database.models import Message
from app.repositories.message_repository import MessageRepository
from app.repositories.session_repository import SessionRepository
from app.router.router import IntentRouter, IntentType
from app.services.mock_services import (
    MockArtifactService,
    MockEssayService,
    MockQAService,
)


class ChatService:
    """
    Service layer orchestrating the Chat pipeline:
    1. Receive user message
    2. Load conversation history
    3. Call IntentRouter
    4. Process through intent target mock service (No retrieval, no AI)
    5. Persist assistant response & return payload
    """

    def __init__(
        self,
        session_repo: SessionRepository,
        message_repo: MessageRepository,
        router: Optional[IntentRouter] = None,
        qa_service: Optional[MockQAService] = None,
        essay_service: Optional[MockEssayService] = None,
        artifact_service: Optional[MockArtifactService] = None,
    ):
        self.session_repo = session_repo
        self.message_repo = message_repo
        self.router = router or IntentRouter()
        self.qa_service = qa_service or MockQAService()
        self.essay_service = essay_service or MockEssayService()
        self.artifact_service = artifact_service or MockArtifactService()

    def process_chat(self, user_id: UUID, session_id: UUID, message_text: str):
        # Verify session exists
        session = self.session_repo.get_by_id(session_id)
        if not session or session.user_id != user_id:
            raise ValueError("Session not found for given user")

        # 1. Receive & save user message
        self.message_repo.create_message(
            session_id=session_id,
            role="user",
            content=message_text,
        )

        # 2. Load conversation history
        history = self.message_repo.get_session_history(session_id)

        # 3. Call IntentRouter
        intent = self.router.route(message_text, history)

        # 4. Dispatch to mock services (No retrieval, no AI)
        if intent == IntentType.ESSAY:
            res = self.essay_service.process(message_text, history)
        elif intent == IntentType.ARTIFACT:
            res = self.artifact_service.process(message_text, history)
        else:
            res = self.qa_service.process(message_text, history)

        # 5. Persist assistant response message
        assistant_msg = self.message_repo.create_message(
            session_id=session_id,
            role="assistant",
            content=res["content"],
            metadata_json=res.get("metadata"),
        )

        return {
            "session_id": session_id,
            "intent": intent.value,
            "response_message": assistant_msg,
            "history_count": len(history),
            "metadata": res.get("metadata"),
        }
