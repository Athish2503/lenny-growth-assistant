import logging
from typing import List, Union
import numpy as np
from sentence_transformers import SentenceTransformer

from .config import RetrievalConfig, get_retrieval_config

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating normalized sentence embeddings using SentenceTransformers.
    
    Loads the underlying SentenceTransformer model once during initialization
    to prevent reloading during runtime.
    """

    def __init__(
        self,
        model_name: str | None = None,
        batch_size: int | None = None,
        device: str | None = None,
        config: RetrievalConfig | None = None,
    ) -> None:
        """Initialize the EmbeddingService with model configurations.
        
        Args:
            model_name: SentenceTransformer model name or path.
            batch_size: Default batch size for encoding multiple texts.
            device: Computing device ('cpu', 'cuda', etc.).
            config: Optional RetrievalConfig override.
        """
        cfg = config or get_retrieval_config()
        self.model_name = model_name or cfg.EMBEDDING_MODEL
        self.batch_size = batch_size or cfg.BATCH_SIZE
        self.device = device or cfg.DEVICE

        logger.info(
            "Initializing EmbeddingService with model: %s on device: %s",
            self.model_name,
            self.device,
        )
        self._model = SentenceTransformer(self.model_name, device=self.device)
        self._dimension = self._model.get_sentence_embedding_dimension()
        logger.info("Model loaded successfully. Embedding dimension: %d", self._dimension)

    @property
    def embedding_dimension(self) -> int:
        """Return the dimension of output embeddings."""
        return self._dimension

    def embed_documents(
        self,
        texts: List[str],
        batch_size: int | None = None,
        show_progress_bar: bool = False,
    ) -> List[List[float]]:
        """Generate normalized embeddings for a list of documents in batches.
        
        Args:
            texts: List of document text strings to embed.
            batch_size: Optional override for default batch size.
            show_progress_bar: Whether to display a progress bar during encoding.
            
        Returns:
            List of normalized floating point embedding vectors.
        """
        return self.embed(texts, batch_size=batch_size, show_progress_bar=show_progress_bar)

    def embed(
        self,
        texts: List[str],
        batch_size: int | None = None,
        show_progress_bar: bool = False,
    ) -> List[List[float]]:
        """Generate normalized embeddings for a list of texts in batches.
        
        Args:
            texts: List of text strings to embed.
            batch_size: Optional override for default batch size.
            show_progress_bar: Whether to display a progress bar during encoding.
            
        Returns:
            List of normalized floating point embedding vectors.
        """
        if not texts:
            return []

        effective_batch_size = batch_size or self.batch_size
        embeddings: Union[np.ndarray, List[np.ndarray]] = self._model.encode(
            texts,
            batch_size=effective_batch_size,
            show_progress_bar=show_progress_bar,
            normalize_embeddings=True,
            convert_to_numpy=True,
        )

        if isinstance(embeddings, np.ndarray):
            return embeddings.tolist()
        return [e.tolist() for e in embeddings]

    def embed_query(self, text: str) -> List[float]:
        """Generate a single normalized embedding for a query string.
        
        Args:
            text: Query string to embed.
            
        Returns:
            List of floats representing the query embedding vector.
        """
        if not text:
            return [0.0] * self._dimension

        embedding = self._model.encode(
            text,
            normalize_embeddings=True,
            convert_to_numpy=True,
        )
        return embedding.tolist()
