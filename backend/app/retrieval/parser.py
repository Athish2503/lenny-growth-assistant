"""
TranscriptParser — Step 2 of the ingestion pipeline.

Responsibility:
    Read a transcript file, parse the YAML frontmatter, extract the body
    text (everything after the closing ``---``), and return a
    :class:`~app.retrieval.models.Document`.

Usage::

    parser = TranscriptParser()
    document = parser.parse(Path("data/transcripts/episodes/brian-chesky/transcript.md"))
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

from app.retrieval.models import Document, EpisodeMetadata

logger = logging.getLogger(__name__)

# Regex that matches the YAML frontmatter block at the start of a file.
# Group 1 captures the raw YAML content between the two ``---`` fences.
_FRONTMATTER_RE = re.compile(
    r"^---[ \t]*\r?\n(.*?)\r?\n---[ \t]*\r?\n",
    re.DOTALL,
)


class TranscriptParser:
    """
    Parses a single transcript markdown file into a :class:`Document`.

    The parser is resilient: missing or malformed frontmatter fields are
    silently ignored and the document is still returned with whatever
    metadata could be recovered.

    Parameters
    ----------
    encoding :
        File encoding used when reading transcript files.
    """

    def __init__(self, encoding: str = "utf-8") -> None:
        self.encoding = encoding

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def parse(self, path: Path) -> Document:
        """
        Parse *path* and return a :class:`Document`.

        Parameters
        ----------
        path :
            Absolute (or relative) path to a ``transcript.md`` file.

        Returns
        -------
        Document
            Populated document with metadata and raw body text.

        Raises
        ------
        FileNotFoundError
            If *path* does not exist.
        """
        path = path.resolve()
        if not path.is_file():
            raise FileNotFoundError(f"Transcript file not found: {path}")

        raw = path.read_text(encoding=self.encoding)

        # Derive episode id from the parent directory name (the slug)
        episode_id = path.parent.name

        metadata = self._parse_frontmatter(raw, episode_id=episode_id)
        content = self._extract_body(raw)

        doc = Document(
            id=episode_id,
            source_path=str(path),
            metadata=metadata,
            content=content,
        )

        logger.debug("Parsed transcript: episode_id=%s  guest=%s", episode_id, metadata.guest)
        return doc

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _parse_frontmatter(self, raw: str, episode_id: str) -> EpisodeMetadata:
        """
        Extract and parse YAML frontmatter from *raw* file content.

        Unknown YAML keys are silently ignored by Pydantic.
        """
        match = _FRONTMATTER_RE.match(raw)
        if not match:
            logger.warning(
                "No YAML frontmatter found for episode '%s'; using defaults.", episode_id
            )
            return EpisodeMetadata()

        yaml_text = match.group(1)
        try:
            data: Dict[str, Any] = yaml.safe_load(yaml_text) or {}
        except yaml.YAMLError as exc:
            logger.warning(
                "YAML parse error for episode '%s': %s — using defaults.", episode_id, exc
            )
            return EpisodeMetadata()

        if not isinstance(data, dict):
            return EpisodeMetadata()

        # Coerce publish_date to string (YAML may produce a date object)
        if "publish_date" in data and data["publish_date"] is not None:
            data["publish_date"] = str(data["publish_date"])

        # Pydantic ignores unrecognised keys (model has extra="ignore" behaviour
        # because we use model_config; here we just pass known keys)
        known_keys = EpisodeMetadata.model_fields.keys()
        filtered = {k: v for k, v in data.items() if k in known_keys}

        try:
            return EpisodeMetadata(**filtered)
        except Exception as exc:
            logger.warning(
                "Failed to build EpisodeMetadata for '%s': %s", episode_id, exc
            )
            return EpisodeMetadata()

    def _extract_body(self, raw: str) -> str:
        """
        Return the transcript body (everything after the YAML block).

        If no frontmatter exists the entire file content is returned.
        """
        match = _FRONTMATTER_RE.match(raw)
        if match:
            return raw[match.end():]
        return raw
