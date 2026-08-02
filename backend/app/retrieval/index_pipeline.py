import sys
from pathlib import Path

# Ensure backend directory is in sys.path for seamless package execution
_backend_dir = str(Path(__file__).resolve().parent.parent.parent)
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

import json
import logging
import time
from typing import Any, Dict, List, Optional, Set, Tuple

from tqdm import tqdm

from .config import RetrievalConfig, get_retrieval_config
from .embedding_service import EmbeddingService
from .vector_store import VectorStore

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)


class IndexPipeline:
    """Production-grade transcript indexing pipeline for embedding generation and ChromaDB persistence."""

    def __init__(
        self,
        embedding_service: Optional[EmbeddingService] = None,
        vector_store: Optional[VectorStore] = None,
        config: Optional[RetrievalConfig] = None,
    ) -> None:
        """Initialize IndexPipeline with required services.
        
        Args:
            embedding_service: EmbeddingService instance.
            vector_store: VectorStore instance.
            config: Optional RetrievalConfig settings override.
        """
        self.config = config or get_retrieval_config()
        self.embedding_service = embedding_service or EmbeddingService(config=self.config)
        self.vector_store = vector_store or VectorStore(config=self.config)

    def load_chunks(self, chunks_path: Optional[Path] = None) -> List[Dict[str, Any]]:
        """Load transcript chunks from the specified JSON file.
        
        Args:
            chunks_path: Path to chunks.json file.
            
        Returns:
            List of chunk dictionaries.
        """
        target_path = chunks_path or self.config.resolved_chunks_path
        logger.info("Loading chunks from %s ...", target_path)

        if not target_path.exists():
            raise FileNotFoundError(f"Chunks file not found at: {target_path}")

        with open(target_path, "r", encoding="utf-8") as f:
            chunks = json.load(f)

        logger.info("Loaded %d total chunks from disk", len(chunks))
        return chunks

    def get_existing_ids(self) -> Set[str]:
        """Fetch all existing chunk IDs stored in the ChromaDB collection for duplicate protection.
        
        Returns:
            Set of existing chunk ID strings.
        """
        try:
            collection = self.vector_store.get_or_create_collection()
            if collection.count() == 0:
                return set()
            records = collection.get(include=[])
            return set(records.get("ids", []))
        except Exception as e:
            logger.warning("Error fetching existing IDs from VectorStore: %s", e)
            return set()

    def prepare_metadata(self, chunk: Dict[str, Any]) -> Dict[str, Any]:
        """Format chunk fields into ChromaDB compatible metadata dictionary.
        
        Args:
            chunk: Raw chunk dictionary from chunks.json.
            
        Returns:
            Metadata dictionary with scalar primitive types.
        """
        topics_val = chunk.get("topics", [])
        if isinstance(topics_val, list):
            topics_str = ", ".join(str(t) for t in topics_val)
        else:
            topics_str = str(topics_val or "")

        return {
            "episode_id": str(chunk.get("episode_id", "")),
            "guest": str(chunk.get("guest", "")),
            "title": str(chunk.get("title", "")),
            "topics": topics_str,
            "publish_date": str(chunk.get("publish_date", "")),
            "youtube_url": str(chunk.get("youtube_url", "")),
            "chunk_number": int(chunk.get("chunk_number", 0)),
        }

    def run(self, chunks_path: Optional[Path] = None) -> Dict[str, Any]:
        """Execute the indexing pipeline.
        
        Workflow:
        1. Load chunks from chunks.json
        2. Filter out already-indexed chunks (Duplicate Protection)
        3. Generate embeddings in configurable batches
        4. Add documents, vectors, and metadata into ChromaDB
        5. Report indexing metrics and validation summary
        
        Args:
            chunks_path: Optional path override for chunks.json.
            
        Returns:
            Dictionary containing indexing statistics.
        """
        print("Loading chunks...")
        raw_chunks = self.load_chunks(chunks_path)
        total_chunks_loaded = len(raw_chunks)
        print(f"{total_chunks_loaded} chunks loaded")

        # Duplicate protection & incremental indexing
        existing_ids = self.get_existing_ids()
        new_chunks = [c for c in raw_chunks if c["id"] not in existing_ids]

        if not new_chunks:
            logger.info("No new chunks to index. All %d chunks already exist in ChromaDB.", total_chunks_loaded)
            collection_size = self.vector_store.count()
            print("=== Indexing Validation ===")
            print(f"Chunks loaded: {total_chunks_loaded}")
            print("Embeddings generated: 0 (All chunks already indexed)")
            print(f"Collection size: {collection_size}")
            print(f"Embedding dimension: {self.embedding_service.embedding_dimension}")
            print("Elapsed time: 0.00 seconds")
            print("===========================")
            return {
                "total_chunks_loaded": total_chunks_loaded,
                "documents_indexed": 0,
                "embeddings_generated": 0,
                "collection_size": collection_size,
                "embedding_dimension": self.embedding_service.embedding_dimension,
                "elapsed_seconds": 0.0,
                "chunks_per_second": 0.0,
            }

        logger.info(
            "Found %d new chunks to process out of %d loaded (%d already indexed).",
            len(new_chunks),
            total_chunks_loaded,
            len(existing_ids),
        )

        batch_size = self.config.BATCH_SIZE
        num_batches = (len(new_chunks) + batch_size - 1) // batch_size
        print(f"Generating embeddings...")

        start_time = time.perf_counter()
        documents_indexed = 0

        pbar = tqdm(total=len(new_chunks), desc="Indexing chunks", unit="chunk")

        for batch_idx in range(num_batches):
            batch_start_idx = batch_idx * batch_size
            batch_end_idx = min(batch_start_idx + batch_size, len(new_chunks))
            batch_chunks = new_chunks[batch_start_idx:batch_end_idx]

            batch_texts = [c["text"] for c in batch_chunks]
            batch_ids = [c["id"] for c in batch_chunks]
            batch_metadatas = [self.prepare_metadata(c) for c in batch_chunks]

            batch_start_time = time.perf_counter()
            # Batch embedding generation
            embeddings = self.embedding_service.embed(batch_texts, batch_size=batch_size)

            # Store in ChromaDB
            self.vector_store.add_documents(
                ids=batch_ids,
                embeddings=embeddings,
                documents=batch_texts,
                metadatas=batch_metadatas,
            )

            batch_elapsed = time.perf_counter() - batch_start_time
            documents_indexed += len(batch_chunks)
            pbar.update(len(batch_chunks))

            logger.info(
                "Current batch: %d/%d | Elapsed time: %.2fs | Vectors stored: %d",
                batch_idx + 1,
                num_batches,
                batch_elapsed,
                documents_indexed,
            )

        pbar.close()

        total_elapsed = time.perf_counter() - start_time
        avg_speed = documents_indexed / total_elapsed if total_elapsed > 0 else 0.0
        final_collection_size = self.vector_store.count()
        dim = self.embedding_service.embedding_dimension

        print("=== Indexing Validation ===")
        print(f"Chunks loaded: {total_chunks_loaded}")
        print(f"Embeddings generated: {documents_indexed}")
        print(f"Collection size: {final_collection_size}")
        print(f"Embedding dimension: {dim}")
        print(f"Elapsed time: {total_elapsed:.2f} seconds")
        print("===========================")

        return {
            "total_chunks_loaded": total_chunks_loaded,
            "documents_indexed": documents_indexed,
            "embeddings_generated": documents_indexed,
            "collection_size": final_collection_size,
            "embedding_dimension": dim,
            "elapsed_seconds": total_elapsed,
            "chunks_per_second": avg_speed,
        }


def main() -> None:
    """CLI entrypoint for running the indexing pipeline."""
    pipeline = IndexPipeline()
    pipeline.run()


if __name__ == "__main__":
    main()
