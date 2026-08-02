from typing import Optional, Dict, Any
from fastapi import APIRouter
from pydantic import BaseModel

from app.core.config import settings

router = APIRouter(prefix="/settings", tags=["settings"])


class SettingsSchema(BaseModel):
    theme: Optional[str] = "dark"
    provider: Optional[str] = "ollama"
    model: Optional[str] = "mistral:7b"
    embedding_model: Optional[str] = "all-MiniLM-L6-v2"
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 4096
    system_prompt: Optional[str] = (
        "You are Lenny, an expert growth advisor with deep knowledge of product-led growth, "
        "SaaS metrics, retention, and growth strategy. You have access to Lenny Rachitsky's newsletter archives."
    )
    stream_responses: Optional[bool] = True


# In-memory runtime settings initialized from app configuration
runtime_settings: Dict[str, Any] = {
    "theme": "dark",
    "provider": settings.MODEL_PROVIDER or "ollama",
    "model": settings.OLLAMA_MODEL if (settings.MODEL_PROVIDER or "ollama").lower() == "ollama" else settings.ANTHROPIC_MODEL,
    "embedding_model": settings.EMBEDDING_MODEL or "all-MiniLM-L6-v2",
    "temperature": 0.7,
    "max_tokens": 4096,
    "system_prompt": (
        "You are Lenny, an expert growth advisor with deep knowledge of product-led growth, "
        "SaaS metrics, retention, and growth strategy."
    ),
    "stream_responses": True,
}


import httpx

@router.get("", response_model=SettingsSchema)
def get_settings():
    """
    Get current application settings.
    """
    return runtime_settings


@router.get("/models")
async def get_available_models():
    """
    List available models for each provider (including live installed local Ollama models).
    """
    ollama_models = ["mistral:7b"]
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.get(f"{settings.OLLAMA_URL.rstrip('/')}/api/tags")
            if resp.status_code == 200:
                data = resp.json()
                tags = [m.get("name") for m in data.get("models", []) if m.get("name")]
                if tags:
                    ollama_models = tags
    except Exception:
        pass

    return {
        "ollama": ollama_models,
        "anthropic": ["claude-3-5-sonnet-20240620", "claude-3-opus-20240229", "claude-3-haiku-20240307"],
        "openai": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"],
        "current_provider": runtime_settings.get("provider", "ollama"),
        "current_model": runtime_settings.get("model", "mistral:7b"),
    }


@router.put("", response_model=SettingsSchema)
def update_settings(payload: SettingsSchema):
    """
    Update runtime settings and reflect provider selection in application config.
    """
    update_data = payload.model_dump(exclude_unset=True)
    runtime_settings.update(update_data)

    if "provider" in update_data:
        settings.MODEL_PROVIDER = update_data["provider"]
    if "model" in update_data:
        new_model = update_data["model"]
        if (settings.MODEL_PROVIDER or "").lower() == "ollama":
            settings.OLLAMA_MODEL = new_model
        else:
            settings.ANTHROPIC_MODEL = new_model

    return runtime_settings
