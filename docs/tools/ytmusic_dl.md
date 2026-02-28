# YouTube Music Downloader

A tool to download audio from YouTube videos/playlists and manage your local music library.

## Features

- ✅ **Download**: Download audio from YouTube videos, playlists, or channels
- ✅ **Verify**: Check local backup against history to find missing songs
- ✅ **Metadata**: Extract YouTube IDs from downloaded files
- ✅ **Migrate**: Redownload songs from a text list

## Installation

Install the YouTube Music Downloader with its specific dependencies:

```bash
uv sync --group ytmusic_dl
```

## Configuration

Add these settings to your `.env` file:

| Variable | Required | Description |
|----------|----------|-------------|
| `YTMUSIC_DL_DOWNLOAD_DIR` | ✅ | Directory where audio files will be saved |
| `YTMUSIC_DL_HISTORY_FILE` | ✅ | Path to JSONL file tracking download history |

> [!NOTE]
> **WSL Users**: Use WSL paths (e.g., `/mnt/d/Music`). Set paths via environment variables in your `.env` file.

**Example `.env` configuration:**
```bash
YTMUSIC_DL_DOWNLOAD_DIR=/path/to/your/music
YTMUSIC_DL_HISTORY_FILE=/path/to/history.jsonl
```

## Usage

The tool provides four subcommands:

```bash
uv run python -m ytmusic_dl <command> [options]
```

---

## Command: `download`

Download audio from YouTube URLs.

### Usage

```bash
uv run python -m ytmusic_dl download <urls...> [options]
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `urls` | ✅ | One or more YouTube URLs (video/playlist/channel) |
| `-o`, `--output` | ❌ | Output directory (overrides config) |
| `-f`, `--format` | ❌ | Audio format: `mp3`, `m4a`, `opus`, etc. Default: `best` (keeps original) |
| `-dr`, `--dry-run` | ❌ | Show what would be downloaded without actually downloading |

### Examples

**Download a single video:**
```bash
uv run python -m ytmusic_dl download "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

**Download a playlist:**
```bash
uv run python -m ytmusic_dl download "https://music.youtube.com/playlist?list=PLxxxxxxx"
```

**Download multiple URLs:**
```bash
uv run python -m ytmusic_dl download \
  "https://www.youtube.com/watch?v=video1" \
  "https://www.youtube.com/watch?v=video2"
```

**Download and convert to MP3:**
```bash
uv run python -m ytmusic_dl download "URL" --format mp3
```

**Dry run to preview:**
```bash
uv run python -m ytmusic_dl download "URL" --dry-run
```

---

## Command: `verify`

Verify that your local backup matches the download history. Finds missing songs that were recorded in history but are no longer on disk.

### Usage

```bash
uv run python -m ytmusic_dl verify [options]
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `-b`, `--backup-dir` | ❌ | Directory containing backup files (default from config) |
| `-d`, `--download-missing` | ❌ | Automatically download missing songs |

### Examples

**Check for missing songs:**
```bash
uv run python -m ytmusic_dl verify
```

**Check and auto-download missing:**
```bash
uv run python -m ytmusic_dl verify --download-missing
```

**Verify a different directory:**
```bash
uv run python -m ytmusic_dl verify -b "/path/to/backup"
```

---

## Command: `extract-id`

Extract YouTube video IDs from filenames in a directory.

### Usage

```bash
uv run python -m ytmusic_dl extract-id <directory>
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `directory` | ✅ | Directory containing downloaded files |

### Example

```bash
uv run python -m ytmusic_dl extract-id "/path/to/music"
```

**Output:** Lists all YouTube IDs found in filenames (e.g., `dQw4w9WgXcQ`)

**Use cases:**
- Rebuild history file from existing downloads
- Audit what's been downloaded
- Create playlists from local files

---

## Command: `migrate`

Redownload songs from a text file containing YouTube URLs or IDs.

### Usage

```bash
uv run python -m ytmusic_dl migrate <file>
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `file` | ✅ | Text file with YouTube URLs or IDs (one per line) |

### Example

Create a `songs.txt` file:
```
https://www.youtube.com/watch?v=dQw4w9WgXcQ
https://www.youtube.com/watch?v=9bZkp7q19f0
oHg5SJYRHA0
```

Then migrate:
```bash
uv run python -m ytmusic_dl migrate songs.txt
```

**Use cases:**
- Migrate to a new computer
- Restore from backup list
- Batch redownload after cleanup

---

## How It Works

### Download History

The tool maintains a JSONL (JSON Lines) file tracking all downloads:

```json
{"id": "dQw4w9WgXcQ", "title": "Rick Astley - Never Gonna Give You Up", "timestamp": "2024-01-15T10:30:00"}
{"id": "9bZkp7q19f0", "title": "PSY - GANGNAM STYLE", "timestamp": "2024-01-15T10:31:00"}
```

This allows the `verify` command to detect missing files.

### File Naming

Downloaded files include the YouTube ID in the filename:
```
Rick Astley - Never Gonna Give You Up [dQw4w9WgXcQ].opus
```

This enables:
- Deduplication (won't redownload existing files)
- ID extraction for rebuilding history
- Easy identification of source videos

## Troubleshooting

### Issue: "yt-dlp not found" or download errors

**Solution**: 
```bash
# Update yt-dlp to latest version
uv sync --group ytmusic_dl --upgrade-package yt-dlp
```

> [!TIP]
> `yt-dlp` is frequently updated to handle YouTube changes. If downloads fail, updating `yt-dlp` often fixes the issue.

### Issue: "Permission denied" writing files

**Solution**:
- Verify `YTMUSIC_DL_DOWNLOAD_DIR` exists and is writable
- Check directory permissions
- On WSL, ensure Windows partition is mounted with proper permissions

### Issue: verify command reports many missing files

**Solution**:
1. Check if files were moved/renamed manually
2. Use `extract-id` to see what's actually present
3. Run `verify --download-missing` to restore them

### Issue: Downloads are very slow

**Solution**:
- YouTube may throttle based on IP/rate
- Try downloading in smaller batches
- Consider using `--format best` to avoid conversion overhead

### Issue: Wrong audio quality

**Solution**:
```bash
# Explicitly request format
uv run python -m ytmusic_dl download "URL" --format m4a  # Higher quality
uv run python -m ytmusic_dl download "URL" --format opus # Good quality, smaller size
```

### Issue: History file corrupted

**Solution**:
1. Backup the current history file
2. Use `extract-id` to rebuild from existing downloads
3. Manually fix any malformed JSON lines

## Next Steps

- 📖 [Setup Guide](../setup.md) - Configure download paths and WSL setup
- 🏠 [Back to Main README](../../README.md)
