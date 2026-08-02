import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import chromadb
from chromadb.api import ClientAPI
from chromadb.api.models.Collection import Collection

from .config import RetrievalConfig, get_retrieval_config

logger = logging.getLogger(__name__)


class VectorStore:
    """Vector database wrapper for managing local persistent ChromaDB collections."""

    def __init__(
        self,
        chroma_path: Optional[Union[str, Path]] = None,
        collection_name: Optional[str] = None,
        config: Optional[RetrievalConfig] = None,
        api_key: Optional[str] = None,
        tenant: Optional[str] = None,
        database: Optional[str] = None,
    ) -> None:
        """Initialize VectorStore with local persistence path or Chroma Cloud connection settings.
        
        Args:
            chroma_path: Path to local directory where ChromaDB stores data.
            collection_name: Name of ChromaDB collection.
            config: Optional RetrievalConfig override.
            api_key: Optional Chroma Cloud API key.
            tenant: Optional Chroma Cloud tenant ID.
            database: Optional Chroma Cloud database name.
        """
        cfg = config or get_retrieval_config()
        path = Path(chroma_path) if chroma_path else cfg.resolved_chroma_path
        self.chroma_path = path.resolve()
        self.collection_name = collection_name or cfg.COLLECTION_NAME
        self.api_key = api_key or cfg.CHROMA_API_KEY
        self.tenant = tenant or cfg.CHROMA_TENANT
        self.database = database or cfg.CHROMA_DATABASE

        if self.api_key:
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
            # Ensure target directory exists for local persistence
            self.chroma_path.mkdir(parents=True, exist_ok=True)
            logger.info(
                "Connecting to persistent local ChromaDB at: %s for collection: %s",
                self.chroma_path,
                self.collection_name,
            )
            self.client: ClientAPI = chromadb.PersistentClient(path=str(self.chroma_path))
        self._collection: Optional[Collection] = None

    def get_or_create_collection(self) -> Collection:
        """Get existing collection or create a new one using cosine distance metric.
        
        Returns:
            ChromaDB Collection instance.
        """
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
        """Add documents, vectors, and metadata into the ChromaDB collection.
        
        Args:
            ids: List of unique document identifiers.
            embeddings: List of embedding vectors.
            documents: List of document text strings.
            metadatas: List of metadata dictionaries.
        """
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
        """Query the collection using dense vector representations.
        
        Args:
            query_embeddings: Query embedding vector or list of query embedding vectors.
            n_results: Number of nearest neighbors to return.
            where: Metadata filter conditions.
            where_document: Document text filter conditions.
            
        Returns:
            ChromaDB query results dictionary containing ids, distances, metadatas, documents.
        """
        collection = self.get_or_create_collection()

        # Wrap single vector if necessary
        if query_embeddings and isinstance(query_embeddings[0], float):
            query_embeddings = [query_embeddings]  # type: ignore

        return collection.query(
            query_embeddings=query_embeddings,  # type: ignore
            n_results=n_results,
            where=where,
            where_document=where_document,
        )

    def peek(self, limit: int = 5) -> Dict[str, Any]:
        """Peek at the first few items in the collection.
        
        Args:
            limit: Maximum items to return.
            
        Returns:
            Peek result dictionary.
        """
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

