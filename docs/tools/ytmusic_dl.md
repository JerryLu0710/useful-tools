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
| `-q`, `--quality SELECTOR` | Override the yt-dlp format selector. Default: `bestaudio[abr>=200][ext=m4a]/bestaudio[ext=m4a]/bestaudio`. |
| `-hi`, `--history FILE` | Override the history path. |
| `-dr`, `--dry-run` | Show planned downloads without downloading. |
| `--[no-]prompt-on-duplicate` | Confirm before a same-title download renames the existing file. Prompting is enabled by default. |
| `--no-thumbnail` | Do not embed thumbnails. |
| `--no-metadata` | Do not add metadata. |
| `--browser NAME` | Read cookies from Chrome, Firefox, Brave, or Edge. |
| `--cookies FILE` | Use a Netscape-format cookie file. |
| `--force` | Download IDs already recorded in history. |

Downloads use a title-based filename while the title is unique in the output directory.
Once a second track shares that title, every file carrying it becomes artist-suffixed:
the existing title-only file is renamed to `Title - Artist`, sidecars move with it, and the
rename is recorded in history. The new download is then saved as `Title - Artist` too, or as
`Title - Artist [VIDEO_ID]` when that name already belongs to another track by the same artist.
Titles containing `/` or `:` are matched by the sanitised name yt-dlp writes, so an existing
file is never silently replaced.
The artist of an existing title-only file is read from its history entry, falling back to the
file's own tags. If neither is available the file is left title-only and a warning is logged.
A file that cannot be renamed, for example on a read-only mount, is reported and left as it is,
and the download still proceeds.
Renaming happens before the download, and a failed download does not undo it.
`--dry-run` lists the renames it would perform.

With `--browser` or `--cookies`, a track whose authenticated extraction or download fails is
retried without cookies, trading Premium 256 kbps audio for guest streams. If both attempts fail
the track is reported as failed: a single URL exits non-zero, while a playlist continues with the
next track and lists the failures in its summary.

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

`verify` matches audio files to history by the YouTube ID embedded in their tags, never by
filename, so renaming files does not disturb verification.
Files whose tags carry no ID are listed separately, and `--scan-all` searches every tag value
for a YouTube URL.

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
Duplicate-title prompting applies only to the direct `download` command; `migrate` and
`verify --download-missing` rename title-only files without asking.

History records include the video ID, title, artist, download timestamp, output path, and available media metadata.
A rename is recorded by appending a later line with the same video ID and the new output path;
the history file is never rewritten, and the last line for an ID is the current one.
