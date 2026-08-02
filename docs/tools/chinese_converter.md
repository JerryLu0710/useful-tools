# Chinese Converter

Convert Simplified and Traditional Chinese text in EPUB and plain-text files.

## Install

```bash
uv sync --group chinese_converter
```

## Configuration

| Variable | Default | Purpose |
| --- | --- | --- |
| `EPUB_DEFAULT_CONVERSION` | `s2t` | Default OpenCC conversion profile. |
| `BACKUP_SUFFIX` | `.backup` | Suffix used for backups created before conversion. |

## Usage

```bash
uv run python -m chinese_converter INPUT [OUTPUT] [options]
```

| Option | Purpose |
| --- | --- |
| `-t`, `--type` | Choose `s2t`, `s2tw`, `s2hk`, or `t2s`. |
| `-b`, `--batch` | Convert supported files in an input directory. |
| `--no-backup` | Do not create a backup when converting one file. |

```bash
uv run python -m chinese_converter "book.epub"
uv run python -m chinese_converter "traditional.txt" --type t2s
uv run python -m chinese_converter "input-dir" "output-dir" --batch
```

When output is omitted, a file is written with a `_trad` suffix.
Supported input types are `.epub` and `.txt`.
Format-specific behavior is implemented by the handlers in [`chinese_converter/formats/`](../../chinese_converter/formats/).
