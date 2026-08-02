from typing import Optional
from pydantic import Field, AliasChoices, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application configuration settings loaded from environment variables or .env file.
    Uses pydantic-settings with AliasChoices to ensure seamless binding with environment keys.
    """
    PROJECT_NAME: str = "Lenny Growth Assistant"
    DATABASE_URL: str = Field(
        default="sqlite:///./lenny_growth.db",
        validation_alias=AliasChoices("DATABASE_URL")
    )
    
    # Model & provider configuration
    MODEL_PROVIDER: str = Field(
        default="ollama",
        validation_alias=AliasChoices("MODEL_PROVIDER", "PROVIDER")
    )
    OLLAMA_URL: str = Field(
        default="http://localhost:11434",
        validation_alias=AliasChoices("OLLAMA_URL")
    )
    OLLAMA_MODEL: str = Field(
        default="mistral:7b",
        validation_alias=AliasChoices("OLLAMA_MODEL", "MODEL")
    )
    ANTHROPIC_API_KEY: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("ANTHROPIC_API_KEY")
    )
    ANTHROPIC_MODEL: str = Field(
        default="claude-3-5-sonnet-20240620",
        validation_alias=AliasChoices("ANTHROPIC_MODEL")
    )
    EMBEDDING_MODEL: Optional[str] = Field(
        default="all-MiniLM-L6-v2",
        validation_alias=AliasChoices("EMBEDDING_MODEL", "MODEL_NAME")
    )

    # Chroma Cloud (required for vector storage)
    CHROMA_API_KEY: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("CHROMA_API_KEY")
    )
    CHROMA_TENANT: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("CHROMA_TENANT")
    )
    CHROMA_DATABASE: Optional[str] = Field(
        default="lenny_transcripts",
        validation_alias=AliasChoices("CHROMA_DATABASE")
    )
    CHROMA_COLLECTION_NAME: str = Field(
        default="Lenny_Assist",
        validation_alias=AliasChoices("CHROMA_COLLECTION_NAME", "CHROMA_COLLECTION", "COLLECTION_NAME")
    )
    # Local path — only used in tests when CHROMA_API_KEY is explicitly empty
    CHROMA_PERSIST_DIRECTORY: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("CHROMA_PERSIST_DIRECTORY", "CHROMA_DB_PATH", "CHROMA_PATH")
    )

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
