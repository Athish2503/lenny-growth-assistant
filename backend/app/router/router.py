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

        # Check Essay intents
        essay_keywords = [
            "/essay", "write an essay", "essay on", "draft essay", "ship30", "ship 30",
            "atomic essay", "essay format", "essay about"
        ]
        if any(kw in content for kw in essay_keywords):
            return IntentType.ESSAY

        # Check Artifact intents
        artifact_keywords = [
            "/artifact", "generate artifact", "create artifact", "build artifact",
            "make artifact", "create an artifact", "generate an artifact", "make an artifact",
            "build an artifact", "render artifact", "show artifact", "artifact viewer",
            "html snippet", "css snippet", "markdown document"
        ]
        if any(kw in content for kw in artifact_keywords):
            return IntentType.ARTIFACT

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
