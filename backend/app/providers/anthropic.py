from typing import AsyncGenerator, Any, Optional
import httpx

from app.providers.base import BaseProvider

try:
    import anthropic
except ImportError:
    anthropic = None


class AnthropicProvider(BaseProvider):
    """
    LLM provider implementation for Anthropic Claude models.
    Supports both official anthropic SDK (if installed) and direct HTTP fallback.
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-5-sonnet-20240620"):
        self.api_key = api_key
        self.model = model

    async def generate(self, prompt: str, **kwargs: Any) -> str:
        if anthropic:
            client = anthropic.AsyncAnthropic(api_key=self.api_key)
            response = await client.messages.create(
                model=self.model,
                max_tokens=kwargs.pop("max_tokens", 1024),
                messages=[{"role": "user", "content": prompt}],
                **kwargs,
            )
            return "".join(block.text for block in response.content if getattr(block, "type", None) == "text")
        else:
            headers = {
                "x-api-key": self.api_key or "",
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            }
            payload = {
                "model": self.model,
                "max_tokens": kwargs.pop("max_tokens", 1024),
                "messages": [{"role": "user", "content": prompt}],
                **kwargs,
            }
            async with httpx.AsyncClient(base_url="https://api.anthropic.com") as client:
                response = await client.post("/v1/messages", json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()
                content = data.get("content", [])
                return "".join(item.get("text", "") for item in content if item.get("type") == "text")

    async def stream(self, prompt: str, **kwargs: Any) -> AsyncGenerator[str, None]:
        if anthropic:
            client = anthropic.AsyncAnthropic(api_key=self.api_key)
            async with client.messages.stream(
                model=self.model,
                max_tokens=kwargs.pop("max_tokens", 1024),
                messages=[{"role": "user", "content": prompt}],
                **kwargs,
            ) as stream:
                async for text in stream.text_stream:
                    yield text
        else:
            import json
            headers = {
                "x-api-key": self.api_key or "",
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            }
            payload = {
                "model": self.model,
                "max_tokens": kwargs.pop("max_tokens", 1024),
                "messages": [{"role": "user", "content": prompt}],
                "stream": True,
                **kwargs,
            }
            async with httpx.AsyncClient(base_url="https://api.anthropic.com") as client:
                async with client.stream("POST", "/v1/messages", json=payload, headers=headers) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if line and line.startswith("data: "):
                            data_str = line[6:].strip()
                            if data_str == "[DONE]":
                                break
                            try:
                                data = json.loads(data_str)
                                if data.get("type") == "content_block_delta":
                                    delta = data.get("delta", {})
                                    if delta.get("type") == "text_delta":
                                        yield delta.get("text", "")
                            except json.JSONDecodeError:
                                continue
