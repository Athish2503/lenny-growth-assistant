import json
from typing import AsyncGenerator, Any
import httpx

from app.providers.base import BaseProvider


class OllamaProvider(BaseProvider):
    """
    LLM provider implementation for Ollama HTTP API.
    """

    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3"):
        self.base_url = base_url.rstrip("/")
        self.model = model

    async def generate(self, prompt: str, **kwargs: Any) -> str:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            **kwargs,
        }
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            response = await client.post("/api/generate", json=payload)
            response.raise_for_status()
            data = response.json()
            return data.get("response", "")

    async def stream(self, prompt: str, **kwargs: Any) -> AsyncGenerator[str, None]:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": True,
            **kwargs,
        }
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            async with client.stream("POST", "/api/generate", json=payload) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line:
                        data = json.loads(line)
                        chunk = data.get("response", "")
                        if chunk:
                            yield chunk
