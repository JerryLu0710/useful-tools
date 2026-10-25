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

    # Quality-based selectors never hard-fail on a missing format ID, unlike the
    # hard-coded Premium format 141, which is absent without a Premium account.
    DEFAULT_QUALITY = "bestaudio[abr>=200][ext=m4a]/bestaudio[ext=m4a]/bestaudio"
