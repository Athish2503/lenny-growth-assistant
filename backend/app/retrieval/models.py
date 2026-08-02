"""
Pydantic models for the transcript ingestion pipeline and retrieval layer.

This module defines the shared data contracts used across:
  - TranscriptLoader
  - TranscriptParser
  - TopicParser
  - TranscriptCleaner
  - SemanticChunker
  - Pipeline

It also preserves the RetrievalResult dataclass consumed by the retrieval layer.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Retrieval layer model (preserved from previous milestone)
# ---------------------------------------------------------------------------


@dataclass
class RetrievalResult:
    """
    Represents a single document/chunk retrieved by a retrieval algorithm.
    """

    doc_id: str
    chunk_id: str
    content: str
    score: float
    metadata: Dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Ingestion pipeline models
# ---------------------------------------------------------------------------


class EpisodeMetadata(BaseModel):
    """
    Structured metadata extracted from a transcript's YAML frontmatter.

    All fields are Optional to tolerate malformed or incomplete transcripts.
    """

    guest: Optional[str] = None
    title: Optional[str] = None
    youtube_url: Optional[str] = None
    video_id: Optional[str] = None
    publish_date: Optional[str] = None          # kept as str for flexibility
    description: Optional[str] = None
    duration: Optional[str] = None
    duration_seconds: Optional[float] = None
    view_count: Optional[int] = None
    channel: Optional[str] = None
    keywords: List[str] = Field(default_factory=list)

    # Enrichment field populated after topic parsing
    topics: List[str] = Field(default_factory=list)


class Document(BaseModel):
    """
    An in-memory representation of a single parsed transcript file.

    Fields
    ------
    id :
        Unique episode identifier derived from the folder slug
        (e.g. ``"brian-chesky"``).
    source_path :
        Absolute path to the transcript file on disk.
    metadata :
        Structured frontmatter + enriched fields.
    content :
        Raw (or cleaned) transcript body, *excluding* the YAML block.
    """

    id: str
    source_path: str
    metadata: EpisodeMetadata = Field(default_factory=EpisodeMetadata)
    content: str = ""


class Chunk(BaseModel):
    """
    A single text chunk ready for embedding.

    Every chunk inherits the episode-level metadata so that retrieval
    results carry full context without a secondary lookup.
    """

    chunk_id: str
    episode_id: str
    chunk_number: int

    # Denormalised episode fields for fast retrieval access
    guest: Optional[str] = None
    title: Optional[str] = None
    topics: List[str] = Field(default_factory=list)
    publish_date: Optional[str] = None
    youtube_url: Optional[str] = None

    text: str = ""


class TopicMap(BaseModel):
    """
    Mapping from guest name → list of topic labels.

    Example::

        {
            "Brian Chesky": ["Leadership", "Product Management", "Hiring"]
        }
    """

    mapping: Dict[str, List[str]] = Field(default_factory=dict)

    def get_topics(self, guest_name: str) -> List[str]:
        """
        Return topics for *guest_name*, trying exact match first then
        case-insensitive fallback.
        """
        if guest_name in self.mapping:
            return self.mapping[guest_name]
        lower = guest_name.lower()
        for key, topics in self.mapping.items():
            if key.lower() == lower:
                return topics
        return []

    def add(self, guest_name: str, topic: str) -> None:
        """Add *topic* to *guest_name*, creating the entry if absent."""
        if guest_name not in self.mapping:
            self.mapping[guest_name] = []
        if topic not in self.mapping[guest_name]:
            self.mapping[guest_name].append(topic)
