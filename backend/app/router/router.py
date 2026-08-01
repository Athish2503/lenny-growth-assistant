from enum import Enum
from typing import Any, List, Optional
from app.database.models import Message


class IntentType(str, Enum):
    QA = "qa"
    ESSAY = "essay"
    ARTIFACT = "artifact"


class IntentRouter:
    """
    IntentRouter routes a user's message and session history to the appropriate handling service using deterministic rules.
    """

    def __init__(
        self,
        qa_service: Optional[Any] = None,
        essay_service: Optional[Any] = None,
        artifact_service: Optional[Any] = None,
    ):
        self.qa_service = qa_service
        self.essay_service = essay_service
        self.artifact_service = artifact_service

    def classify_intent(self, message: str, history: Optional[List[Message]] = None) -> IntentType:
        """
        Classify input message into an intent deterministically without calling LLMs.
        """
        content = message.strip().lower()
        if content.startswith("/essay") or "write an essay" in content or "essay on" in content or "draft essay" in content:
            return IntentType.ESSAY
        elif content.startswith("/artifact") or "generate artifact" in content or "create artifact" in content or "build artifact" in content:
            return IntentType.ARTIFACT
        else:
            return IntentType.QA

    def route(self, message: str, history: Optional[List[Message]] = None) -> IntentType:
        """
        Maintains backward compatibility returning IntentType enum.
        """
        return self.classify_intent(message, history)

    def get_service(self, message: str, history: Optional[List[Message]] = None) -> Any:
        """
        Classify intent and return the corresponding target service instance.
        """
        intent = self.classify_intent(message, history)
        if intent == IntentType.ESSAY:
            return self.essay_service
        elif intent == IntentType.ARTIFACT:
            return self.artifact_service
        else:
            return self.qa_service
