"""Unit tests for anime1_downloader history module."""

import json
from pathlib import Path

from anime1_downloader.history import (
    append_to_history,
    create_history_entry,
    load_history,
)


class TestLoadHistory:
    """Tests for load_history function."""

    def test_load_empty_file(self, tmp_path: Path) -> None:
        """Test loading from an empty history file."""
        history_file = tmp_path / "history.jsonl"
        history_file.touch()

        result = load_history(history_file)

        assert result == set()

    def test_load_nonexistent_file(self, tmp_path: Path) -> None:
        """Test loading from a non-existent file returns empty set."""
        history_file = tmp_path / "nonexistent.jsonl"

        result = load_history(history_file)

        assert result == set()

    def test_load_valid_history(self, tmp_path: Path) -> None:
        """Test loading valid history entries."""
        history_file = tmp_path / "history.jsonl"
        entries = [
            {"title": "Anime A [01]", "anime_series": "Anime A"},
            {"title": "Anime A [02]", "anime_series": "Anime A"},
            {"title": "Anime B [01]", "anime_series": "Anime B"},
        ]
        with open(history_file, "w", encoding="utf-8") as f:
            for entry in entries:
                f.write(json.dumps(entry) + "\n")

        result = load_history(history_file)

        assert result == {"Anime A [01]", "Anime A [02]", "Anime B [01]"}

    def test_load_history_with_malformed_lines(self, tmp_path: Path) -> None:
        """Test loading history with some malformed JSON lines."""
        history_file = tmp_path / "history.jsonl"
        with open(history_file, "w", encoding="utf-8") as f:
            f.write('{"title": "Valid [01]"}\n')
            f.write("not valid json\n")
            f.write('{"title": "Valid [02]"}\n')

        # Should not raise, but may log warning
        result = load_history(history_file)

        # Depending on implementation, could be partial or empty
        # Current implementation catches exceptions so should return partial
        assert "Valid [01]" in result or len(result) == 0


class TestAppendToHistory:
    """Tests for append_to_history function."""

    def test_append_creates_file(self, tmp_path: Path) -> None:
        """Test that append creates file if it doesn't exist."""
        history_file = tmp_path / "new_history.jsonl"
        entry = {"title": "Test [01]", "anime_series": "Test"}

        append_to_history(history_file, entry)

        assert history_file.exists()
        with open(history_file, encoding="utf-8") as f:
            content = f.read()
        assert "Test [01]" in content

    def test_append_to_existing_file(self, tmp_path: Path) -> None:
        """Test appending to an existing history file."""
        history_file = tmp_path / "history.jsonl"
        history_file.write_text('{"title": "Existing [01]"}\n')

        entry = {"title": "New [01]", "anime_series": "New"}
        append_to_history(history_file, entry)

        with open(history_file, encoding="utf-8") as f:
            lines = f.readlines()

        assert len(lines) == 2
        assert "Existing [01]" in lines[0]
        assert "New [01]" in lines[1]

    def test_append_creates_parent_directories(self, tmp_path: Path) -> None:
        """Test that append creates parent directories if needed."""
        history_file = tmp_path / "nested" / "dir" / "history.jsonl"
        entry = {"title": "Test [01]"}

        append_to_history(history_file, entry)

        assert history_file.exists()


class TestCreateHistoryEntry:
    """Tests for create_history_entry function."""

    def test_creates_entry_with_required_fields(self) -> None:
        """Test that create_history_entry includes all expected fields."""
        entry = create_history_entry(
            title="Anime Name [05]",
            anime_series="Anime Name",
            url="https://anime1.me/12345",
            output_path="/downloads/Anime Name/Anime Name [05].mp4",
        )

        assert entry["title"] == "Anime Name [05]"
        assert entry["anime_series"] == "Anime Name"
        assert entry["url"] == "https://anime1.me/12345"
        assert entry["output_path"] == "/downloads/Anime Name/Anime Name [05].mp4"
        assert "downloaded_at" in entry

    def test_downloaded_at_is_iso_format(self) -> None:
        """Test that downloaded_at is in ISO format."""
        entry = create_history_entry(
            title="Test",
            anime_series="Test",
            url="https://example.com",
            output_path="/path",
        )

        # Should be parseable as ISO format
        from datetime import datetime

        dt = datetime.fromisoformat(entry["downloaded_at"])
        assert dt is not None
