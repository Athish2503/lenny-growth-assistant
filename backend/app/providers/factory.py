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
        elif provider_type == "openai":
            # If Anthropic or Ollama are active, fallback or use Anthropic/Ollama if no key
            if settings.ANTHROPIC_API_KEY:
                return AnthropicProvider(
                    api_key=settings.ANTHROPIC_API_KEY,
                    model="claude-3-5-sonnet-20240620",
                )
            return OllamaProvider(
                base_url=settings.OLLAMA_URL or "http://localhost:11434",
                model=settings.OLLAMA_MODEL or "mistral:7b",
            )
        else:
            return OllamaProvider(
                base_url=settings.OLLAMA_URL or "http://localhost:11434",
                model=settings.OLLAMA_MODEL or "mistral:7b",
            )
