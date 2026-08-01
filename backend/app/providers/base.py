from abc import ABC, abstractmethod
from typing import AsyncGenerator, Any


class BaseProvider(ABC):
    """
    Abstract base interface for LLM providers.
    All providers must implement generate and stream.
    """

    @abstractmethod
    async def generate(self, prompt: str, **kwargs: Any) -> str:
        """
        Generate a complete text response asynchronously given a prompt.
        """
        pass

    @abstractmethod
    async def stream(self, prompt: str, **kwargs: Any) -> AsyncGenerator[str, None]:
        """
        Stream text response chunks asynchronously given a prompt.
        """
        pass
