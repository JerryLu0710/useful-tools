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
| `--no-backup` | Do not copy the input file before converting it. Applies to a single file and to `--batch`. |

```bash
uv run python -m chinese_converter "book.epub"
uv run python -m chinese_converter "traditional.txt" --type t2s
uv run python -m chinese_converter "input-dir" "output-dir" --batch
```

When output is omitted, a file is written with a `_trad` suffix.
Supported input types are `.epub` and `.txt`.
An input is copied to `<name><suffix>.backup` (see `BACKUP_SUFFIX`) only after it passes validation, so an unsupported or invalid input leaves no backup behind.
A converter failure fails the run instead of writing an unconverted copy: exit code `1`, and in `--batch` exit code `1` means at least one file failed.
Format-specific behavior is implemented by the handlers in [`chinese_converter/formats/`](../../chinese_converter/formats/).
