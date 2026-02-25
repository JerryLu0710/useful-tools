import argparse
from pathlib import Path

from ytmusic_dl.commands.download import download_command
from ytmusic_dl.commands.metadata import metadata_command
from ytmusic_dl.commands.migrate import migrate_command
from ytmusic_dl.commands.verify import verify_command
from ytmusic_dl.common.logger import logger
from ytmusic_dl.config import YTMusicDLConfig


def setup_logger(log_level: str):
    """Setup console logger with specified level."""
    logger.setLevel(log_level.upper())


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="YouTube Music Downloader and Library Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Global arguments
    parser.add_argument(
        "-l",
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Log level (default: INFO)",
    )

    subparsers = parser.add_subparsers(dest="command", required=True, help="Command to run")

    # --- Download Command ---
    download_parser = subparsers.add_parser(
        "download", help="Download audio from YouTube videos/playlists"
    )
    download_parser.add_argument(
        "urls", nargs="+", help="One or more YouTube URLs (video/playlist/channel)"
    )
    download_parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=YTMusicDLConfig.DEFAULT_DOWNLOAD_DIR,
        help=f"Output directory (default: {YTMusicDLConfig.DEFAULT_DOWNLOAD_DIR})",
    )
    download_parser.add_argument(
        "-f",
        "--format",
        default="best",
        dest="audio_format",
        help="Audio format to convert to. 'best' (default) keeps original. Specify 'mp3' to convert.",
    )
    download_parser.add_argument(
        "-q",
        "--quality",
        default="141/bestaudio[ext=m4a]/bestaudio",
        help="Quality selection (default: 141/bestaudio[ext=m4a]/bestaudio)",
    )
    download_parser.add_argument(
        "-hi",
        "--history",
        type=Path,
        default=YTMusicDLConfig.DEFAULT_HISTORY_FILE,
        help=f"Path to JSONL history file (default: {YTMusicDLConfig.DEFAULT_HISTORY_FILE})",
    )
    download_parser.add_argument(
        "-dr",
        "--dry-run",
        action="store_true",
        help="Show what would be downloaded without downloading",
    )
    download_parser.add_argument(
        "--no-thumbnail", action="store_true", help="Skip embedding thumbnail"
    )
    download_parser.add_argument("--no-metadata", action="store_true", help="Skip adding metadata")
    cookie_group = download_parser.add_mutually_exclusive_group()
    cookie_group.add_argument(
        "--browser",
        default=None,
        choices=["chrome", "firefox", "brave", "edge"],
        help="Browser to extract cookies from for authentication (optional, enables Premium formats)",
    )
    cookie_group.add_argument(
        "--cookies",
        type=Path,
        default=None,
        help="Path to a Netscape-format cookies.txt file for authentication (useful in WSL)",
    )
    download_parser.add_argument("--force", action="store_true", help="Download even if in history")
    download_parser.set_defaults(func=download_command)

    # --- Verify Command ---
    verify_parser = subparsers.add_parser("verify", help="Verify backup files against history")
    verify_parser.add_argument(
        "-b",
        "--backup-dir",
        metavar="BACKUP_DIR",
        type=Path,
        default=YTMusicDLConfig.DEFAULT_DOWNLOAD_DIR,
        help=f"Directory containing the backup audio files (default: {YTMusicDLConfig.DEFAULT_DOWNLOAD_DIR})",
    )
    verify_parser.add_argument(
        "--history",
        metavar="HISTORY_FILE",
        type=Path,
        default=YTMusicDLConfig.DEFAULT_HISTORY_FILE,
        help=f"Path to the JSONL history file (default: {YTMusicDLConfig.DEFAULT_HISTORY_FILE})",
    )
    verify_parser.add_argument(
        "-s",
        "--scan-all",
        action="store_true",
        help="Perform a deep scan of all metadata tags.",
    )
    verify_parser.add_argument(
        "-d",
        "--download-missing",
        action="store_true",
        help="Automatically download any songs found in backup but not in the history file.",
    )
    verify_parser.set_defaults(func=verify_command)

    # --- Metadata Command (Extract ID) ---
    metadata_parser = subparsers.add_parser(
        "extract-id", help="Extract YouTube ID from an audio file"
    )
    metadata_parser.add_argument("file_path", type=Path, help="Path to the audio file.")
    metadata_parser.set_defaults(func=metadata_command)

    # --- Migrate Command (Redownload from TXT) ---
    migrate_parser = subparsers.add_parser("migrate", help="Redownload songs from a text file list")
    migrate_parser.add_argument(
        "file_path", type=Path, help="Path to the text file containing 'youtube <id>' lines."
    )
    migrate_parser.set_defaults(func=migrate_command)

    args = parser.parse_args()

    # Setup logger
    setup_logger(args.log_level)

    # Execute command
    args.func(args)


if __name__ == "__main__":
    main()
