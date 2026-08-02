# Anime1 Downloader

Download videos from `anime1.me` pages.

## Install

```bash
uv sync --group anime1_downloader
```

## Configuration

| Variable | Default | Purpose |
| --- | --- | --- |
| `ANIME1_DOWNLOAD_DIR` | `anime` | Base directory for downloaded series. |
| `ANIME1_MAX_CONCURRENT_DOWNLOADS` | `4` | Maximum concurrent episode downloads. |
| `ANIME1_HISTORY_FILE` | `anime_downloaded.jsonl` | JSONL file of completed downloads. |

## Usage

```bash
uv run python -m anime1_downloader URL [options]
```

| Option | Purpose |
| --- | --- |
| `-x`, `--extract` | Print video URLs without downloading. |
| `-cf`, `--cloudflare COOKIE` | Supply a `cf_clearance` cookie. |
| `-ua`, `--user-agent VALUE` | Supply a custom User-Agent header. |
| `-o`, `--output-dir DIR` | Override the base download directory. |
| `-j`, `--max-concurrent-downloads COUNT` | Override concurrent download count. |
| `--history FILE` | Override the JSONL history path. |
| `--force` | Download entries already present in history. |

```bash
uv run python -m anime1_downloader "https://anime1.me/18305"
uv run python -m anime1_downloader "https://anime1.me/18305" --extract
```

Downloads are organized below the selected base directory by series name.
Use quoted cookie values and URLs to avoid shell parsing problems.
