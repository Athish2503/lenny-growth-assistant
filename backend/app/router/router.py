from enum import Enum
from typing import List
from app.database.models import Message


class IntentType(str, Enum):
    QA = "qa"
    ESSAY = "essay"
    ARTIFACT = "artifact"


class IntentRouter:
    """
    IntentRouter routes a user's message and session history to the target intent handling logic.
    """

    def route(self, message: str, history: List[Message]) -> IntentType:
        """
        Classify input message into an intent without calling AI.
        """
        content = message.strip().lower()
        if content.startswith("/essay") or "write an essay" in content or "essay on" in content:
            return IntentType.ESSAY
        elif content.startswith("/artifact") or "generate artifact" in content or "create artifact" in content:
            return IntentType.ARTIFACT
        else:
            return IntentType.QA
