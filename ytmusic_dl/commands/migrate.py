import json
import sys
from argparse import Namespace

from ytmusic_dl.common.logger import logger


def _read_ids_from_txt(path) -> list[str]:
    """Read video IDs from a plain-text file.

    Supported line formats:
    - ``youtube <id>`` (yt-dlp format)
    - ``<id>`` (bare video ID, single token per line)

    Blank lines and unrecognised formats are skipped.

    Args:
        path: Path to the text file.

    Returns:
        List of video ID strings.
    """
    video_ids: list[str] = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            if len(parts) == 1:
                # Bare video ID
                video_ids.append(parts[0])
            elif len(parts) == 2 and parts[0] == "youtube":
                # "youtube <id>" format
                video_ids.append(parts[1])
            else:
                logger.warning(f"Skipping invalid line: {line}")
    return video_ids


def _read_ids_from_jsonl(path) -> list[str]:
    """Read video IDs from a JSONL history file.

    Each line is expected to be a JSON object with an ``"id"`` key.

    Args:
        path: Path to the JSONL file.

    Returns:
        List of video ID strings.
    """
    video_ids: list[str] = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                vid = entry.get("id")
                if vid:
                    video_ids.append(vid)
                else:
                    logger.warning(f"Skipping JSONL entry without 'id': {line}")
            except json.JSONDecodeError:
                logger.warning(f"Skipping malformed JSONL line: {line}")
    return video_ids


def migrate_command(args):
    """Read video IDs from a text or JSONL file and redownload them.

    File format is auto-detected by extension:
    - ``.jsonl`` → each line is a JSON object with an ``"id"`` key.
    - anything else → plain text, one video ID per line (or ``youtube <id>``).
    """
    file_path = args.file_path

    if not file_path.exists():
        logger.error(f"Error: '{file_path}' not found.")
        sys.exit(1)

    # Auto-detect format by extension
    if file_path.suffix == ".jsonl":
        logger.info(f"Reading JSONL history file: {file_path}")
        video_ids = _read_ids_from_jsonl(file_path)
    else:
        logger.info(f"Reading plain-text ID file: {file_path}")
        video_ids = _read_ids_from_txt(file_path)

    if not video_ids:
        logger.warning("No valid video IDs found to download.")
        sys.exit(0)

    logger.info(f"Found {len(video_ids)} songs to redownload. Starting batch process...")

    from ytmusic_dl.commands.download import download_command
    from ytmusic_dl.config import YTMusicDLConfig

    # Build full YouTube Music URLs from video IDs
    urls = [f"https://music.youtube.com/watch?v={vid}" for vid in video_ids]

    # Use CLI args for output/history/quality when provided, otherwise defaults
    fake_args = Namespace(
        urls=urls,
        output=getattr(args, "output", YTMusicDLConfig.DEFAULT_DOWNLOAD_DIR),
        history=getattr(args, "history", YTMusicDLConfig.DEFAULT_HISTORY_FILE),
        audio_format=getattr(args, "audio_format", "best"),
        quality=getattr(args, "quality", "141/bestaudio[ext=m4a]/bestaudio"),
        no_thumbnail=getattr(args, "no_thumbnail", False),
        no_metadata=getattr(args, "no_metadata", False),
        force=getattr(args, "force", False),
        dry_run=getattr(args, "dry_run", False),
        browser=getattr(args, "browser", None),
        cookies=getattr(args, "cookies", None),
    )

    try:
        download_command(fake_args)
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")

    logger.info("All songs have been processed.")
