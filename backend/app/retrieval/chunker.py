"""
SemanticChunker — Step 6 of the ingestion pipeline.

Responsibility:
    Split a cleaned transcript body into overlapping text chunks that
    respect natural language boundaries (paragraphs, speaker turns,
    section headings).  Every chunk inherits the full episode metadata
    so it is self-contained for embedding and retrieval.

Chunking strategy
-----------------
1. **Section split** — Markdown headings (``#``, ``##``, ``###``) define
   top-level section boundaries.
2. **Speaker-turn split** — Within each section, lines matching the
   ``Name (HH:MM:SS):`` pattern start a new logical block.
3. **Paragraph split** — Within each speaker block, double-newlines
   (``\\n\\n``) further subdivide the text.
4. **Greedy assembly with overlap** — Blocks are greedily merged into
   chunks up to *chunk_size* tokens.  When a chunk boundary is reached
   the last *overlap* tokens are carried forward into the next chunk.

Token counting
--------------
Tokens are approximated as ``len(text.split())`` (whitespace words).
This avoids a tokeniser dependency while remaining accurate enough for
~800-token target chunks.

Usage::

    chunker = SemanticChunker(chunk_size=800, overlap=150)
    chunks = chunker.chunk(document)
"""

from __future__ import annotations

import logging
import re
import uuid
from typing import List

from app.retrieval.models import Chunk, Document

logger = logging.getLogger(__name__)

# Markdown heading line: ``# …``, ``## …``, ``### …``
_HEADING_RE = re.compile(r"^#{1,3}\s+.+", re.MULTILINE)

# Speaker-turn line: ``Name (HH:MM:SS):``  or  ``(HH:MM:SS):``
_SPEAKER_RE = re.compile(r"^.{0,80}\(\d{2}:\d{2}:\d{2}\):\s*$", re.MULTILINE)


def _token_count(text: str) -> int:
    """Approximate token count using whitespace word splits."""
    return len(text.split())


def _split_on_boundaries(text: str) -> List[str]:
    """
    Split *text* into fine-grained semantic blocks using three levels of
    boundary detection (headings → speaker turns → paragraphs).

    Returns a non-empty list of stripped non-empty string fragments.
    """
    # Level 1: section headings
    section_parts: List[str] = re.split(r"(?m)^(#{1,3}\s+.+)$", text)

    blocks: List[str] = []
    for part in section_parts:
        if not part.strip():
            continue

        # Level 2: speaker turns within each section
        speaker_parts = re.split(
            r"(?m)^(.{0,80}\(\d{2}:\d{2}:\d{2}\):\s*)$", part
        )

        for sp in speaker_parts:
            if not sp.strip():
                continue

            # Level 3: paragraphs (blank lines)
            for para in sp.split("\n\n"):
                stripped = para.strip()
                if stripped:
                    blocks.append(stripped)

    return blocks if blocks else [text.strip()]


class SemanticChunker:
    """
    Splits a :class:`~app.retrieval.models.Document` into
    :class:`~app.retrieval.models.Chunk` objects with token-aware
    overlap.

    Parameters
    ----------
    chunk_size :
        Target maximum number of tokens per chunk.  Defaults to 800.
    overlap :
        Number of tokens to overlap between consecutive chunks.
        Defaults to 150.
    """

    def __init__(self, chunk_size: int = 800, overlap: int = 150) -> None:
        if overlap >= chunk_size:
            raise ValueError("overlap must be less than chunk_size")
        self.chunk_size = chunk_size
        self.overlap = overlap

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def chunk(self, document: Document) -> List[Chunk]:
        """
        Chunk *document* into :class:`Chunk` objects.

        Parameters
        ----------
        document :
            A parsed and cleaned :class:`Document`.

        Returns
        -------
        List[Chunk]
            Ordered list of chunks; guaranteed non-empty as long as
            ``document.content`` is non-empty.
        """
        if not document.content.strip():
            logger.warning(
                "Document '%s' has empty content — no chunks produced.", document.id
            )
            return []

        blocks = _split_on_boundaries(document.content)
        raw_chunks = self._assemble_chunks(blocks)

        chunks: List[Chunk] = []
        meta = document.metadata

        for i, text in enumerate(raw_chunks, start=1):
            chunk = Chunk(
                chunk_id=str(uuid.uuid4()),
                episode_id=document.id,
                chunk_number=i,
                guest=meta.guest,
                title=meta.title,
                topics=list(meta.topics),
                publish_date=meta.publish_date,
                youtube_url=meta.youtube_url,
                text=text,
            )
            chunks.append(chunk)

        logger.debug(
            "SemanticChunker: episode='%s'  blocks=%d  chunks=%d",
            document.id,
            len(blocks),
            len(chunks),
        )
        return chunks

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _assemble_chunks(self, blocks: List[str]) -> List[str]:
        """
        Greedily assemble *blocks* into chunks up to :attr:`chunk_size`
        tokens, with :attr:`overlap` tokens carried forward.

        A single block that exceeds :attr:`chunk_size` is hard-split at
        the word level to avoid losing content.
        """
        chunks: List[str] = []
        current_tokens: List[str] = []
        current_count = 0

        for block in blocks:
            block_words = block.split()
            block_count = len(block_words)

            # A block by itself is already too big — hard-split it
            if block_count > self.chunk_size:
                # Flush current buffer first
                if current_tokens:
                    chunks.append(" ".join(current_tokens))
                    current_tokens = []
                    current_count = 0

                sub_chunks = self._hard_split(block_words)
                # Carry overlap from last sub_chunk into current buffer
                for sc in sub_chunks[:-1]:
                    chunks.append(sc)
                last_words = sub_chunks[-1].split() if sub_chunks else []
                # Seed overlap from last sub_chunk
                overlap_words = last_words[-self.overlap:] if last_words else []
                current_tokens = overlap_words
                current_count = len(current_tokens)
                continue

            # Adding this block would exceed the target — flush
            if current_count + block_count > self.chunk_size and current_tokens:
                chunks.append(" ".join(current_tokens))
                # Retain overlap from current chunk
                overlap_words = current_tokens[-self.overlap:]
                current_tokens = list(overlap_words)
                current_count = len(current_tokens)

            current_tokens.extend(block_words)
            current_count += block_count

        # Flush remaining tokens
        if current_tokens:
            chunks.append(" ".join(current_tokens))

        return [c.strip() for c in chunks if c.strip()]

    def _hard_split(self, words: List[str]) -> List[str]:
        """
        Hard-split a word list that is larger than :attr:`chunk_size`
        into chunks of exactly :attr:`chunk_size` words with
        :attr:`overlap` carry-forward.
        """
        chunks: List[str] = []
        step = self.chunk_size - self.overlap
        for start in range(0, len(words), step):
            end = start + self.chunk_size
            chunk = " ".join(words[start:end])
            chunks.append(chunk)
            if end >= len(words):
                break
        return chunks
