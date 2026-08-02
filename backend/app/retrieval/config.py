import os
from pathlib import Path
from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


_env_file_path = Path(__file__).resolve().parent.parent.parent / ".env"


class RetrievalConfig(BaseSettings):
    """Configuration settings for retrieval, embedding, and ChromaDB vector store.
    
    Reads values from environment variables or .env file.
    Never hardcodes absolute paths.
    """
    
    model_config = SettingsConfigDict(
        env_file=str(_env_file_path),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    CHROMA_API_KEY: str | None = Field(default=None)
    CHROMA_TENANT: str | None = Field(default=None)
    CHROMA_DATABASE: str | None = Field(default=None)

    CHROMA_DB_PATH: str = Field(
        default="backend/chroma_db",
        validation_alias=AliasChoices("CHROMA_DB_PATH", "CHROMA_PATH")
    )
    CHROMA_COLLECTION: str = Field(
        default="lenny_transcripts",
        validation_alias=AliasChoices("CHROMA_COLLECTION", "COLLECTION_NAME")
    )
    EMBEDDING_MODEL: str = Field(
        default="all-MiniLM-L6-v2",
        validation_alias=AliasChoices("EMBEDDING_MODEL", "MODEL_NAME")
    )
    EMBEDDING_DEVICE: str = Field(
        default="cpu",
        validation_alias=AliasChoices("EMBEDDING_DEVICE", "DEVICE")
    )
    EMBEDDING_BATCH_SIZE: int = Field(
        default=64,
        validation_alias=AliasChoices("EMBEDDING_BATCH_SIZE", "BATCH_SIZE")
    )
    CHUNKS_FILE_PATH: str = Field(
        default="backend/data/processed/chunks.json",
        validation_alias=AliasChoices("CHUNKS_FILE_PATH", "CHUNKS_PATH")
    )

    @property
    def CHROMA_PATH(self) -> str:
        return self.CHROMA_DB_PATH

    @property
    def COLLECTION_NAME(self) -> str:
        return self.CHROMA_COLLECTION

    @property
    def DEVICE(self) -> str:
        return self.EMBEDDING_DEVICE

    @property
    def BATCH_SIZE(self) -> int:
        return self.EMBEDDING_BATCH_SIZE

    @property
    def resolved_chroma_path(self) -> Path:
        """Resolves absolute path for ChromaDB storage directory."""
        path = Path(self.CHROMA_DB_PATH)
        if path.is_absolute():
            return path
        base_dir = Path(__file__).resolve().parent.parent.parent
        # If path starts with "backend/" and base_dir ends with "backend", resolve properly
        if str(path).startswith("backend") and base_dir.name == "backend":
            return (base_dir.parent / path).resolve()
        return (base_dir / path).resolve()

    @property
    def resolved_chunks_path(self) -> Path:
        """Resolves absolute path for processed chunks JSON file."""
        path = Path(self.CHUNKS_FILE_PATH)
        if path.is_absolute():
            return path
        base_dir = Path(__file__).resolve().parent.parent.parent
        if str(path).startswith("backend") and base_dir.name == "backend":
            return (base_dir.parent / path).resolve()
        return (base_dir / path).resolve()


def get_retrieval_config() -> RetrievalConfig:
    """Factory function to instantiate RetrievalConfig."""
    return RetrievalConfig()

