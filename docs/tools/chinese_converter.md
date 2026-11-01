# Chinese Converter

Converts Chinese text between simplified and traditional variants.
New to this tool? Start with the [walk-through](../tutorials/chinese_converter.md).

Convert Simplified and Traditional Chinese text in EPUB and plain-text files.

## Install

```bash
uv sync --group chinese_converter
```

## Configuration

| Variable | Default | Purpose |
| --- | --- | --- |
| `EPUB_DEFAULT_CONVERSION` | `s2t` | Default OpenCC conversion profile. |

## Usage

```bash
uv run python -m chinese_converter INPUT [OUTPUT] [options]
```

| Option | Purpose |
| --- | --- |
| `-t`, `--type` | Choose `s2t`, `s2tw`, `s2hk`, or `t2s`. |
| `-b`, `--batch` | Convert supported files in an input directory. |
| `--no-backup` | Do not copy the input file before converting it. Applies to a single file and to `--batch`. |

`OUTPUT` must directly follow `INPUT`. An option between the two positionals makes the command exit
with status `2` and `unrecognized arguments`.

```bash
uv run python -m chinese_converter "book.epub"
uv run python -m chinese_converter "traditional.txt" --type t2s
uv run python -m chinese_converter "input-dir" "output-dir" --batch
```

Omitting `OUTPUT` names the output from the input, and the rule differs between the two modes:

| Mode | Output location |
| --- | --- |
| Single file | `<stem>_trad<ext>` beside the input. The `_trad` does not change with the conversion direction. |
| `--batch` | Each converted file keeps its own name inside the output directory. Without an output directory, a sibling of the input named `<dir>_trad`. |

Batch mode reads `*.epub` and `*.txt` in the given directory only; it does not descend into
subdirectories.
Supported input types are `.epub` and `.txt`.
An input is copied to `<input><BACKUP_SUFFIX>` (for example `notes.txt.backup`; the suffix is set by
`BACKUP_SUFFIX`, see [the configuration reference](../configuration.md)) only after it passes
validation, so an unsupported or invalid input leaves no backup behind.
A converter failure fails the run instead of writing an unconverted copy: exit code `1`, and in `--batch` exit code `1` means at least one file failed.
Format-specific behavior is implemented by the handlers in [`chinese_converter/formats/`](../../chinese_converter/formats/).
