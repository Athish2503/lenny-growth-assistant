import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import chromadb
from chromadb.api import ClientAPI
from chromadb.api.models.Collection import Collection

from .config import RetrievalConfig, get_retrieval_config

logger = logging.getLogger(__name__)


class VectorStore:
    """Vector database wrapper for Chroma Cloud collections."""

    def __init__(
        self,
        chroma_path: Optional[Union[str, Path]] = None,
        collection_name: Optional[str] = None,
        config: Optional[RetrievalConfig] = None,
        api_key: Optional[str] = None,
        tenant: Optional[str] = None,
        database: Optional[str] = None,
    ) -> None:
        """Initialize VectorStore with Chroma Cloud connection settings.

        Pass ``api_key=""`` explicitly to force local persistent mode (tests only).
        """
        cfg = config or get_retrieval_config()
        self.collection_name = collection_name or cfg.COLLECTION_NAME
        self.api_key = api_key if api_key is not None else cfg.CHROMA_API_KEY
        self.tenant = tenant or cfg.CHROMA_TENANT
        self.database = database or cfg.CHROMA_DATABASE
        self.chroma_path: Optional[Path] = None

        if self.api_key:
            if not self.tenant or not self.database:
                raise ValueError(
                    "CHROMA_TENANT and CHROMA_DATABASE are required when using Chroma Cloud"
                )
            logger.info(
                "Connecting to Chroma Cloud (tenant: %s, database: %s) for collection: %s",
                self.tenant,
                self.database,
                self.collection_name,
            )
            self.client: ClientAPI = chromadb.CloudClient(
                tenant=self.tenant,
                database=self.database,
                api_key=self.api_key,
            )
        else:
            path = Path(chroma_path) if chroma_path else cfg.resolved_chroma_path
            self.chroma_path = path.resolve()
            self.chroma_path.mkdir(parents=True, exist_ok=True)
            logger.info(
                "Connecting to persistent local ChromaDB at: %s for collection: %s",
                self.chroma_path,
                self.collection_name,
            )
            self.client = chromadb.PersistentClient(path=str(self.chroma_path))
        self._collection: Optional[Collection] = None

    def get_or_create_collection(self) -> Collection:
        """Get existing collection or create a new one using cosine distance metric."""
        if self._collection is None:
            # Dynamically auto-select the correct non-empty collection if configured one is empty
            try:
                collections = self.client.list_collections()
                non_empty_cols = [c for c in collections if c.count() > 0]
                if non_empty_cols:
                    chosen_col = None
                    # Keep configured name if it actually has data
                    for c in non_empty_cols:
                        if c.name == self.collection_name:
                            chosen_col = c
                            break
                    # Otherwise fallback to the first collection that actually has data
                    if not chosen_col:
                        chosen_col = non_empty_cols[0]
                        logger.info("Chroma auto-selected non-empty collection: %s (count: %d)", chosen_col.name, chosen_col.count())
                        self.collection_name = chosen_col.name
                    self._collection = chosen_col
            except Exception as e:
                logger.warning("Error listing collections for auto-selection: %s", e)

            if self._collection is None:
                self._collection = self.client.get_or_create_collection(
                    name=self.collection_name,
                    metadata={"hnsw:space": "cosine"},
                )
            logger.info(
                "Collection '%s' ready (Cosine Similarity). Total items: %d",
                self.collection_name,
                self._collection.count(),
            )
        return self._collection

    def delete_collection(self) -> None:
        """Delete the collection if it exists."""
        try:
            self.client.delete_collection(name=self.collection_name)
            self._collection = None
            logger.info("Deleted collection '%s'", self.collection_name)
        except Exception as e:
            logger.warning("Could not delete collection '%s': %s", self.collection_name, e)

    def count(self) -> int:
        """Return the current document count in the collection."""
        collection = self.get_or_create_collection()
        return collection.count()

    def add_documents(
        self,
        ids: List[str],
        embeddings: List[List[float]],
        documents: List[str],
        metadatas: List[Dict[str, Any]],
    ) -> None:
        """Add documents, vectors, and metadata into the ChromaDB collection."""
        if not ids:
            return

        collection = self.get_or_create_collection()
        collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
        )
        logger.debug("Successfully added %d documents to collection '%s'", len(ids), self.collection_name)

    def query(
        self,
        query_embeddings: Union[List[float], List[List[float]]],
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None,
        where_document: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Query the collection using dense vector representations."""
        collection = self.get_or_create_collection()

        if query_embeddings and isinstance(query_embeddings[0], float):
            query_embeddings = [query_embeddings]  # type: ignore

        return collection.query(
            query_embeddings=query_embeddings,  # type: ignore
            n_results=n_results,
            where=where,
            where_document=where_document,
            include=["documents", "metadatas", "distances"],
        )

    def peek(self, limit: int = 5) -> Dict[str, Any]:
        """Peek at the first few items in the collection."""
        collection = self.get_or_create_collection()
        return collection.peek(limit=limit)

    def reset_collection(self) -> None:
        """Reset collection by deleting and re-creating it."""
        self.delete_collection()
        self.get_or_create_collection()
        logger.info("VectorStore collection reset complete for '%s'", self.collection_name)

    def reset(self) -> None:
        """Alias for reset_collection."""
        self.reset_collection()
