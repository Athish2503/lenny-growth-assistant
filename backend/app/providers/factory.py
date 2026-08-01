from app.core.config import Settings
from app.providers.base import BaseProvider
from app.providers.ollama import OllamaProvider
from app.providers.anthropic import AnthropicProvider


class ProviderFactory:
    """
    Factory responsible for instantiating LLM provider instances
    based on application configuration settings.
    """

    @staticmethod
    def create_provider(settings: Settings) -> BaseProvider:
        provider_type = (settings.MODEL_PROVIDER or "ollama").lower().strip()

        if provider_type == "ollama":
            return OllamaProvider(
                base_url=settings.OLLAMA_URL or "http://localhost:11434",
                model=settings.OLLAMA_MODEL or "llama3",
            )
        elif provider_type == "anthropic":
            return AnthropicProvider(
                api_key=settings.ANTHROPIC_API_KEY,
                model=settings.ANTHROPIC_MODEL or "claude-3-5-sonnet-20240620",
            )
        else:
            raise ValueError(f"Unsupported LLM provider type: {provider_type}")
