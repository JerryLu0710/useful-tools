"""Shared pytest fixtures for the useful_tools project.

This conftest.py provides common fixtures that can be used across all test modules.
"""

from pathlib import Path

import pytest


@pytest.fixture
def temp_dir(tmp_path: Path) -> Path:
    """Provide a temporary directory for tests.

    This is a convenience wrapper around pytest's tmp_path fixture.
    """
    return tmp_path


@pytest.fixture
def sample_env_vars(monkeypatch):
    """Set up sample environment variables for testing config modules.

    Use this fixture when testing modules that read from environment variables.
    """
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("LOG_TO_FILE", "false")
    monkeypatch.setenv("LOG_TO_CONSOLE", "true")
    yield
    # Cleanup is automatic with monkeypatch


@pytest.fixture
def mock_history_file(tmp_path: Path) -> Path:
    """Create a temporary history file with sample entries.

    Returns the path to the history file.
    """
    import json

    history_file = tmp_path / "test_history.jsonl"
    entries = [
        {
            "title": "Test Anime [01]",
            "anime_series": "Test Anime",
            "downloaded_at": "2026-01-17T12:00:00+08:00",
        },
        {
            "title": "Test Anime [02]",
            "anime_series": "Test Anime",
            "downloaded_at": "2026-01-17T12:30:00+08:00",
        },
    ]

    with open(history_file, "w", encoding="utf-8") as f:
        for entry in entries:
            f.write(json.dumps(entry) + "\n")

    return history_file
