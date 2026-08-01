import asyncio
from typing import Optional
import chromadb
from app.core.config import settings


class VectorStore:
    """
    Asynchronous ChromaDB vector store wrapper.
    Manages persistent client connections and collection retrieval asynchronously.
    """

    def __init__(
        self,
        persist_directory: Optional[str] = None,
        collection_name: Optional[str] = None,
    ):
        self.persist_directory = (
            persist_directory or settings.CHROMA_PERSIST_DIRECTORY
        )
        self.collection_name = (
            collection_name or settings.CHROMA_COLLECTION_NAME
        )
        self._client: Optional[AsyncClientAPI] = None
        self._collection: Optional[AsyncCollection] = None

    async def get_client(self) -> chromadb.ClientAPI:
        """
        Get or initialize the ChromaDB persistent client.
        """
        if self._client is None:
            self._client = chromadb.PersistentClient(
                path=self.persist_directory
            )
        return self._client

    async def get_collection(self):
        """
        Get or create the target collection asynchronously.
        """
        if self._collection is None:
            client = await self.get_client()
            loop = asyncio.get_running_loop()
            self._collection = await loop.run_in_executor(
                None, lambda: client.get_or_create_collection(name=self.collection_name)
            )
        return self._collection
