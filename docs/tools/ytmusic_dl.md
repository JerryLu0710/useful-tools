# YouTube Music Downloader

Download audio from YouTube Music and maintain a local JSONL history.

## Install

```bash
uv sync --group ytmusic_dl
```

## Configuration

| Variable | Default | Purpose |
| --- | --- | --- |
| `YTMUSIC_DL_DOWNLOAD_DIR` | `~/Music` | Default audio output directory. |
| `YTMUSIC_DL_HISTORY_FILE` | `~/.ytmusic_dl/history.jsonl` | Download history path. |

Both values are optional.
Use paths appropriate to the current shell, such as `/mnt/d/Music` in WSL.

## Download

```bash
uv run python -m ytmusic_dl download URL [URL ...] [options]
```

| Option | Purpose |
| --- | --- |
| `-o`, `--output DIRECTORY` | Override the output directory. |
| `-f`, `--format FORMAT` | Convert audio to a requested format, or use `best`. |
| `-q`, `--quality SELECTOR` | Override the yt-dlp format selector. |
| `-hi`, `--history FILE` | Override the history path. |
| `-dr`, `--dry-run` | Show planned downloads without downloading. |
| `--[no-]prompt-on-duplicate` | Confirm same-title downloads. Prompting is enabled by default. |
| `--no-thumbnail` | Do not embed thumbnails. |
| `--no-metadata` | Do not add metadata. |
| `--browser NAME` | Read cookies from Chrome, Firefox, Brave, or Edge. |
| `--cookies FILE` | Use a Netscape-format cookie file. |
| `--force` | Download IDs already recorded in history. |

Downloads normally use a title-based filename.
When an audio file with the same title exists, confirmation downloads a separate artist-suffixed file.
If that filename exists too, the video ID is added to the filename.

```bash
uv run python -m ytmusic_dl download "https://music.youtube.com/playlist?list=PLAYLIST"
uv run python -m ytmusic_dl download "URL" --format mp3 --no-prompt-on-duplicate
```

## Verify

```bash
uv run python -m ytmusic_dl verify [options]
```

| Option | Purpose |
| --- | --- |
| `-b`, `--backup-dir DIRECTORY` | Directory to verify. |
| `--history FILE` | History file to compare. |
| `-s`, `--scan-all` | Deep-scan audio metadata. |
| `-d`, `--download-missing` | Download tracks missing from history. |

## Extract an ID

```bash
uv run python -m ytmusic_dl extract-id AUDIO_FILE
```

The command reads supported metadata tags from one audio file.

## Migrate

```bash
uv run python -m ytmusic_dl migrate INPUT_FILE [options]
```

`INPUT_FILE` can be JSONL history or plain text containing YouTube URLs or video IDs.
The command accepts output, format, quality, history, dry-run, thumbnail, metadata, cookie, and force options equivalent to `download`.
Duplicate-title prompting applies only to the direct `download` command.

History records include the video ID, title, artist, download timestamp, output path, and available media metadata.
