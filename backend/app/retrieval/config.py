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
    CHROMA_DATABASE: str | None = Field(default="lenny_transcripts")

    # Local path — only used in tests when CHROMA_API_KEY is explicitly empty
    CHROMA_DB_PATH: str | None = Field(
        default=None,
        validation_alias=AliasChoices("CHROMA_DB_PATH", "CHROMA_PATH", "CHROMA_PERSIST_DIRECTORY")
    )
    CHROMA_COLLECTION: str = Field(
        default="Lenny_Assist",
        validation_alias=AliasChoices("CHROMA_COLLECTION", "CHROMA_COLLECTION_NAME", "COLLECTION_NAME")
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
    def CHROMA_PATH(self) -> str | None:
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
    def use_chroma_cloud(self) -> bool:
        """True when Chroma Cloud credentials are configured."""
        return bool(self.CHROMA_API_KEY and self.CHROMA_TENANT and self.CHROMA_DATABASE)

    @property
    def resolved_chroma_path(self) -> Path:
        """Resolves absolute path for local ChromaDB storage (tests only)."""
        if not self.CHROMA_DB_PATH:
            raise ValueError("CHROMA_DB_PATH is required for local ChromaDB mode")
        path = Path(self.CHROMA_DB_PATH)
        if path.is_absolute():
            return path
        base_dir = Path(__file__).resolve().parent.parent.parent
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

