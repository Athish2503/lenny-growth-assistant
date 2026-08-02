from typing import Optional
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application configuration settings loaded from environment variables or .env file.
    Uses pydantic-settings to ensure type safety and proper defaults.
    Never calls os.getenv() directly.
    """
    PROJECT_NAME: str = "Lenny Growth Assistant"
    DATABASE_URL: str = "sqlite:///./lenny_growth.db"
    
    # Model & provider configuration
    MODEL_PROVIDER: str = "ollama"
    OLLAMA_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "mistral:7b"
    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL: str = "claude-3-5-sonnet-20240620"
    EMBEDDING_MODEL: Optional[str] = "all-MiniLM-L6-v2"
    CHROMA_PERSIST_DIRECTORY: str = "./chroma_db"
    CHROMA_COLLECTION_NAME: str = "transcript_chunks"

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def validate_database_url(cls, v: Optional[str]) -> str:
        if not v or not v.strip():
            return "sqlite:///./lenny_growth.db"
        return v.strip()

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
