# Configuration Reference

Reference for the project-wide settings.
Tool-specific keys are documented by each tool guide; the list at the end points to them.

Settings come from a `.env` file in the project root, read by [`config.py`](../config.py) at import time.
The file is located next to `config.py`, not in the current working directory, so one `.env` serves every tool however it is invoked.
A change takes effect on the next run: nothing reloads it in place.

## Logging

These keys apply to every tool.

| Variable | Default | Purpose |
| --- | --- | --- |
| `LOG_LEVEL` | `INFO` | Console detail. One of `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`. |
| `LOG_TO_FILE` | `true` | Write a log file. |
| `LOG_TO_CONSOLE` | `true` | Write to stdout. |
| `LOG_DIRECTORY` | `logs` | Log directory, resolved against the project root. |
| `LOG_MAX_FILE_SIZE` | `10485760` | Bytes per log file before rotation. |
| `LOG_BACKUP_COUNT` | `5` | Rotated log files kept. |

An unrecognised `LOG_LEVEL` value raises at import with a message naming the setting.

## File operations

| Variable | Default | Purpose |
| --- | --- | --- |
| `DEFAULT_ENCODING` | `utf-8` | Encoding used for file reads and writes. |
| `TEMP_DIRECTORY` | `temp` | Base directory for temporary work, resolved against the project root. |
| `TEMP_DIR_PREFIX` | `utility_temp_` | Prefix for temporary directories created inside it. |
| `BACKUP_SUFFIX` | `.backup` | Suffix for backups created before an in-place edit. |

## Path values

- Shared settings above resolve relative paths against the project root.
- Tool output and history settings resolve relative paths against the current working directory, so use absolute paths for anything outside the project.
- A Windows drive from WSL is written as `/mnt/<drive>/...`; the same directory is `<drive>:\...` on Windows. Keep one convention per machine, because recorded paths are not translated.

## Tool-specific settings

| Tool | Guide |
| --- | --- |
| Chinese Converter | [Configuration](tools/chinese_converter.md#configuration) |
| Anime1 Downloader | [Configuration](tools/anime1_downloader.md#configuration) |
| Image Tool | [Configuration](tools/image_tool.md#configuration) |
| YouTube Music Downloader | [Configuration](tools/ytmusic_dl.md#configuration) |
