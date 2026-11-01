import json
import os
from pathlib import Path

from ytmusic_dl.common.logger import logger
from ytmusic_dl.common.utils import latest_from_entries, load_history_entries


def _count_written_lines(history_path: Path) -> int:
    """Count the non-blank lines the history file actually holds."""
    with open(history_path, encoding="utf-8") as f:
        return sum(1 for line in f if line.strip())


def prune_history_command(args):
    """Rewrite the history file so each video ID is represented by its current line.

    Downloading appends one line per track, and `normalize-names` appends a
    superseding line per rename, so a history file accumulates lines whose
    `file_path` no longer exists. Reading it naively counts a renamed track
    twice. Pruning collapses each ID to its last line, in first-appearance order.
    """
    history_path = args.history

    if not history_path.exists():
        logger.error(f"History file not found at '{history_path}'.")
        return 1

    try:
        written = _count_written_lines(history_path)
    except OSError as e:
        logger.error(f"Could not read '{history_path}': {e}")
        return 1

    entries = load_history_entries(history_path)
    if written != len(entries):
        logger.error(
            f"'{history_path}' holds {written} lines but only {len(entries)} usable entries. "
            "Refusing to rewrite a damaged history file; repair the unreadable lines first."
        )
        return 1

    current = latest_from_entries(entries)
    dropped = written - len(current)
    if not dropped:
        logger.info(f"'{history_path}': {written} lines, one per video ID. Nothing to prune.")
        return 0

    # The kept line is the last one for an ID, so every earlier line is a path a
    # rename moved away from. Showing both sides is what makes the count checkable.
    last_index = {entry["id"]: index for index, entry in enumerate(entries)}
    for index, entry in enumerate(entries):
        if last_index[entry["id"]] != index:
            kept = current[entry["id"]]
            logger.info(
                f"Drops '{Path(entry.get('file_path', '<no path>')).name}' for {entry['id']} "
                f"-> kept '{Path(kept.get('file_path', '<no path>')).name}'"
            )
    logger.info(f"'{history_path}': {written} lines, {len(current)} current, {dropped} superseded.")

    if args.dry_run:
        logger.info("Dry run: the history file was not changed.")
        return 0

    # A temp file plus os.replace means an interrupted prune leaves the original
    # intact instead of a half-written history.
    temp_path = history_path.with_name(f"{history_path.name}.pruning")
    try:
        with open(temp_path, "w", encoding="utf-8") as f:
            for entry in current.values():
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        os.replace(temp_path, history_path)
    except OSError as e:
        logger.error(f"Could not rewrite '{history_path}': {e}")
        Path(temp_path).unlink(missing_ok=True)
        return 1

    logger.info(f"Rewrote '{history_path}' with {len(current)} lines.")
    return 0
