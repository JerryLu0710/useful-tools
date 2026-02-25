import re

# Regex to extract YouTube ID from a URL
# It looks for various youtube URL formats and captures the 11-character ID.
YOUTUBE_ID_REGEX = re.compile(r"(?:v=|\/|youtu\.be\/|embed\/|shorts\/)([a-zA-Z0-9_-]{11})")


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
