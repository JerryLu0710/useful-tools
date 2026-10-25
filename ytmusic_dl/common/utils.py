import re
from typing import Any

# Regex to extract YouTube ID from a URL
# It looks for various youtube URL formats and captures the 11-character ID.
YOUTUBE_ID_REGEX = re.compile(r"(?:v=|\/|youtu\.be\/|embed\/|shorts\/)([a-zA-Z0-9_-]{11})")


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
