from typing import Any, Dict, List
from app.database.models import Message


class MockQAService:
    """
    Mock service for Q&A handling (no retrieval / AI).
    """

    def process(self, message: str, history: List[Message]) -> Dict[str, Any]:
        return {
            "content": f"[Mock QA Service Response] Answer to query: '{message}'",
            "metadata": {"service": "MockQAService", "retrieval_performed": False},
        }


class MockEssayService:
    """
    Mock service for Essay generation handling (no AI).
    """

    def process(self, message: str, history: List[Message]) -> Dict[str, Any]:
        return {
            "content": f"[Mock Essay Service Response] Outlined essay topic based on: '{message}'",
            "metadata": {"service": "MockEssayService", "ai_generated": False},
        }


class MockArtifactService:
    """
    Mock service for Artifact generation handling (no AI).
    """

    def process(self, message: str, history: List[Message]) -> Dict[str, Any]:
        return {
            "content": f"[Mock Artifact Service Response] Created template artifact for: '{message}'",
            "metadata": {"service": "MockArtifactService", "artifact_type": "template"},
        }
