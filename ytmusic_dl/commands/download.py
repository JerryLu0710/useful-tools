import contextlib
import json
import logging
import sys
from datetime import datetime, timedelta
from glob import escape
from pathlib import Path
from zoneinfo import ZoneInfo

import yt_dlp
from mutagen import File as MutagenFile
from yt_dlp.utils import sanitize_filename

from ytmusic_dl.common.logger import logger
from ytmusic_dl.common.utils import extract_artist, tag_values

HONG_KONG_TZ = ZoneInfo("Asia/Hong_Kong")

# yt-dlp's own fallback chain for the artist field, so yt-dlp sanitises the value
# instead of us interpolating a raw artist name into the template.
ARTIST_TEMPLATE = "%(artist,channel,uploader)s"

# Artist tag keys to read from an existing file, covering mp3, m4a and opus/webm.
ARTIST_TAG_KEYS = ("TPE1", "\xa9ART", "----:com.apple.iTunes:ARTIST", "artist")

AUDIO_FILE_EXTENSIONS = frozenset(
    {
        ".aac",
        ".flac",
        ".m4a",
        ".m4b",
        ".mka",
        ".mp3",
        ".mp4",
        ".ogg",
        ".opus",
        ".wav",
        ".webm",
    }
)


def _build_js_opts() -> dict:
    """Build yt-dlp options for JS runtime discovery and remote components.

    When yt-dlp is used as a Python library, it does not read its CLI
    config.txt, so js_runtimes and remote_components must be injected
    directly into the options dict.

    Returns:
        Dictionary of JS-related yt-dlp options.
    """
    return {
        "js_runtimes": {"node": {}, "deno": {}, "bun": {}},
        "remote_components": ["ejs:github"],
    }


def load_history_entries(history_path: Path) -> list[dict]:
    """
    Load history entries from JSONL history file.

    Entries are returned in file order; later lines supersede earlier ones for
    the same video ID, which is how renames are recorded without rewriting the
    file.

    Args:
        history_path: Path to JSONL history file

    Returns:
        List of history entry dictionaries that carry a video ID
    """
    entries = []

    if not history_path.exists():
        return entries

    try:
        with open(history_path, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    entry = json.loads(line)
                    if entry.get("id"):
                        entries.append(entry)
    except Exception as e:
        logger.warning(f"Error loading history file: {e}")

    return entries


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


def get_video_info(url: str, cookie_opts: dict | None = None) -> tuple[list[dict], bool]:
    """
    Extract video information without downloading.

    Args:
        url: YouTube URL
        cookie_opts: Optional dictionary of cookie-related yt-dlp options
            (e.g. cookiefile or cookiesfrombrowser).

    Returns:
        Tuple of (list of video info dictionaries, is_playlist flag).
        Returns ([], False) on failure.
    """
    if cookie_opts is None:
        cookie_opts = {}

    js_opts = _build_js_opts()
    ydl_opts = {
        "quiet": True,
        "no_warnings": logger.level != logging.DEBUG,
        "extract_flat": "in_playlist",
        **js_opts,
        **cookie_opts,
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


def render_filename_stem(title: str, artist: str | None = None) -> str:
    """Reproduce the filename stem yt-dlp writes for a title (and optional artist).

    yt-dlp sanitises each field it substitutes into an output template, so a
    title containing '/' or ':' is written differently from the raw title. Disk
    lookups must compare against the written form or they miss the file.
    """
    return " - ".join(sanitize_filename(part) for part in (title, artist) if part)


def _audio_files_matching(output_path: Path, pattern: str) -> list[Path]:
    """Return audio files matched by a glob ``pattern``."""
    return [
        path
        for path in output_path.glob(pattern)
        if path.is_file() and path.suffix.lower() in AUDIO_FILE_EXTENSIONS
    ]


def find_existing_audio_files(output_path: Path, filename_stem: str) -> list[Path]:
    """Return audio files whose filename stem exactly matches ``filename_stem``."""
    return _audio_files_matching(output_path, f"{escape(filename_stem)}.*")


def find_same_title_files(output_path: Path, title: str) -> list[Path]:
    """Return audio files named ``Title`` or ``Title - <artist>`` for ``title``.

    shortcut: a title that itself contains ' - ' can match another title's
    artist-suffixed file; the effect is one extra artist suffix, upgrade to
    parsing the artist back out of the name if that ever matters.
    """
    stem = render_filename_stem(title)
    return find_existing_audio_files(output_path, stem) + _audio_files_matching(
        output_path, f"{escape(stem)} - *"
    )


def read_artist_tag(path: Path) -> str | None:
    """Read the artist from an audio file's own tags, or None if unreadable."""
    try:
        audio_file = MutagenFile(path)
    except Exception:
        return None
    if audio_file is None:
        return None

    for key in ARTIST_TAG_KEYS:
        values = tag_values(audio_file, key)
        if values:
            return values[0]
    return None


def rename_title_only_files(
    output_path: Path,
    title: str,
    entries_by_path: dict[str, dict],
    history_path: Path,
    *,
    dry_run: bool = False,
    tag_fallback: bool = True,
) -> int:
    """Rename ``Title.ext`` files to ``Title - Artist.ext`` so a shared title uses
    one naming scheme instead of a mix that depends on download order.

    The artist comes from the history entry for that exact file, optionally
    falling back to the file's own tags. The rename is recorded by appending a
    superseding history line, keeping the history file append-only.

    Returns:
        The number of title-only files renamed, or would be renamed for dry_run
    """
    stem = render_filename_stem(title)
    renamed = 0
    for audio_file in find_existing_audio_files(output_path, stem):
        entry = entries_by_path.get(str(audio_file))
        artist = (entry or {}).get("artist")
        if not artist and tag_fallback:
            artist = read_artist_tag(audio_file)
        if not artist:
            logger.warning(
                f"No history entry with an artist for '{audio_file.name}'. Leaving it title-only."
            )
            continue

        new_stem = render_filename_stem(title, artist)
        new_audio = audio_file.with_name(new_stem + audio_file.name[len(stem) :])
        if new_audio.exists():
            logger.warning(
                f"'{new_audio.name}' already exists. Leaving '{audio_file.name}' title-only."
            )
            continue

        # This glob deliberately takes every file with the stem, not just audio, so
        # sidecars and thumbnails move with the track. A sidecar whose target already
        # exists is left behind rather than renamed over.
        moved = 0
        for path in output_path.glob(f"{escape(stem)}.*"):
            if not path.is_file():
                continue
            new_path = path.with_name(new_stem + path.name[len(stem) :])
            if new_path.exists():
                logger.warning(f"'{new_path.name}' already exists. Leaving '{path.name}' as it is.")
                continue
            if dry_run:
                logger.info(f"Would rename '{path.name}' to '{new_path.name}'")
                moved += 1
                continue
            try:
                path.rename(new_path)
            except OSError as e:
                logger.warning(f"Could not rename '{path.name}': {e}")
                continue
            logger.info(f"Renamed '{path.name}' to '{new_path.name}'")
            moved += 1

        if not moved:
            continue
        renamed += 1
        if dry_run or not entry:
            continue
        append_to_history(
            history_path,
            {
                **entry,
                "file_path": str(new_audio),
                "renamed_at": datetime.now(HONG_KONG_TZ).isoformat(),
            },
        )
    return renamed


def confirm_duplicate_download(title: str, existing_files: list[Path]) -> bool:
    """Ask whether to download a same-title track as a separate file."""
    existing_names = ", ".join(path.name for path in existing_files)
    prompt = (
        f"Existing audio file(s) for '{title}' found: {existing_names}. "
        "Download a separate artist-suffixed file and rename the existing one to "
        "match? [y/N]: "
    )

    try:
        response = input(prompt).strip().casefold()
    except (EOFError, OSError):
        logger.warning("No duplicate-download response available. Skipping track.")
        return False

    return response in {"y", "yes"}


def build_duplicate_output_template(
    output_path: Path, title: str, artist: str, video_id: str
) -> str:
    """Build a collision-safe output template for a confirmed duplicate title."""
    artist_stem = render_filename_stem(title, artist)
    if find_existing_audio_files(output_path, artist_stem):
        logger.info(
            "Artist-suffixed filename already exists; appending the video ID to keep the "
            "download separate."
        )
        suffix = f" [{video_id}]"
    else:
        suffix = ""

    return str(output_path / f"%(title)s - {ARTIST_TEMPLATE}{suffix}.%(ext)s")


def _cookie_opts(args) -> dict:
    """Build the yt-dlp cookie options from the mutually exclusive CLI flags."""
    if args.browser:
        return {"cookiesfrombrowser": (args.browser,)}
    if args.cookies:
        return {"cookiefile": str(args.cookies)}
    return {}


def _postprocessors(audio_format: str, add_metadata: bool, embed_thumbnail: bool) -> list[dict]:
    """Build the yt-dlp postprocessor chain for the requested output."""
    postprocessors = []

    # Add conversion postprocessor only if a specific format is requested
    if audio_format != "best":
        postprocessors.append(
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": audio_format,
                "preferredquality": "0",  # Use highest VBR quality for conversions
                "nopostoverwrites": False,
            }
        )

    if add_metadata:
        postprocessors.append(
            {
                "key": "FFmpegMetadata",
                "add_metadata": True,
                "add_chapters": True,
                "add_infojson": "if_exists",
            }
        )

    if embed_thumbnail:
        postprocessors.extend(
            [
                {"key": "FFmpegThumbnailsConvertor", "format": "jpg", "when": "before_dl"},
                {"key": "EmbedThumbnail", "already_have_thumbnail": False},
            ]
        )

    return postprocessors


def _download_opts(args, output_path: Path, cookie_opts: dict) -> dict:
    """Build the yt-dlp options used for the download itself."""
    embed_thumbnail = not args.no_thumbnail

    return {
        "format": args.quality,
        "outtmpl": {"default": str(output_path / "%(title)s.%(ext)s")},
        "postprocessors": _postprocessors(args.audio_format, not args.no_metadata, embed_thumbnail),
        "writethumbnail": embed_thumbnail,
        "convert_thumbnails": "jpg",
        "quiet": logger.level != logging.DEBUG,
        "no_warnings": logger.level != logging.DEBUG,
        "extract_flat": "discard_in_playlist",
        "fragment_retries": 10,
        "retries": 10,
        "ignoreerrors": "only_download",
        "extractor_args": {"youtube": {"lang": ["ja"]}},
        **_build_js_opts(),
        **cookie_opts,
    }


def _meta_opts(cookie_opts: dict) -> dict:
    """Build the yt-dlp options used for extraction without downloading."""
    return {
        "quiet": logger.level != logging.DEBUG,
        "no_warnings": logger.level != logging.DEBUG,
        **_build_js_opts(),
        **cookie_opts,
    }


def _without_cookies(opts: dict, cookie_opts: dict) -> dict:
    """Copy of ``opts`` without the cookie entries, for the unauthenticated retry."""
    return {key: value for key, value in opts.items() if key not in cookie_opts}


def download_command(args):
    """Main logic for the download command."""
    # Convert paths
    output_path = args.output
    history_path = args.history

    # Ensure output directory exists
    output_path.mkdir(parents=True, exist_ok=True)

    # Load history
    logger.info(f"Loading history from {history_path}")
    history_entries = load_history_entries(history_path)
    downloaded_ids = {entry["id"] for entry in history_entries}
    entries_by_path = {
        entry["file_path"]: entry for entry in history_entries if entry.get("file_path")
    }
    if downloaded_ids:
        logger.info(f"Found {len(downloaded_ids)} previously downloaded tracks")

    # Build cookie options early so they are available for info extraction
    cookie_opts = _cookie_opts(args)

    # Get video information from all URLs
    all_videos = []
    is_playlist = False
    for url in args.urls:
        logger.info(f"Extracting video information from: {url}")
        videos_from_url, url_is_playlist = get_video_info(url, cookie_opts)
        all_videos.extend(videos_from_url)
        if url_is_playlist:
            is_playlist = True

    if not all_videos:
        logger.warning("No videos found from the provided URLs. Exiting.")
        return

    videos = all_videos
    if is_playlist:
        logger.info(f"Found a total of {len(videos)} videos from all provided URLs.")

    ydl_opts = _download_opts(args, output_path, cookie_opts)
    meta_ydl_opts = _meta_opts(cookie_opts)
    # Captured up front: yt-dlp keeps only a shallow copy of the options, so the
    # inner outtmpl dict is shared and the loop rewrites it per track.
    default_outtmpl = ydl_opts["outtmpl"]["default"]

    # Prepare unauthenticated fallback options if cookie authentication is enabled
    fallback_ydl_opts = _without_cookies(ydl_opts, cookie_opts) if cookie_opts else None
    fallback_meta_ydl_opts = _without_cookies(meta_ydl_opts, cookie_opts) if cookie_opts else None

    # Statistics
    downloaded_count = 0
    skipped_count = 0
    failed_count = 0
    failed_videos = []

    # Process each video
    with (
        yt_dlp.YoutubeDL(ydl_opts) as ydl,
        yt_dlp.YoutubeDL(meta_ydl_opts) as meta_ydl,
        yt_dlp.YoutubeDL(fallback_ydl_opts)
        if fallback_ydl_opts
        else contextlib.nullcontext() as fallback_ydl,
        yt_dlp.YoutubeDL(fallback_meta_ydl_opts)
        if fallback_meta_ydl_opts
        else contextlib.nullcontext() as fallback_meta_ydl,
    ):
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
                    if fallback_meta_ydl:
                        logger.warning(
                            f"Metadata extraction with cookies failed for {video_id}: {e}. Retrying without cookies..."
                        )
                        try:
                            video = fallback_meta_ydl.extract_info(
                                f"https://music.youtube.com/watch?v={video_id}",
                                download=False,
                            )
                        except Exception as fallback_e:
                            logger.error(f"Failed to get info for video {video_id}: {fallback_e}")
                            failed_count += 1
                            failed_videos.append(video_id)
                            continue
                    else:
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
                rename_title_only_files(
                    output_path, title, entries_by_path, history_path, dry_run=True
                )
                if find_same_title_files(output_path, title):
                    logger.info(
                        f"    Would save the new file as: {render_filename_stem(title, artist)}.*"
                    )
                continue

            # Normal download
            logger.info(f"[{idx}/{len(videos)}] Downloading: {artist} - {title}")

            # Rename before choosing the template: build_duplicate_output_template()
            # picks the new filename from the directory, so a same-artist clash has to
            # see the renamed file or it would be written over the older recording.
            existing_files = find_same_title_files(output_path, title)
            if existing_files:
                logger.info(
                    f"Found {len(existing_files)} existing audio file(s) with title '{title}'."
                )

                # migrate and verify pass prompt_on_duplicate=False so batch runs
                # rename title-only files without waiting for input.
                prompt_on_duplicate = args.prompt_on_duplicate
                if prompt_on_duplicate and not confirm_duplicate_download(title, existing_files):
                    logger.info(f"Skipping duplicate-title track: {artist} - {title}")
                    skipped_count += 1
                    continue

                rename_title_only_files(output_path, title, entries_by_path, history_path)

                target_outtmpl = build_duplicate_output_template(
                    output_path, title, artist, video_id
                )
            else:
                target_outtmpl = default_outtmpl

            ydl.params["outtmpl"]["default"] = target_outtmpl

            try:
                info = ydl.extract_info(
                    f"https://music.youtube.com/watch?v={video_id}", download=True
                )
                if info is None and fallback_ydl:
                    raise RuntimeError("Download failed with cookies (no info returned)")
            except Exception as e:
                if fallback_ydl:
                    logger.warning(
                        f"Authenticated download failed for {video_id}: {e}. Retrying without cookies..."
                    )
                    fallback_ydl.params["outtmpl"]["default"] = target_outtmpl
                    try:
                        info = fallback_ydl.extract_info(
                            f"https://music.youtube.com/watch?v={video_id}", download=True
                        )
                    except Exception as fallback_err:
                        logger.error(f"✗ Failed to download {video_id}: {fallback_err}")
                        failed_count += 1
                        failed_videos.append(f"{artist} - {title} ({video_id})")
                        if not is_playlist:
                            sys.exit(1)
                        continue
                else:
                    logger.error(f"✗ Failed to download {video_id}: {e}")
                    failed_count += 1
                    failed_videos.append(f"{artist} - {title} ({video_id})")
                    if not is_playlist:
                        sys.exit(1)
                    continue

            try:
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
                logger.error(f"✗ Failed to process output for {video_id}: {e}")
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
