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

## Global option

| Option | Purpose |
| --- | --- |
| `-l`, `--log-level LEVEL` | Minimum level the command logs at: `DEBUG`, `INFO`, `WARNING`, `ERROR`. Default: `INFO`. |

It belongs to the program, not to a subcommand, so it goes before the subcommand name:
`uv run python -m ytmusic_dl -l WARNING prune-history`.

The option can only hide output, never add it. It sets the level of the tool's logger, while the
console stream is filtered by the `LOG_LEVEL` environment variable, so a level below `LOG_LEVEL`
changes nothing on screen. `DEBUG` and `INFO` are also indistinguishable for this tool: no code
path in `ytmusic_dl` logs at `DEBUG`.

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
Files that were already named under the older rule are brought into line by `normalize-names`.

With `--browser` or `--cookies`, a track whose authenticated extraction or download fails is
retried without cookies, trading Premium 256 kbps audio for guest streams. If both attempts fail
the track is reported as failed: a single URL exits non-zero, while a playlist continues with the
next track and lists the failures in its summary. A playlist whose summary contains any failure
also exits non-zero.

```bash
uv run python -m ytmusic_dl download "https://music.youtube.com/playlist?list=PLAYLIST"
uv run python -m ytmusic_dl download "URL" --format mp3 --no-prompt-on-duplicate
```

## Normalize Names

```bash
uv run python -m ytmusic_dl normalize-names [options]
```

| Option | Purpose |
| --- | --- |
| `-o`, `--output DIRECTORY` | Directory to rename files in. |
| `-hi`, `--history FILE` | History file supplying each file's title and artist. |
| `-dr`, `--dry-run` | Print the planned renames without renaming anything. |

Renames existing title-only files so that tracks sharing a title follow the same rule `download`
applies. It runs offline: titles and artists come from the history file and are never guessed from
a filename, because `Song - Live.m4a` could otherwise be an artist-suffixed `Song` or a bare title
of its own. Each rename appends a superseding history line.
A rename is refused when the target filename already exists, so a second run changes nothing.
Audio files missing from the history file are listed and left alone.
The scan covers the output directory itself, not subfolders.

```bash
uv run python -m ytmusic_dl normalize-names -dr
uv run python -m ytmusic_dl normalize-names -o /mnt/d/Music
```

## Prune History

```bash
uv run python -m ytmusic_dl prune-history [options]
```

| Option | Purpose |
| --- | --- |
| `-hi`, `--history FILE` | History file to rewrite. |
| `-dr`, `--dry-run` | Print the lines that would be dropped without touching the file. |

Collapses the history file so each video ID keeps exactly one line: the last one written for
that ID, which is the line carrying the current output path.
Every earlier line for the same ID names a path a rename moved away from, so a reader that
takes the file line by line counts a renamed track twice and reports output paths that no
longer exist.
Kept lines stay in the order their IDs first appeared.
Each dropped line is logged with the path it carried and the path that was kept, so the count
can be checked before applying.
The rewrite goes through a temporary file and an atomic replace, so an interrupted run leaves
the original file intact.

Pruning refuses to run when the file holds lines it cannot read as entries, because those lines
would be lost for good; repair them first and the command exits non-zero.
A missing history file also exits non-zero.
A file that already holds one line per ID is reported and left untouched.
Blank lines are dropped along with the superseded ones.

```bash
uv run python -m ytmusic_dl prune-history -dr
uv run python -m ytmusic_dl prune-history -hi /mnt/d/Music/history.jsonl
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
It scans every audio container a download can produce, so `--format flac` output is verified too.
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
the last line for an ID is the current one, and every earlier line for that ID is superseded.
Commands read history through one shared helper so they all see the current line per ID.
The history file is otherwise never rewritten in place; `prune-history` is the one command that
replaces it, and it does so atomically. See [ADR 0001](../adr/0001-append-only-history-with-explicit-pruning.md).
