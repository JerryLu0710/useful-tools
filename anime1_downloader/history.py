"""Download history management for anime1_downloader.

This module provides functions for tracking downloaded anime episodes
in a JSONL (JSON Lines) format file.
"""

import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from logger_setup import get_logger

logger = get_logger(__name__, "anime1_downloader")

# Use local timezone for timestamps
LOCAL_TZ = ZoneInfo("Asia/Hong_Kong")


def load_history(history_path: Path) -> set[str]:
    """Load previously downloaded episode titles from JSONL history file.

    Args:
        history_path: Path to JSONL history file

    Returns:
        Set of episode titles that have been downloaded
    """
    downloaded_titles = set()

    if not history_path.exists():
        return downloaded_titles

    try:
        with open(history_path, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    entry = json.loads(line)
                    # Use title as unique identifier
                    downloaded_titles.add(entry.get("title", ""))
    except Exception as e:
        logger.warning(f"Error loading history file: {e}")

    return downloaded_titles


def append_to_history(history_path: Path, entry: dict) -> None:
    """Append a new download entry to JSONL history file.

    Args:
        history_path: Path to JSONL history file
        entry: Dictionary containing download metadata
    """
    # Ensure directory exists
    history_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(history_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception as e:
        logger.error(f"Failed to write to history file: {e}")


def create_history_entry(
    title: str,
    anime_series: str,
    url: str,
    output_path: str,
) -> dict:
    """Create a history entry dictionary.

    Args:
        title: Episode title (e.g., "Anime Name [01]")
        anime_series: Anime series name
        url: Original page URL
        output_path: Path where the video was saved

    Returns:
        Dictionary with download metadata
    """
    return {
        "title": title,
        "anime_series": anime_series,
        "url": url,
        "output_path": output_path,
        "downloaded_at": datetime.now(LOCAL_TZ).isoformat(),
    }
