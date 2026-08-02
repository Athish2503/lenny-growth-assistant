import asyncio
from typing import Any, Dict, List, Optional, Union

from app.retrieval.config import RetrievalConfig, get_retrieval_config
from app.retrieval.vector_store import VectorStore as SyncVectorStore


class VectorStore:
    """
    Async ChromaDB vector store wrapper.
    Delegates to the sync retrieval VectorStore (Chroma Cloud by default).
    """

    def __init__(
        self,
        persist_directory: Optional[str] = None,
        collection_name: Optional[str] = None,
        config: Optional[RetrievalConfig] = None,
        api_key: Optional[str] = None,
        tenant: Optional[str] = None,
        database: Optional[str] = None,
    ):
        cfg = config or get_retrieval_config()
        force_local = api_key == "" or persist_directory is not None
        self._store = SyncVectorStore(
            chroma_path=persist_directory or cfg.CHROMA_DB_PATH,
            collection_name=collection_name,
            config=cfg,
            api_key="" if force_local else api_key,
            tenant=tenant,
            database=database,
        )

    async def get_collection(self):
        """Get or create the target collection asynchronously."""
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self._store.get_or_create_collection)

    async def query(
        self,
        query_embeddings: Union[List[float], List[List[float]]],
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None,
        where_document: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Query the collection asynchronously."""
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None,
            lambda: self._store.query(
                query_embeddings=query_embeddings,
                n_results=n_results,
                where=where,
                where_document=where_document,
            ),
        )
