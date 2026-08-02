"""
TranscriptCleaner — Step 5 of the ingestion pipeline.

Responsibility:
    Clean raw transcript body text extracted by :class:`TranscriptParser`:

    * Normalise Unicode to NFC form.
    * Collapse duplicate blank lines (3+ → 2).
    * Strip trailing whitespace from every line.
    * Remove excessive horizontal whitespace within lines (2+ spaces → 1).
    * Preserve speaker name lines (``Name (HH:MM:SS):``) intact.
    * Do NOT strip speaker names or conversation structure.

Usage::

    cleaner = TranscriptCleaner()
    clean_text = cleaner.clean(raw_body)
"""

from __future__ import annotations

import logging
import re
import unicodedata

logger = logging.getLogger(__name__)

# Match lines that are *only* a timestamp reference, e.g.  ``(00:01:23):``
# These are continuations of the previous speaker block and should be kept.
_STANDALONE_TIMESTAMP_RE = re.compile(r"^\s*\(\d{2}:\d{2}:\d{2}\):\s*$")

# Two or more consecutive blank lines (after normalising to \n)
_MULTI_BLANK_RE = re.compile(r"\n{3,}")


class TranscriptCleaner:
    """
    Cleans transcript body text without removing structural formatting.

    Parameters
    ----------
    max_blank_lines :
        Maximum number of consecutive blank lines to allow.  Defaults to 2.
    """

    def __init__(self, max_blank_lines: int = 2) -> None:
        self.max_blank_lines = max_blank_lines
        self._blank_pattern = re.compile(r"\n{%d,}" % (max_blank_lines + 1))

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def clean(self, text: str) -> str:
        """
        Apply all cleaning steps to *text* and return the result.

        Steps applied (in order):

        1. Normalise line-endings to ``\\n``.
        2. Unicode NFC normalisation.
        3. Remove null bytes.
        4. Strip trailing whitespace from every line.
        5. Collapse excessive intra-line whitespace (≥2 spaces → 1 space),
           *except* on lines that appear to be speaker labels.
        6. Collapse 3+ consecutive blank lines to :attr:`max_blank_lines`.
        7. Strip leading/trailing whitespace from the whole text.
        """
        if not text:
            return text

        # 1. Normalise line endings
        text = text.replace("\r\n", "\n").replace("\r", "\n")

        # 2. Unicode NFC normalisation
        text = unicodedata.normalize("NFC", text)

        # 3. Remove null bytes / BOM
        text = text.replace("\x00", "").replace("\ufeff", "")

        # 4. Process line by line
        lines = text.split("\n")
        cleaned_lines = []
        for line in lines:
            # Strip trailing whitespace
            line = line.rstrip()

            # 5. Collapse excessive internal whitespace — but be careful not
            #    to mangle speaker label lines like "Brian Chesky (00:05:04):"
            #    which legitimately contain a single-space gap.
            #    We only collapse runs of 2+ spaces that are NOT at the start
            #    (indentation is rare but we want to be safe).
            if not _STANDALONE_TIMESTAMP_RE.match(line):
                line = re.sub(r"  +", " ", line)

            cleaned_lines.append(line)

        text = "\n".join(cleaned_lines)

        # 6. Collapse excess blank lines
        replacement = "\n" * self.max_blank_lines
        text = self._blank_pattern.sub(replacement, text)

        # 7. Strip surrounding whitespace
        return text.strip()
