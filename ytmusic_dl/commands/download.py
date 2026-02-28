import json
import logging
import shutil
import sys
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import yt_dlp

from ytmusic_dl.common.logger import logger
from ytmusic_dl.common.utils import extract_artist

HONG_KONG_TZ = ZoneInfo("Asia/Hong_Kong")


def _build_js_opts() -> dict:
    """Build yt-dlp options for Node.js runtime discovery.

    When yt-dlp is used as a Python library, it does not read its CLI
    config.txt, so js_runtimes and remote_components must be injected
    directly into the options dict.

    Returns:
        Dictionary of JS-related yt-dlp options, or empty dict if
        Node.js is not found.
    """
    node_path = shutil.which("node")
    if node_path:
        logger.debug(f"Using Node.js at: {node_path}")
        return {
            "js_runtimes": {"node": {"path": node_path}},
            "remote_components": ["ejs:github"],
        }
    logger.warning("Node.js not found in PATH — some formats may be missing")
    return {}


def load_history(history_path: Path) -> set[str]:
    """
    Load previously downloaded video IDs from JSONL history file.

    Args:
        history_path: Path to JSONL history file

    Returns:
        Set of video IDs that have been downloaded
    """
    downloaded_ids = set()

    if not history_path.exists():
        return downloaded_ids

    try:
        with open(history_path, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    entry = json.loads(line)
                    downloaded_ids.add(entry["id"])
    except Exception as e:
        logger.warning(f"Error loading history file: {e}")

    return downloaded_ids


def append_to_history(history_path: Path, entry: dict):
    """
    Append a new download entry to JSONL history file.

    Args:
        history_path: Path to JSONL history file
        entry: Dictionary containing download metadata
    """
    # Ensure directory exists
    history_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(history_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception as e:
        logger.error(f"Failed to write to history file: {e}")


def get_video_info(url: str) -> tuple[list[dict], bool]:
    """
    Extract video information without downloading.

    Args:
        url: YouTube URL

    Returns:
        Tuple of (list of video info dictionaries, is_playlist flag).
        Returns ([], False) on failure.
    """
    js_opts = _build_js_opts()
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": "in_playlist",
        **js_opts,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            # Handle playlist/channel
            if "entries" in info:
                return list(info["entries"]), True
            # Single video
            else:
                return [info], False
    except Exception as e:
        logger.error(f"Failed to extract video info for '{url}': {e}")
        return [], False


def download_command(args):
    """Main logic for the download command."""
    # Convert paths
    output_path = args.output
    history_path = args.history

    # Ensure output directory exists
    output_path.mkdir(parents=True, exist_ok=True)

    # Load history
    logger.info(f"Loading history from {history_path}")
    downloaded_ids = load_history(history_path)
    if downloaded_ids:
        logger.info(f"Found {len(downloaded_ids)} previously downloaded tracks")

    # Get video information from all URLs
    all_videos = []
    is_playlist = False
    for url in args.urls:
        logger.info(f"Extracting video information from: {url}")
        videos_from_url, url_is_playlist = get_video_info(url)
        all_videos.extend(videos_from_url)
        if url_is_playlist:
            is_playlist = True

    if not all_videos:
        logger.warning("No videos found from the provided URLs. Exiting.")
        return

    videos = all_videos
    if is_playlist:
        logger.info(f"Found a total of {len(videos)} videos from all provided URLs.")

    # Download options
    download_options = {
        "audio_format": args.audio_format,
        "quality": args.quality,
        "embed_thumbnail": not args.no_thumbnail,
        "add_metadata": not args.no_metadata,
    }

    # Build output template
    # output_template = str(output_path / "%(artist,channel,uploader)s - %(title)s.%(ext)s")
    output_template = str(output_path / "%(title)s.%(ext)s")

    # Build postprocessors list
    postprocessors = []

    # Add conversion postprocessor only if a specific format is requested
    if download_options["audio_format"] != "best":
        postprocessors.append(
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": download_options["audio_format"],
                "preferredquality": "0",  # Use highest VBR quality for conversions
                "nopostoverwrites": False,
            }
        )

    if download_options["add_metadata"]:
        postprocessors.append(
            {
                "key": "FFmpegMetadata",
                "add_metadata": True,
                "add_chapters": True,
                "add_infojson": "if_exists",
            }
        )
    if download_options["embed_thumbnail"]:
        postprocessors.extend(
            [
                {
                    "key": "FFmpegThumbnailsConvertor",
                    "format": "jpg",
                    "when": "before_dl",
                },
                {
                    "key": "EmbedThumbnail",
                    "already_have_thumbnail": False,
                },
            ]
        )

    # Find Node.js for JS-based extractors
    js_opts = _build_js_opts()

    # yt-dlp options for downloading
    ydl_opts = {
        "format": download_options["quality"],
        "outtmpl": {"default": output_template},
        "postprocessors": postprocessors,
        "writethumbnail": download_options["embed_thumbnail"],
        "convert_thumbnails": "jpg",
        "quiet": logger.level != logging.DEBUG,
        "no_warnings": True,
        "extract_flat": "discard_in_playlist",
        "fragment_retries": 10,
        "retries": 10,
        "ignoreerrors": "only_download",
        "extractor_args": {"youtube": {"lang": ["ja"]}},
        **js_opts,
    }

    # yt-dlp options for fetching metadata
    meta_ydl_opts = {"quiet": True, "no_warnings": True, **js_opts}

    if args.browser:
        ydl_opts["cookiesfrombrowser"] = (args.browser,)
        meta_ydl_opts["cookiesfrombrowser"] = (args.browser,)
    elif args.cookies:
        ydl_opts["cookiefile"] = str(args.cookies)
        meta_ydl_opts["cookiefile"] = str(args.cookies)

    # Statistics
    downloaded_count = 0
    skipped_count = 0
    failed_count = 0
    failed_videos = []

    # Process each video
    with yt_dlp.YoutubeDL(ydl_opts) as ydl, yt_dlp.YoutubeDL(meta_ydl_opts) as meta_ydl:
        for idx, video in enumerate(videos, 1):
            if video is None:
                continue

            video_id = video.get("id")
            if not video_id:
                logger.warning("Skipping video without ID")
                continue

            # Get full info for single video or need to extract from playlist entry
            if is_playlist and not video.get("title"):
                try:
                    video = meta_ydl.extract_info(
                        f"https://music.youtube.com/watch?v={video_id}",
                        download=False,
                    )
                except Exception as e:
                    logger.error(f"Failed to get info for video {video_id}: {e}")
                    failed_count += 1
                    failed_videos.append(video_id)
                    continue

            artist, artist_source = extract_artist(video)
            title = video.get("title", "Unknown")

            # Check if already downloaded
            if not args.force and video_id in downloaded_ids:
                logger.info(
                    f"[{idx}/{len(videos)}] Already downloaded, skipping: {artist} - {title}"
                )
                skipped_count += 1
                continue

            # Dry run mode
            if args.dry_run:
                logger.info(f"[{idx}/{len(videos)}] Would download: {artist} - {title}")
                continue

            # Normal download
            logger.info(f"[{idx}/{len(videos)}] Downloading: {artist} - {title}")

            try:
                info = ydl.extract_info(video_id, download=True)
                # logger.info(f"Info: {json.dumps(info, indent=2)}")

                # With ignoreerrors="only_download", yt-dlp returns None
                # or omits requested_downloads when the download fails
                if info is None:
                    raise RuntimeError("Download failed (no info returned)")

                requested_downloads = info.get("requested_downloads")
                if not requested_downloads:
                    raise RuntimeError("Download failed (no output file produced)")

                file_path = requested_downloads[0].get("filepath")
                if not file_path or not Path(file_path).exists():
                    raise RuntimeError(f"Download failed (output file '{file_path}' not found)")

                # Create history entry
                entry = {
                    "id": video_id,
                    "artist": artist,
                    "artist_source": artist_source,
                    "title": title,
                    "source": video.get("extractor", "youtube"),
                    "downloaded_at": datetime.now(HONG_KONG_TZ).isoformat(),
                    "file_path": file_path,
                    "tags": info.get("tags", []),
                    "duration": str(timedelta(seconds=info.get("duration"))),
                    "album": info.get("album"),
                    "track": info.get("track"),
                    "release_date": info.get("release_date"),
                    "upload_date": info.get("upload_date"),
                }

                # Append to history
                append_to_history(history_path, entry)
                downloaded_ids.add(video_id)

                logger.info(f"✓ Downloaded: {artist} - {title}")
                downloaded_count += 1

            except Exception as e:
                logger.error(f"✗ Failed to download {video_id}: {e}")
                failed_count += 1
                failed_videos.append(f"{artist} - {title} ({video_id})")

                # Exit immediately for single video
                if not is_playlist:
                    sys.exit(1)

        # Print summary for playlists or dry-run
        if is_playlist or args.dry_run:
            logger.info("=" * 50)
            if args.dry_run:
                logger.info(
                    f"Dry-run complete: {len(videos) - skipped_count - failed_count} videos would be processed, {skipped_count} skipped, {failed_count} failed"
                )
            else:
                logger.info(
                    f"Summary: {downloaded_count} downloaded, {skipped_count} skipped, {failed_count} failed"
                )
                if failed_videos:
                    logger.info("Failed videos:")
                    for video in failed_videos:
                        logger.info(f"  - {video}")
