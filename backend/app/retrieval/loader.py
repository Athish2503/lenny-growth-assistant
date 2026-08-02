"""
TranscriptLoader — Step 1 of the ingestion pipeline.

Responsibility:
    Recursively scan ``data/transcripts/episodes/`` for every
    ``transcript.md`` file, skip hidden files, and return a sorted list
    of :class:`pathlib.Path` objects.

Usage::

    loader = TranscriptLoader(episodes_dir=Path("data/transcripts/episodes"))
    paths = loader.discover()
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)


class TranscriptLoader:
    """
    Discovers transcript markdown files beneath an *episodes* directory.

    Parameters
    ----------
    episodes_dir :
        Root directory that contains one sub-folder per guest episode,
        each with a ``transcript.md`` file.  Defaults to
        ``data/transcripts/episodes`` relative to the current working
        directory.
    filename :
        Target filename inside each episode folder.  Defaults to
        ``"transcript.md"``.
    """

    def __init__(
        self,
        episodes_dir: Optional[Path] = None,
        filename: str = "transcript.md",
    ) -> None:
        self.episodes_dir: Path = (
            episodes_dir
            if episodes_dir is not None
            else Path("data/transcripts/episodes")
        )
        self.filename = filename

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def discover(self) -> List[Path]:
        """
        Recursively find all transcript files.

        Returns
        -------
        List[Path]
            Sorted list of absolute paths to every ``transcript.md``
            found under :attr:`episodes_dir`.

        Raises
        ------
        FileNotFoundError
            If :attr:`episodes_dir` does not exist.
        """
        if not self.episodes_dir.exists():
            raise FileNotFoundError(
                f"Episodes directory not found: {self.episodes_dir.resolve()}"
            )

        paths: List[Path] = []

        for path in sorted(self.episodes_dir.rglob(self.filename)):
            # Skip hidden files / directories (names starting with '.')
            if any(part.startswith(".") for part in path.parts):
                logger.debug("Skipping hidden path: %s", path)
                continue
            paths.append(path.resolve())

        logger.info(
            "TranscriptLoader: discovered %d transcripts in '%s'",
            len(paths),
            self.episodes_dir.resolve(),
        )
        return paths
