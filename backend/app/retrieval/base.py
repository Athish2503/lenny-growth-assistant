from abc import ABC, abstractmethod
from typing import List
from app.retrieval.models import RetrievalResult


class BaseRetriever(ABC):
    """
    Abstract base class for all retrieval algorithms.
    """

    @abstractmethod
    async def retrieve(self, query: str, top_k: int = 5) -> List[RetrievalResult]:
        """
        Retrieves top_k documents relevant to the given query.

        Args:
            query: User search/question string.
            top_k: Maximum number of documents to return.

        Returns:
            List of RetrievalResult containing top_k documents, scores, and metadata.
        """
        pass
