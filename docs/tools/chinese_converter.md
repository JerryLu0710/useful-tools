# Chinese Converter

A flexible, multi-format tool for converting Chinese text between Simplified and Traditional characters.

## Features

- ✅ Supports `.epub` and `.txt` files
- ✅ Multiple conversion profiles (Simplified ↔ Traditional)
- ✅ Batch processing for directories
- ✅ Automatic backup creation
- ✅ Extensible architecture (easy to add new formats)

## Installation

Install the Chinese Converter with its specific dependencies:

```bash
uv sync --group chinese_converter
```

## Configuration

Add these settings to your `.env` file (all optional):

| Variable | Default | Description |
|----------|---------|-------------|
| `CHINESE_CONVERTER_DEFAULT_CONVERSION` | `s2t` | Default conversion type |
| `CHINESE_CONVERTER_CREATE_BACKUP` | `true` | Create backup files before conversion |
| `CHINESE_CONVERTER_BACKUP_SUFFIX` | `.backup` | Suffix for backup files |

## Usage

Run from the project root:

```bash
python -m chinese_converter <input> [output] [options]
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `input` | ✅ | Source file (`.epub`, `.txt`) or directory |
| `output` | ❌ | Destination file or directory. If omitted, generates default name with `_trad` suffix |
| `-t`, `--type` | ❌ | Conversion type (default: `s2t`) |
| `-b`, `--batch` | ❌ | Enable batch processing for directories |
| `--no-backup` | ❌ | Disable backup creation for single files |

### Conversion Types

| Type | Description | Example |
|------|-------------|---------|
| `s2t` | Simplified → Traditional (generic) | 软件 → 軟體 |
| `s2tw` | Simplified → Traditional (Taiwan) | 软件 → 軟體 |
| `s2hk` | Simplified → Traditional (Hong Kong) | 软件 → 軟件 |
| `t2s` | Traditional → Simplified | 軟體 → 软件 |

## Examples

### Convert a Single EPUB File

Converts `my_book.epub` to `my_book_trad.epub`:

```bash
python -m chinese_converter "path/to/my_book.epub"
```

### Specify Output Location

```bash
python -m chinese_converter "input.epub" "output/converted.epub"
```

### Convert Traditional to Simplified

```bash
python -m chinese_converter "traditional_book.txt" --type t2s
```

### Batch Convert a Directory

Converts all `.epub` and `.txt` files from `books_simplified/` and saves them in `books_traditional/`:

```bash
python -m chinese_converter "books_simplified" "books_traditional" --batch
```

### Disable Backup

```bash
python -m chinese_converter "my_file.epub" --no-backup
```

## How It Works

The tool uses the [OpenCC](https://github.com/BYVoid/OpenCC) library for accurate Chinese character conversion with context-aware transformations.

**Architecture:**
- **Handler pattern**: Each file format (EPUB, TXT) has its own handler class
- **Extensible**: Add new formats by implementing the handler interface
- See [`chinese_converter/handlers.py`](../../chinese_converter/handlers.py) for implementation details

## Troubleshooting

### Issue: "Unsupported file type"

**Solution**: Only `.epub` and `.txt` files are supported. Check your file extension.

### Issue: Output file is corrupted

**Solution**: 
1. Check that you have write permissions to the output directory
2. Ensure sufficient disk space
3. Try with `--no-backup` to rule out backup-related issues

### Issue: Conversion seems incorrect

**Solution**: Try different conversion types:
- For Taiwan localization: use `--type s2tw`
- For Hong Kong localization: use `--type s2hk`

## Next Steps

- 📖 [Setup Guide](../setup.md) - Configure logging and environment
- 🏠 [Back to Main README](../../README.md)
