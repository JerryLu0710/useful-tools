import os
from pathlib import Path

from config import Config as BaseConfig


class YTMusicDLConfig(BaseConfig):
    """Configuration for ytmusic_dl."""

    # Default paths (cross-platform, overridable via environment variables)
    DEFAULT_DOWNLOAD_DIR = Path(os.getenv("YTMUSIC_DL_DOWNLOAD_DIR", str(Path.home() / "Music")))
    DEFAULT_HISTORY_FILE = Path(
        os.getenv(
            "YTMUSIC_DL_HISTORY_FILE",
            str(Path.home() / ".ytmusic_dl" / "history.jsonl"),
        )
    )
