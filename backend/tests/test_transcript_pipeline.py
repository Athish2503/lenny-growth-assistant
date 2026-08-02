"""
Unit tests for the transcript ingestion pipeline.

Tests cover:
    - TranscriptLoader  (Step 1)
    - TranscriptParser  (Step 2)
    - TranscriptCleaner (Step 5)
    - SemanticChunker   (Step 6)

All tests are self-contained and use pytest's tmp_path fixture so they
never touch production data.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.retrieval.chunker import SemanticChunker
from app.retrieval.cleaner import TranscriptCleaner
from app.retrieval.loader import TranscriptLoader
from app.retrieval.models import Document, EpisodeMetadata
from app.retrieval.parser import TranscriptParser
from app.retrieval.topic_parser import TopicParser


# ---------------------------------------------------------------------------
# Helpers / fixtures
# ---------------------------------------------------------------------------

SAMPLE_FRONTMATTER = """\
---
guest: Brian Chesky
title: Brian Chesky's new playbook
youtube_url: https://www.youtube.com/watch?v=4ef0juAMqoE
video_id: 4ef0juAMqoE
publish_date: 2023-11-12
description: 'Brian Chesky is the co-founder and CEO of Airbnb.'
duration_seconds: 4408.0
duration: '1:13:28'
view_count: 381905
channel: Lenny's Podcast
keywords:
- growth
- leadership
---
"""

SAMPLE_BODY = """\
# Brian Chesky's new playbook

## Transcript

Brian Chesky (00:00:00):
Way too many founders apologize for how they want to run the company.
They find some midpoint and that's a good way to make everyone miserable.

Lenny (00:01:01):
Today my guest is Brian Chesky, CEO of Airbnb.

(00:01:27):
In our conversation Brian shares how he runs Airbnb now.

Brian Chesky (00:05:04):
I basically got involved in every single detail and told leaders
that leaders are in the details. There's a difference between
micromanagement and being in the details.
"""

SAMPLE_TRANSCRIPT = SAMPLE_FRONTMATTER + SAMPLE_BODY


@pytest.fixture
def episode_dir(tmp_path: Path) -> Path:
    """Create a fake episodes/ directory tree with two transcripts."""
    (tmp_path / "episodes" / "brian-chesky").mkdir(parents=True)
    (tmp_path / "episodes" / "ada-chen-rekhi").mkdir(parents=True)

    (tmp_path / "episodes" / "brian-chesky" / "transcript.md").write_text(
        SAMPLE_TRANSCRIPT, encoding="utf-8"
    )
    (tmp_path / "episodes" / "ada-chen-rekhi" / "transcript.md").write_text(
        SAMPLE_TRANSCRIPT.replace("Brian Chesky", "Ada Chen Rekhi"),
        encoding="utf-8",
    )
    return tmp_path / "episodes"


@pytest.fixture
def index_dir(tmp_path: Path) -> Path:
    """Create a fake index/ directory with two topic files and a README."""
    idx = tmp_path / "index"
    idx.mkdir()

    (idx / "README.md").write_text("# Readme\nIgnore this.\n", encoding="utf-8")

    (idx / "leadership.md").write_text(
        "# leadership\n\nEpisodes:\n\n"
        "- [Brian Chesky](../episodes/brian-chesky/transcript.md)\n"
        "- [Ada Chen Rekhi](../episodes/ada-chen-rekhi/transcript.md)\n",
        encoding="utf-8",
    )
    (idx / "product-management.md").write_text(
        "# product management\n\nEpisodes:\n\n"
        "- [Brian Chesky](../episodes/brian-chesky/transcript.md)\n",
        encoding="utf-8",
    )
    return idx


# ---------------------------------------------------------------------------
# TranscriptLoader tests
# ---------------------------------------------------------------------------


class TestTranscriptLoader:
    def test_discovers_all_transcripts(self, episode_dir: Path) -> None:
        loader = TranscriptLoader(episodes_dir=episode_dir)
        paths = loader.discover()
        assert len(paths) == 2

    def test_returns_sorted_absolute_paths(self, episode_dir: Path) -> None:
        loader = TranscriptLoader(episodes_dir=episode_dir)
        paths = loader.discover()
        names = [p.parent.name for p in paths]
        assert names == sorted(names), "Paths should be lexicographically sorted"
        for p in paths:
            assert p.is_absolute(), "Paths should be absolute"

    def test_skips_hidden_files(self, tmp_path: Path) -> None:
        ep = tmp_path / "episodes"
        ep.mkdir()
        (ep / "valid-guest").mkdir()
        (ep / "valid-guest" / "transcript.md").write_text("---\nguest: X\n---\nbody")
        (ep / ".hidden-guest").mkdir()
        (ep / ".hidden-guest" / "transcript.md").write_text("---\nguest: Y\n---\nbody")

        loader = TranscriptLoader(episodes_dir=ep)
        paths = loader.discover()
        assert len(paths) == 1
        assert ".hidden-guest" not in str(paths[0])

    def test_raises_on_missing_directory(self, tmp_path: Path) -> None:
        loader = TranscriptLoader(episodes_dir=tmp_path / "does_not_exist")
        with pytest.raises(FileNotFoundError):
            loader.discover()

    def test_returns_empty_list_for_no_transcripts(self, tmp_path: Path) -> None:
        ep = tmp_path / "episodes"
        ep.mkdir()
        loader = TranscriptLoader(episodes_dir=ep)
        assert loader.discover() == []


# ---------------------------------------------------------------------------
# TranscriptParser tests
# ---------------------------------------------------------------------------


class TestTranscriptParser:
    def test_parses_frontmatter_fields(self, episode_dir: Path) -> None:
        path = episode_dir / "brian-chesky" / "transcript.md"
        parser = TranscriptParser()
        doc = parser.parse(path)

        assert doc.metadata.guest == "Brian Chesky"
        assert doc.metadata.title == "Brian Chesky's new playbook"
        assert doc.metadata.video_id == "4ef0juAMqoE"
        assert doc.metadata.publish_date == "2023-11-12"
        assert doc.metadata.view_count == 381905
        assert doc.metadata.channel == "Lenny's Podcast"

    def test_episode_id_from_folder_name(self, episode_dir: Path) -> None:
        path = episode_dir / "brian-chesky" / "transcript.md"
        doc = TranscriptParser().parse(path)
        assert doc.id == "brian-chesky"

    def test_body_excludes_frontmatter(self, episode_dir: Path) -> None:
        path = episode_dir / "brian-chesky" / "transcript.md"
        doc = TranscriptParser().parse(path)
        assert "---" not in doc.content.split("\n")[0]
        assert "Brian Chesky's new playbook" in doc.content

    def test_graceful_on_missing_frontmatter(self, tmp_path: Path) -> None:
        no_fm = tmp_path / "no-fm"
        no_fm.mkdir()
        f = no_fm / "transcript.md"
        f.write_text("Just a body with no YAML.", encoding="utf-8")
        doc = TranscriptParser().parse(f)
        assert doc.metadata.guest is None
        assert "body with no YAML" in doc.content

    def test_raises_on_missing_file(self, tmp_path: Path) -> None:
        parser = TranscriptParser()
        with pytest.raises(FileNotFoundError):
            parser.parse(tmp_path / "ghost" / "transcript.md")

    def test_publish_date_coerced_to_string(self, tmp_path: Path) -> None:
        ep = tmp_path / "date-test"
        ep.mkdir()
        f = ep / "transcript.md"
        f.write_text(
            "---\nguest: Test\npublish_date: 2023-05-01\n---\nbody",
            encoding="utf-8",
        )
        doc = TranscriptParser().parse(f)
        assert isinstance(doc.metadata.publish_date, str)


# ---------------------------------------------------------------------------
# TranscriptCleaner tests
# ---------------------------------------------------------------------------


class TestTranscriptCleaner:
    def test_removes_trailing_whitespace(self) -> None:
        cleaner = TranscriptCleaner()
        result = cleaner.clean("Hello   \nWorld   \n")
        for line in result.split("\n"):
            assert not line.endswith(" "), f"Trailing space on line: {repr(line)}"

    def test_collapses_excess_blank_lines(self) -> None:
        cleaner = TranscriptCleaner(max_blank_lines=2)
        text = "Para A\n\n\n\n\nPara B"
        result = cleaner.clean(text)
        assert "\n\n\n" not in result

    def test_normalises_line_endings(self) -> None:
        cleaner = TranscriptCleaner()
        result = cleaner.clean("line1\r\nline2\r\nline3")
        assert "\r" not in result

    def test_unicode_nfc_normalisation(self) -> None:
        cleaner = TranscriptCleaner()
        # Compose: é as NFD (two codepoints) → should become NFC (one codepoint)
        nfd = "e\u0301"  # e + combining acute accent
        result = cleaner.clean(nfd)
        assert result == "\xe9"  # é in NFC

    def test_preserves_speaker_names(self) -> None:
        cleaner = TranscriptCleaner()
        text = "Brian Chesky (00:00:00):\nWay too many founders.\n"
        result = cleaner.clean(text)
        assert "Brian Chesky" in result
        assert "(00:00:00):" in result

    def test_collapses_internal_spaces(self) -> None:
        cleaner = TranscriptCleaner()
        result = cleaner.clean("Hello  world   again")
        assert "  " not in result

    def test_empty_string_returns_empty(self) -> None:
        cleaner = TranscriptCleaner()
        assert cleaner.clean("") == ""


# ---------------------------------------------------------------------------
# SemanticChunker tests
# ---------------------------------------------------------------------------


class TestSemanticChunker:
    def _make_doc(self, content: str, guest: str = "Test Guest") -> Document:
        meta = EpisodeMetadata(
            guest=guest,
            title="Test Episode",
            publish_date="2023-01-01",
            youtube_url="https://youtu.be/test",
            topics=["Leadership"],
        )
        return Document(id="test-guest", source_path="/fake/path", metadata=meta, content=content)

    def test_returns_chunks_for_normal_content(self) -> None:
        chunker = SemanticChunker(chunk_size=100, overlap=20)
        doc = self._make_doc(SAMPLE_BODY)
        chunks = chunker.chunk(doc)
        assert len(chunks) >= 1

    def test_chunks_inherit_episode_metadata(self) -> None:
        chunker = SemanticChunker(chunk_size=100, overlap=20)
        doc = self._make_doc(SAMPLE_BODY)
        chunks = chunker.chunk(doc)
        for c in chunks:
            assert c.episode_id == "test-guest"
            assert c.guest == "Test Guest"
            assert c.title == "Test Episode"
            assert "Leadership" in c.topics
            assert c.youtube_url == "https://youtu.be/test"

    def test_chunk_numbers_are_sequential(self) -> None:
        chunker = SemanticChunker(chunk_size=50, overlap=10)
        doc = self._make_doc(SAMPLE_BODY * 3)
        chunks = chunker.chunk(doc)
        for i, c in enumerate(chunks, start=1):
            assert c.chunk_number == i

    def test_each_chunk_has_unique_id(self) -> None:
        chunker = SemanticChunker(chunk_size=50, overlap=10)
        doc = self._make_doc(SAMPLE_BODY)
        chunks = chunker.chunk(doc)
        ids = [c.chunk_id for c in chunks]
        assert len(ids) == len(set(ids)), "chunk_ids must be unique"

    def test_empty_content_returns_no_chunks(self) -> None:
        chunker = SemanticChunker()
        doc = self._make_doc("")
        assert chunker.chunk(doc) == []

    def test_chunk_size_respected(self) -> None:
        """No chunk should significantly exceed the target size (word count)."""
        chunk_size = 80
        chunker = SemanticChunker(chunk_size=chunk_size, overlap=15)
        # Create content long enough to force multiple chunks
        long_body = (SAMPLE_BODY + "\n") * 10
        doc = self._make_doc(long_body)
        chunks = chunker.chunk(doc)
        assert len(chunks) > 1
        for c in chunks:
            words = len(c.text.split())
            # Allow a 25% tolerance for the greedy merge logic
            assert words <= chunk_size * 1.25, (
                f"Chunk has {words} words — exceeds {chunk_size * 1.25}"
            )

    def test_invalid_overlap_raises(self) -> None:
        with pytest.raises(ValueError):
            SemanticChunker(chunk_size=100, overlap=100)


# ---------------------------------------------------------------------------
# TopicParser tests
# ---------------------------------------------------------------------------


class TestTopicParser:
    def test_builds_topic_map(self, index_dir: Path) -> None:
        parser = TopicParser(index_dir=index_dir)
        topic_map = parser.parse()
        assert "Brian Chesky" in topic_map.mapping
        topics = topic_map.get_topics("Brian Chesky")
        assert "Leadership" in topics
        assert "Product Management" in topics

    def test_skips_readme(self, index_dir: Path) -> None:
        parser = TopicParser(index_dir=index_dir)
        topic_map = parser.parse()
        # README should not be added as a topic label
        all_topics = {t for topics in topic_map.mapping.values() for t in topics}
        assert "Readme" not in all_topics

    def test_guest_not_in_index_returns_empty(self, index_dir: Path) -> None:
        parser = TopicParser(index_dir=index_dir)
        topic_map = parser.parse()
        assert topic_map.get_topics("Nonexistent Guest") == []

    def test_raises_on_missing_index_dir(self, tmp_path: Path) -> None:
        parser = TopicParser(index_dir=tmp_path / "no_index")
        with pytest.raises(FileNotFoundError):
            parser.parse()
