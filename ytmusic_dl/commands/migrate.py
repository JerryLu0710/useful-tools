import sys
from argparse import Namespace

from ytmusic_dl.common.logger import logger


def migrate_command(args):
    """
    Reads video IDs from a text file and redownloads them efficiently
    by calling the download command directly.
    """
    downloaded_txt_path = args.file_path

    if not downloaded_txt_path.exists():
        logger.error(f"Error: '{downloaded_txt_path}' not found.")
        sys.exit(1)

    with open(downloaded_txt_path, encoding="utf-8") as f:
        lines = f.readlines()

    video_ids = []
    for line in lines:
        line = line.strip()
        if not line:
            continue

        parts = line.split()
        # Expecting format: "youtube <id>" or just "<id>" if we want to be flexible,
        # but original script enforced "youtube <id>".
        if len(parts) != 2 or parts[0] != "youtube":
            logger.warning(f"Skipping invalid line: {line}")
            continue

        video_ids.append(parts[1])

    if not video_ids:
        logger.warning("No valid video IDs found to download.")
        sys.exit(0)

    logger.info(f"Found {len(video_ids)} songs to redownload. Starting batch process...")

    from ytmusic_dl.commands.download import download_command
    from ytmusic_dl.config import YTMusicDLConfig

    # Build full YouTube Music URLs from video IDs
    urls = [f"https://music.youtube.com/watch?v={vid}" for vid in video_ids]

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
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")

    logger.info("All songs have been processed.")
