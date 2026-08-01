import json
from pathlib import Path
from typing import List, Union, Optional, Dict, Any
from app.ingestion.models import Chunk
from app.services.embedding_service import EmbeddingService
from app.repositories.vector_store import VectorStore


def _sanitize_metadata(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitizes metadata values for ChromaDB.
    ChromaDB requires metadata values to be primitive types (str, int, float, bool).
    Complex structures (dicts, lists, None) are converted to JSON strings or removed/converted.
    """
    sanitized = {}
    for key, value in metadata.items():
        if value is None:
            continue
        elif isinstance(value, (str, int, float, bool)):
            sanitized[key] = value
        elif isinstance(value, (dict, list)):
            sanitized[key] = json.dumps(value)
        else:
            sanitized[key] = str(value)
    return sanitized


class VectorRepository:
    """
    Repository layer for managing and storing chunk embeddings in ChromaDB.
    Provides async interface for generating embeddings and storing transcript chunks without retrieval logic.
    """

    def __init__(
        self,
        vector_store: Optional[VectorStore] = None,
        embedding_service: Optional[EmbeddingService] = None,
    ):
        self.vector_store = vector_store or VectorStore()
        self.embedding_service = embedding_service or EmbeddingService()

    async def add_chunks(self, chunks: List[Chunk]) -> None:
        """
        Generates embeddings for transcript chunks asynchronously and stores them in ChromaDB.
        """
        if not chunks:
            return

        texts = [chunk.content for chunk in chunks]
        embeddings = await self.embedding_service.embed_documents(texts)

        ids: List[str] = []
        documents: List[str] = []
        metadatas: List[Dict[str, Any]] = []

        for chunk in chunks:
            ids.append(chunk.chunk_id)
            documents.append(chunk.content)
            
            raw_meta = {
                "doc_id": chunk.doc_id,
                "chunk_index": chunk.chunk_index,
                "start_char": chunk.start_char if chunk.start_char is not None else -1,
                "end_char": chunk.end_char if chunk.end_char is not None else -1,
                **chunk.metadata,
            }
            metadatas.append(_sanitize_metadata(raw_meta))

        collection = await self.vector_store.get_collection()
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(
            None,
            lambda: collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas,
            )
        )

    async def add_chunks_from_file(self, file_path: Union[str, Path]) -> None:
        """
        Reads transcript chunks saved in a JSON or JSONL file and stores their embeddings in ChromaDB.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Chunk file not found at: {file_path}")

        chunks: List[Chunk] = []

        if path.suffix == ".jsonl":
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        chunks.append(Chunk(**data))
        else:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    for item in data:
                        chunks.append(Chunk(**item))
                elif isinstance(data, dict):
                    chunks.append(Chunk(**data))

        await self.add_chunks(chunks)
