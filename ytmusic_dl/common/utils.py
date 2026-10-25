import json
import re
from pathlib import Path
from typing import Any

from ytmusic_dl.common.logger import logger

# Regex to extract YouTube ID from a URL
# It looks for various youtube URL formats and captures the 11-character ID.
YOUTUBE_ID_REGEX = re.compile(r"(?:v=|\/|youtu\.be\/|embed\/|shorts\/)([a-zA-Z0-9_-]{11})")

# Every container a downloaded track can end up in, whatever --format asked for.
AUDIO_FILE_EXTENSIONS = frozenset(
    {
        ".aac",
        ".flac",
        ".m4a",
        ".m4b",
        ".mka",
        ".mp3",
        ".mp4",
        ".ogg",
        ".opus",
        ".wav",
        ".webm",
    }
)


def load_history_entries(history_path: Path) -> list[dict]:
    """Read the download history file, keeping every entry after a damaged line.

    Later lines supersede earlier ones for the same video ID, which is how a
    rename is recorded without rewriting an append-only file.
    """
    entries: list[dict] = []
    if not history_path.exists():
        return entries

    try:
        with open(history_path, encoding="utf-8") as f:
            for number, line in enumerate(f, 1):
                if not line.strip():
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError as e:
                    logger.warning(f"Could not parse line {number} of '{history_path}': {e}")
                    continue
                if entry.get("id"):
                    entries.append(entry)
    except Exception as e:
        logger.warning(f"Error loading history file '{history_path}': {e}")

    return entries


def tag_values(audio_file: Any, key: str) -> list[str]:
    """Return every text value stored under ``key`` of a mutagen tag object.

    mutagen raises for keys a container does not support at all, so one try
    around a whole key scan stops at the first unsupported key.
    """
    try:
        values = audio_file[key]
    except Exception:
        return []
    if not isinstance(values, list):
        values = [values]
    texts = [str(value).strip() for value in values]
    return [text for text in texts if text]


def extract_artist(info: dict) -> tuple[str, str]:
    """
    Extract artist name with priority: artist > channel > uploader.

    Args:
        info: Video info dictionary from yt-dlp

    Returns:
        Tuple of (artist_name, source)
    """
    if info.get("artist"):
        return info["artist"], "artist"
    elif info.get("channel"):
        return info["channel"], "channel"
    else:
        return info.get("uploader", "Unknown"), "uploader"
