import json
import sys
from argparse import Namespace
from pathlib import Path

from mutagen import File as MutagenFile

from ytmusic_dl.common.logger import logger
from ytmusic_dl.common.utils import YOUTUBE_ID_REGEX

# --- List of keys to check for the ID, in order of priority ---
ID_METADATA_KEYS = [
    ("TXXX:youtube_id", False),  # MP3 custom tag (no regex needed)
    ("----:com.apple.iTunes:youtube_id", False),  # M4A custom tag (no regex needed)
    ("TXXX:purl", True),  # MP3 "PURL" tag
    ("TXXX:comment", True),  # MP3 comment tag
    ("©cmt", True),  # M4A comment tag
]


def load_history_ids(history_path: Path) -> set[str]:
    """Loads all video IDs from the JSONL history file into a set."""
    downloaded_ids = set()
    if not history_path.exists():
        logger.warning(f"History file not found at '{history_path}'")
        return downloaded_ids

    with open(history_path, encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            if line.strip():
                try:
                    entry = json.loads(line)
                    if "id" in entry:
                        downloaded_ids.add(entry["id"])
                except json.JSONDecodeError:
                    logger.warning(f"Could not parse line {i} in history file.")
    logger.info(f"Loaded {len(downloaded_ids)} unique IDs from history file.")
    return downloaded_ids


def extract_id_from_file(file_path: Path, scan_all: bool) -> str | None:
    """
    Extracts a YouTube video ID from an audio file's metadata.

    It first checks a prioritized list of common tags. If no ID is found,
    and 'scan_all' is True, it performs a deep scan of all metadata tags.
    """
    try:
        audio_file = MutagenFile(file_path)
        if audio_file is None:
            return None

        # 1. Prioritized Scan
        for key, use_regex in ID_METADATA_KEYS:
            if key in audio_file:
                value = audio_file[key]
                text_content = str(value[0] if isinstance(value, list) else value)

                if not use_regex:
                    # The tag directly contains the ID
                    return text_content.strip()

                # The tag contains a URL that needs to be parsed
                match = YOUTUBE_ID_REGEX.search(text_content)
                if match:
                    return match.group(1)

        # 2. Full Scan (if enabled and necessary)
        if scan_all:
            for key in audio_file:
                # Skip keys we've already checked
                if key in [k[0] for k in ID_METADATA_KEYS]:
                    continue

                values = audio_file[key]
                if not isinstance(values, list):
                    values = [values]
                for value in values:
                    text_content = str(value)
                    match = YOUTUBE_ID_REGEX.search(text_content)
                    if match:
                        return match.group(1)

    except Exception:
        # Ignore files that can't be read by mutagen
        return None
    return None


def download_missing_songs(missing_ids: list[str]):
    """
    Downloads missing songs by calling the download command directly.

    Args:
        missing_ids: List of YouTube video IDs to download.
    """
    if not missing_ids:
        logger.info("No missing songs to download.")
        return

    logger.info("\n" + "=" * 50)
    logger.info(f"Attempting to download {len(missing_ids)} missing song(s)...")
    logger.info("=" * 50)

    from ytmusic_dl.commands.download import download_command
    from ytmusic_dl.config import YTMusicDLConfig

    # Build a Namespace that mirrors the CLI arguments for download_command
    urls = [f"https://music.youtube.com/watch?v={vid}" for vid in missing_ids]
    fake_args = Namespace(
        urls=urls,
        output=YTMusicDLConfig.DEFAULT_DOWNLOAD_DIR,
        history=YTMusicDLConfig.DEFAULT_HISTORY_FILE,
        audio_format="best",
        quality="141/bestaudio[ext=m4a]/bestaudio",
        no_thumbnail=False,
        no_metadata=False,
        force=False,
        dry_run=False,
        browser=None,
        cookies=None,
    )

    try:
        download_command(fake_args)
        logger.info("Download process completed successfully.")
    except Exception as e:
        logger.error(f"An error occurred during the download process: {e}")


def verify_command(args):
    """Main logic for the verify command."""
    logger.info("Starting verification process...")
    history_ids = load_history_ids(args.history)

    if not args.backup_dir.exists():
        logger.error(f"Backup directory not found at '{args.backup_dir}'")
        sys.exit(1)

    logger.info(f"Scanning for audio files in '{args.backup_dir}'...")
    audio_files = (
        list(args.backup_dir.glob("**/*.mp3"))
        + list(args.backup_dir.glob("**/*.m4a"))
        + list(args.backup_dir.glob("**/*.opus"))
        + list(args.backup_dir.glob("**/*.webm"))
    )

    if not audio_files:
        logger.warning("No audio files found in the backup directory.")
        sys.exit(0)

    logger.info(f"Found {len(audio_files)} audio files to check.")

    missing_files = {}
    files_without_id = []

    for i, file in enumerate(audio_files, 1):
        print(f"\rProcessing file {i}/{len(audio_files)}: {file.name.ljust(80)}", end="")
        embedded_id = extract_id_from_file(file, args.scan_all)

        if embedded_id:
            if embedded_id not in history_ids:
                missing_files[embedded_id] = file.name
        else:
            files_without_id.append(file.name)

    # Final summary
    print("\r" + " " * 120 + "\r", end="")
    logger.info("=" * 50)
    logger.info("Verification Complete.")
    logger.info("=" * 50)

    if missing_files:
        logger.info(f"Found {len(missing_files)} songs in backup that are NOT in the history file:")
        for video_id, filename in missing_files.items():
            logger.info(f"  - ID: {video_id:<12} File: {filename}")
    else:
        logger.info("All audio files with a valid YouTube ID are present in the history file.")

    if files_without_id:
        logger.warning(
            f"Could not find a YouTube ID in the metadata of {len(files_without_id)} files:"
        )
        for filename in files_without_id:
            logger.info(f"  - {filename}")

    # Optionally download the missing songs
    if args.download_missing and missing_files:
        download_missing_songs(list(missing_files.keys()))
