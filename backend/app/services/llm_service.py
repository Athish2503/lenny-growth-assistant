from typing import AsyncGenerator, Any
from app.providers.base import BaseProvider


class LLMService:
    """
    High-level LLM service using dependency injection.
    Delegates generation and streaming to the injected BaseProvider without containing
    business logic, chat/retrieval, session handling, or prompt engineering.
    """

    def __init__(self, provider: BaseProvider):
        self.provider = provider

    async def generate(self, prompt: str, **kwargs: Any) -> str:
        """
        Generate text response by calling the injected LLM provider.
        """
        return await self.provider.generate(prompt, **kwargs)

    async def stream(self, prompt: str, **kwargs: Any) -> AsyncGenerator[str, None]:
        """
        Stream text response by calling the injected LLM provider.
        """
        async for chunk in self.provider.stream(prompt, **kwargs):
            yield chunk
