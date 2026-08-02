import asyncio
from typing import List, Optional
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
from app.core.config import settings


class EmbeddingService:
    """
    Asynchronous embedding service using ChromaDB's built-in ONNX default embedding function (ONNX runtime).
    Executes in thread executor to keep the async event loop non-blocking.
    """

    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or settings.EMBEDDING_MODEL or "all-MiniLM-L6-v2"
        self._ef: Optional[DefaultEmbeddingFunction] = None

    def _get_ef(self) -> DefaultEmbeddingFunction:
        if self._ef is None:
            self._ef = DefaultEmbeddingFunction()
        return self._ef

    def _embed_texts_sync(self, texts: List[str]) -> List[List[float]]:
        ef = self._get_ef()
        embeddings = ef(texts)
        return [[float(x) for x in emb] for emb in embeddings]

    async def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding vector for a single string asynchronously.
        """
        results = await self.embed_documents([text])
        return results[0]

    async def embed_query(self, text: str) -> List[float]:
        """
        Generate embedding vector for a single query string asynchronously.
        """
        return await self.embed_text(text)

    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embedding vectors for a list of strings asynchronously.
        """
        if not texts:
            return []
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self._embed_texts_sync, texts)
