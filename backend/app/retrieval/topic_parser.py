"""
TopicParser — Step 3 of the ingestion pipeline.

Responsibility:
    Parse every ``*.md`` file under ``data/transcripts/index/`` (skipping
    ``README.md``) and build a :class:`~app.retrieval.models.TopicMap`
    that maps guest names to their associated topic labels.

Each index file follows the pattern::

    # <topic-label>

    Episodes discussing **<topic-label>**:

    - [Guest Name](../episodes/<slug>/transcript.md)
    - ...

The parser is format-resilient: it extracts the topic label from the H1
heading and guest names from any Markdown link whose URL pattern matches
the expected episode path.

Usage::

    parser = TopicParser(index_dir=Path("data/transcripts/index"))
    topic_map = parser.parse()
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import List, Optional

from app.retrieval.models import TopicMap

logger = logging.getLogger(__name__)

# Match a Markdown list-item link:  - [Guest Name](../episodes/slug/transcript.md)
_LINK_RE = re.compile(
    r"-\s+\[([^\]]+)\]\([^)]*episodes/[^/]+/transcript\.md\)",
    re.IGNORECASE,
)

# Match the H1 heading to derive the topic label
_H1_RE = re.compile(r"^#\s+(.+)", re.MULTILINE)


class TopicParser:
    """
    Parses topic index files and constructs a :class:`TopicMap`.

    Parameters
    ----------
    index_dir :
        Directory containing topic ``*.md`` files.  Defaults to
        ``data/transcripts/index``.
    encoding :
        File encoding.
    skip_files :
        Filenames (case-insensitive) to ignore.  Defaults to
        ``{"README.md"}``.
    """

    def __init__(
        self,
        index_dir: Optional[Path] = None,
        encoding: str = "utf-8",
        skip_files: Optional[set] = None,
    ) -> None:
        self.index_dir: Path = (
            index_dir
            if index_dir is not None
            else Path("data/transcripts/index")
        )
        self.encoding = encoding
        self.skip_files: set = (
            skip_files if skip_files is not None else {"README.md", "episodes.md"}
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def parse(self) -> TopicMap:
        """
        Parse all topic index files and return a populated
        :class:`TopicMap`.

        Returns
        -------
        TopicMap
            guest_name → [topic, …]

        Raises
        ------
        FileNotFoundError
            If :attr:`index_dir` does not exist.
        """
        if not self.index_dir.exists():
            raise FileNotFoundError(
                f"Index directory not found: {self.index_dir.resolve()}"
            )

        topic_map = TopicMap()
        files_processed = 0

        for md_file in sorted(self.index_dir.glob("*.md")):
            if md_file.name in self.skip_files:
                logger.debug("Skipping index file: %s", md_file.name)
                continue

            topic_label = self._parse_topic_file(md_file, topic_map)
            if topic_label:
                files_processed += 1

        logger.info(
            "TopicParser: processed %d topic index files from '%s'",
            files_processed,
            self.index_dir.resolve(),
        )
        return topic_map

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _parse_topic_file(self, path: Path, topic_map: TopicMap) -> Optional[str]:
        """
        Parse a single topic file and mutate *topic_map* in place.

        Returns the topic label on success, or ``None`` if the file
        could not be parsed.
        """
        try:
            content = path.read_text(encoding=self.encoding)
        except OSError as exc:
            logger.warning("Cannot read topic file '%s': %s", path, exc)
            return None

        # Derive label: prefer the H1 heading, fall back to filename stem
        h1_match = _H1_RE.search(content)
        if h1_match:
            raw_label = h1_match.group(1).strip()
        else:
            raw_label = path.stem.replace("-", " ")

        topic_label = self._normalise_label(raw_label)

        # Extract guest names from all Markdown links to episodes
        guests: List[str] = _LINK_RE.findall(content)
        for guest in guests:
            guest = guest.strip()
            if guest:
                topic_map.add(guest, topic_label)

        logger.debug(
            "TopicParser: '%s' → %d guests", topic_label, len(guests)
        )
        return topic_label

    @staticmethod
    def _normalise_label(raw: str) -> str:
        """
        Convert a raw heading string to a canonical topic label.

        E.g. ``"product management"`` → ``"Product Management"``
        """
        return raw.strip().title()
