import sys

from ytmusic_dl.commands.verify import extract_id_from_file
from ytmusic_dl.common.logger import logger


def metadata_command(args):
    """Main logic for the metadata command (extract-id)."""
    video_id = extract_id_from_file(args.file_path, scan_all=False)

    if video_id:
        logger.info("Success: Found YouTube ID.")
        logger.info(f"File: {args.file_path.name}")
        logger.info(f"ID: {video_id}")
    else:
        logger.error(f"Failure: No YouTube ID found in the metadata of '{args.file_path.name}'.")
        sys.exit(1)
