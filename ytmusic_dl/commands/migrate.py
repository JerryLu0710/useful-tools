from argparse import Namespace

from ytmusic_dl.common.logger import logger
from ytmusic_dl.common.utils import load_history_entries


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
    """Read video IDs from a JSONL history file, keeping one entry per ID.

    A rename appends a second line for the same ID, so each ID must become one
    download URL.

    Args:
        path: Path to the JSONL file.

    Returns:
        List of video ID strings, in file order.
    """
    return list(dict.fromkeys(entry["id"] for entry in load_history_entries(path)))


def migrate_command(args):
    """Read video IDs from a text or JSONL file and redownload them.

    File format is auto-detected by extension:
    - ``.jsonl`` → each line is a JSON object with an ``"id"`` key.
    - anything else → plain text, one video ID per line (or ``youtube <id>``).
    """
    file_path = args.file_path

    if not file_path.exists():
        logger.error(f"Error: '{file_path}' not found.")
        return 1

    # Auto-detect format by extension
    if file_path.suffix == ".jsonl":
        logger.info(f"Reading JSONL history file: {file_path}")
        video_ids = _read_ids_from_jsonl(file_path)
    else:
        logger.info(f"Reading plain-text ID file: {file_path}")
        video_ids = _read_ids_from_txt(file_path)

    if not video_ids:
        logger.warning("No valid video IDs found to download.")
        return 0

    logger.info(f"Found {len(video_ids)} songs to redownload. Starting batch process...")

    from ytmusic_dl.commands.download import download_command

    # Build full YouTube Music URLs from video IDs
    urls = [f"https://music.youtube.com/watch?v={vid}" for vid in video_ids]

    # The migrate parser defines every one of these, so read them directly: an
    # unreachable getattr default is how a stale quality selector survived here.
    fake_args = Namespace(
        urls=urls,
        output=args.output,
        history=args.history,
        audio_format=args.audio_format,
        quality=args.quality,
        no_thumbnail=args.no_thumbnail,
        no_metadata=args.no_metadata,
        force=args.force,
        dry_run=args.dry_run,
        browser=args.browser,
        cookies=args.cookies,
        # A batch redownload never waits for input; it renames without asking.
        prompt_on_duplicate=False,
    )

    try:
        status = download_command(fake_args) or 0
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        status = 1

    logger.info(f"All songs have been processed. Exit code {status}.")
    return status
