import sys
from collections import defaultdict

from ytmusic_dl.commands.download import (
    AUDIO_FILE_EXTENSIONS,
    find_same_title_files,
    load_history_entries,
    rename_title_only_files,
)
from ytmusic_dl.common.logger import logger


def rename_command(args):
    """Rename existing title-only files so tracks that share a title share one scheme.

    Titles and artists are read from the history file, so this needs no network
    access and never guesses a title from a filename: 'Song - Live.m4a' could
    otherwise be an artist-suffixed 'Song' or a bare title of its own.
    """
    output_path = args.output
    history_path = args.history

    if not history_path.exists():
        logger.error(f"History file not found at '{history_path}'.")
        sys.exit(1)
    if not output_path.exists():
        logger.error(f"Output directory not found at '{output_path}'.")
        sys.exit(1)

    entries = load_history_entries(history_path)
    # Later lines supersede earlier ones for the same video ID, which is how a
    # previous rename recorded its new path.
    latest_by_id = {entry["id"]: entry for entry in entries}
    entries_by_path = {
        entry["file_path"]: entry for entry in latest_by_id.values() if entry.get("file_path")
    }
    recorded_paths = {entry["file_path"] for entry in entries if entry.get("file_path")}

    ids_by_title = defaultdict(set)
    for entry in latest_by_id.values():
        if entry.get("title"):
            ids_by_title[entry["title"]].add(entry["id"])

    # A title needs disambiguating when history holds more than one track with it,
    # or when the folder already mixes a title-only file with an artist-suffixed one.
    shared = {title for title, ids in ids_by_title.items() if len(ids) > 1}
    shared.update(
        title
        for title in ids_by_title
        if title not in shared and len(find_same_title_files(output_path, title)) > 1
    )

    unrecorded = [
        path
        for path in output_path.glob("*")
        if path.is_file()
        and path.suffix.lower() in AUDIO_FILE_EXTENSIONS
        and str(path) not in recorded_paths
    ]
    if unrecorded:
        logger.warning(
            f"{len(unrecorded)} audio file(s) are not in the history file and are left alone:"
        )
        for path in unrecorded:
            logger.info(f"  - {path.name}")

    if not shared:
        logger.info("No shared titles found; every filename is already unambiguous.")
        return

    logger.info(f"Found {len(shared)} shared title(s) to unify in '{output_path}'.")
    renamed = sum(
        rename_title_only_files(
            output_path,
            title,
            entries_by_path,
            history_path,
            dry_run=args.dry_run,
            tag_fallback=False,
        )
        for title in sorted(shared)
    )

    verb = "Would rename" if args.dry_run else "Renamed"
    logger.info(f"{verb} {renamed} title-only file(s).")
