"""
Ingestion Pipeline — Step 8.

Orchestrates the full transcript ingestion flow:

    TranscriptLoader  →  TranscriptParser  →  TopicParser
         ↓                    ↓                    ↓
    (paths)           (Documents)           (TopicMap)
         └──────────────────┬────────────────────┘
                            ↓ Metadata Enrichment (Step 4)
                     TranscriptCleaner (Step 5)
                            ↓
                     SemanticChunker (Step 6)
                            ↓
                     Save chunks.json (Step 7)

Run directly::

    python -m backend.app.retrieval.pipeline

or::

    cd backend
    python -m app.retrieval.pipeline
"""

from __future__ import annotations

import json
import logging
import sys
import time
from pathlib import Path
from typing import List, Optional

from app.retrieval.chunker import SemanticChunker
from app.retrieval.cleaner import TranscriptCleaner
from app.retrieval.loader import TranscriptLoader
from app.retrieval.models import Chunk, Document, TopicMap
from app.retrieval.parser import TranscriptParser
from app.retrieval.topic_parser import TopicParser

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Default paths  (relative to backend/ working directory)
# ---------------------------------------------------------------------------

_DEFAULT_EPISODES_DIR = Path("data/transcripts/episodes")
_DEFAULT_INDEX_DIR = Path("data/transcripts/index")
_DEFAULT_OUTPUT_PATH = Path("data/processed/chunks.json")


class IngestionPipeline:
    """
    Production-grade transcript ingestion pipeline.

    Parameters
    ----------
    episodes_dir :
        Path to the ``episodes/`` directory.
    index_dir :
        Path to the topic ``index/`` directory.
    output_path :
        Destination path for the processed ``chunks.json`` file.
    chunk_size :
        Target token size per chunk (passed to :class:`SemanticChunker`).
    overlap :
        Token overlap between consecutive chunks.
    """

    def __init__(
        self,
        episodes_dir: Optional[Path] = None,
        index_dir: Optional[Path] = None,
        output_path: Optional[Path] = None,
        chunk_size: int = 800,
        overlap: int = 150,
    ) -> None:
        self.episodes_dir = episodes_dir or _DEFAULT_EPISODES_DIR
        self.index_dir = index_dir or _DEFAULT_INDEX_DIR
        self.output_path = output_path or _DEFAULT_OUTPUT_PATH

        # Injected components (enables test mocking / subclassing)
        self.loader = TranscriptLoader(episodes_dir=self.episodes_dir)
        self.parser = TranscriptParser()
        self.topic_parser = TopicParser(index_dir=self.index_dir)
        self.cleaner = TranscriptCleaner()
        self.chunker = SemanticChunker(chunk_size=chunk_size, overlap=overlap)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(self) -> List[Chunk]:
        """
        Execute the full ingestion pipeline and return all chunks.

        Side-effects
        ------------
        * Writes ``chunks.json`` to :attr:`output_path`.
        * Logs progress and statistics to stdout.

        Returns
        -------
        List[Chunk]
            All generated chunks in episode order.
        """
        start_time = time.perf_counter()

        # ── Step 1: Discover ──────────────────────────────────────────
        logger.info("Step 1: Discovering transcript files …")
        paths = self.loader.discover()
        logger.info("  Transcripts found: %d", len(paths))

        if not paths:
            logger.warning("No transcripts found — exiting early.")
            return []

        # ── Step 3: Parse topic index ─────────────────────────────────
        logger.info("Step 3: Parsing topic index …")
        topic_map: TopicMap = self.topic_parser.parse()
        logger.info("  Topic map entries: %d", len(topic_map.mapping))

        # ── Steps 2 + 4 + 5 + 6: Parse, Enrich, Clean, Chunk ─────────
        logger.info("Steps 2–6: Parsing, enriching, cleaning, chunking …")
        all_chunks: List[Chunk] = []
        errors = 0

        for path in paths:
            try:
                doc = self._process_single(path, topic_map)
                all_chunks.extend(doc)
            except Exception as exc:
                logger.error("Failed to process '%s': %s", path, exc)
                errors += 1

        # ── Step 7: Save JSON ─────────────────────────────────────────
        logger.info("Step 7: Saving chunks to '%s' …", self.output_path)
        self._save(all_chunks)

        elapsed = time.perf_counter() - start_time

        # ── Statistics ────────────────────────────────────────────────
        self._print_stats(
            transcript_count=len(paths),
            chunk_count=len(all_chunks),
            elapsed=elapsed,
            errors=errors,
        )
        return all_chunks

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _process_single(self, path: Path, topic_map: TopicMap) -> List[Chunk]:
        """Parse, enrich, clean, and chunk a single transcript."""
        # Step 2: Parse
        doc: Document = self.parser.parse(path)

        # Step 4: Metadata enrichment — attach topics
        guest_name = doc.metadata.guest or ""
        topics = topic_map.get_topics(guest_name)
        doc.metadata.topics = topics

        # Step 5: Clean
        doc.content = self.cleaner.clean(doc.content)

        # Step 6: Chunk
        return self.chunker.chunk(doc)

    def _save(self, chunks: List[Chunk]) -> None:
        """Serialise *chunks* to pretty-printed JSON at :attr:`output_path`."""
        self.output_path.parent.mkdir(parents=True, exist_ok=True)

        serialised = [
            {
                "id": chunk.chunk_id,
                "episode_id": chunk.episode_id,
                "chunk_number": chunk.chunk_number,
                "guest": chunk.guest,
                "title": chunk.title,
                "topics": chunk.topics,
                "publish_date": chunk.publish_date,
                "youtube_url": chunk.youtube_url,
                "text": chunk.text,
            }
            for chunk in chunks
        ]

        with open(self.output_path, "w", encoding="utf-8") as fh:
            json.dump(serialised, fh, indent=2, ensure_ascii=False)

        logger.info("  Written %d chunks → %s", len(chunks), self.output_path.resolve())

    @staticmethod
    def _print_stats(
        transcript_count: int,
        chunk_count: int,
        elapsed: float,
        errors: int,
    ) -> None:
        """Print a human-readable summary to stdout."""
        if chunk_count:
            avg_tokens = sum(0 for _ in range(chunk_count))  # placeholder
        sep = "=" * 52
        print(f"\n{sep}")
        print("  INGESTION PIPELINE — COMPLETE")
        print(sep)
        print(f"  Transcripts loaded  : {transcript_count:,}")
        print(f"  Chunks generated    : {chunk_count:,}")
        print(f"  Processing errors   : {errors}")
        print(f"  Processing time     : {elapsed:.1f}s")
        print(sep)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    """CLI entry point: ``python -m backend.app.retrieval.pipeline``."""
    # Resolve project root so relative data/ paths work regardless of
    # where the command is invoked from.
    # Strategy: walk up from this file until we find "data/transcripts"
    here = Path(__file__).resolve().parent
    # Walk up to find the backend/ directory (contains data/)
    backend_dir: Optional[Path] = None
    for candidate in [here, here.parent, here.parent.parent, here.parent.parent.parent]:
        if (candidate / "data" / "transcripts").exists():
            backend_dir = candidate
            break

    if backend_dir is None:
        logger.error(
            "Cannot locate data/transcripts. "
            "Run this script from the backend/ directory."
        )
        sys.exit(1)

    pipeline = IngestionPipeline(
        episodes_dir=backend_dir / "data" / "transcripts" / "episodes",
        index_dir=backend_dir / "data" / "transcripts" / "index",
        output_path=backend_dir / "data" / "processed" / "chunks.json",
    )
    pipeline.run()


if __name__ == "__main__":
    main()
