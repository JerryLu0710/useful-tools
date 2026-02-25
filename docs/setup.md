# Setup and Configuration Guide

This guide covers the initial setup, environment configuration, and system-wide settings for the Useful Tools project.

## Prerequisites

- **Python**: Version 3.10 or higher
- **uv**: Recommended package manager ([installation guide](https://github.com/astral-sh/uv))
    - Alternatively, you can use `pip` and `venv`

## Initial Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd useful_tools
```

### 2. Configure Environment Variables

The project uses a `.env` file for configuration (e.g., log levels). Copy the example file to create your own local configuration:

```bash
cp .env.example .env
```

You can then edit the `.env` file to customize settings.

### 3. Install the Base Project

`uv` automatically creates and manages the virtual environment for you:

```bash
uv sync
```

This command:
- ✅ Creates a `.venv` directory if it doesn't exist
- ✅ Installs core dependencies from `pyproject.toml`
- ✅ Updates `uv.lock` for reproducibility
- ✅ Makes the project's packages available

> [!NOTE]
> No need to manually create or activate a virtual environment! `uv sync` handles everything.

### 4. Install Tool-Specific Dependencies

To use a specific tool, install its dependency group:

```bash
# Install Chinese Converter dependencies
uv sync --group chinese_converter

# Install multiple tools
uv sync --group chinese_converter --group ytmusic_dl

# Install ALL tools
uv sync --all-groups
```

### 5. Run Commands

Use `uv run` to execute commands in the project environment:

```bash
# Run a tool
uv run python -m chinese_converter "file.epub"

# Run ruff linting
uv run ruff check ./
```

> [!TIP]
> `uv run` automatically uses the project's virtual environment, no need to activate it manually!

### 4. Configure Environment Variables

Copy the example configuration file:

```bash
cp .env.example .env
```

Then edit `.env` to customize your settings (see [Configuration Reference](#configuration-reference) below).

## Understanding the Modern uv Workflow

### What is `uv sync`?

`uv sync` synchronizes your project environment with the dependencies defined in:
- `pyproject.toml` - Dependency declarations
- `uv.lock` - Locked versions for reproducibility

It's **faster** and more **reliable** than traditional `pip install`.

### Dependency Groups

Instead of optional dependencies, we use **dependency groups** (PEP 735):

```toml
[dependency-groups]
chinese_converter = ["opencc-python-reimplemented~=0.1.7", ...]
dev = ["ruff>=0.14.3"]
```

Install them with:
```bash
uv sync --group chinese_converter
uv sync --group dev  # Install development tools
```

### Why `uv run`?

`uv run` executes commands in the project's virtual environment **without manual activation**:

```bash
# Old way
source .venv/bin/activate
python -m chinese_converter "file.epub"

# Modern way
uv run python -m chinese_converter "file.epub"
```

---

## Configuration Reference

The project uses a `.env` file for configuration. All settings are loaded by [`config.py`](../config.py) and made available to utilities.

### General Project Settings

#### Logging Configuration

Control logging behavior across all utilities:

| Variable | Default | Description |
|----------|---------|-------------|
| `LOG_LEVEL` | `INFO` | Console and file logging level. Options: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` |
| `LOG_TO_FILE` | `true` | Enable file logging |
| `LOG_TO_CONSOLE` | `true` | Enable console logging |
| `LOG_DIRECTORY` | `logs` | Directory for log files (relative to project root) |
| `LOG_MAX_FILE_SIZE` | `10485760` | Maximum log file size in bytes (10MB default) |
| `LOG_BACKUP_COUNT` | `5` | Number of backup log files to keep |

**How it works:**
- The [`logger_setup.py`](logger_setup.py) module provides a centralized logging system
- Each utility gets its own log file (e.g., `logs/chinese_converter.log`)
- Log files use rotation to prevent unlimited growth
- Console output shows simplified messages; files contain detailed debug info

**Example usage in your code:**
```python
from logger_setup import get_logger

logger = get_logger(__name__)
logger.info("This is an info message")
```

#### File Operations

| Variable | Default | Description |
|----------|---------|-------------|
| `DEFAULT_ENCODING` | `utf-8` | Default file encoding |
| `TEMP_DIRECTORY` | `temp` | Temporary files directory |
| `TEMP_DIR_PREFIX` | `utility_temp_` | Prefix for temporary directories |

### Tool-Specific Settings

Each utility has its own configuration section. See the tool-specific documentation for details:

- [Chinese Converter Configuration](tools/chinese_converter.md#configuration)
- [Anime1 Downloader Configuration](tools/anime1_downloader.md#configuration)
- [Image Tool Configuration](tools/image_tool.md#configuration)
- [YouTube Music Downloader Configuration](tools/ytmusic_dl.md#configuration)
- [Novel Scraper Configuration](tools/novel_scraper.md#configuration)

### Performance Settings

These settings can be used by multiple utilities:

| Variable | Default | Description |
|----------|---------|-------------|
| `MAX_WORKERS` | `4` | Maximum number of concurrent workers for parallel processing |
| `CHUNK_SIZE` | `8192` | Default chunk size for file operations (bytes) |

## Special Considerations

### WSL (Windows Subsystem for Linux) Users

If you're using WSL and need to access Windows paths (e.g., `/mnt/c/...` or `/mnt/d/...`), configure the paths in your `.env` file:

```bash
# Example: point to a Windows drive from WSL
YTMUSIC_DL_DOWNLOAD_DIR=/mnt/d/Music
```

### Path Configuration

When setting directory paths in `.env`:

- **Absolute paths**: Recommended for directories outside the project
    ```bash
    ANIME1_DOWNLOAD_DIR=/home/user/videos
    ```
- **Relative paths**: Used for project-internal directories
    ```bash
    LOG_DIRECTORY=logs
    ```

## Troubleshooting

### Issue: "Module not found" errors

**Solution**: Make sure you've installed the tool-specific dependencies:
```bash
uv sync --group chinese_converter
```

### Issue: Logs not appearing

**Solution**: Check these settings in `.env`:
- `LOG_TO_FILE=true`
- `LOG_TO_CONSOLE=true`
- `LOG_LEVEL=INFO` (or lower for more verbose output)

### Issue: Permission denied when creating log files

**Solution**: Ensure the `LOG_DIRECTORY` path is writable:
```bash
mkdir -p logs
chmod 755 logs
```

### Issue: Environment variables not loading

**Solution**: 
1. Verify `.env` file exists in the project root
2. Check for syntax errors (no quotes needed around values)
3. Run `uv sync` to ensure environment is up to date
4. Restart your terminal/IDE after modifying `.env`

### Issue: `uv sync` fails

**Solution**:
1. Check `pyproject.toml` syntax (must be valid TOML)
2. Update `uv` to latest version: `pip install --upgrade uv`
3. Delete `.venv` and `uv.lock`, then retry: `rm -rf .venv uv.lock && uv sync`

## Next Steps

- 📚 [View available tools](../README.md#available-tools)
- 🛠️ [Contributing guide](../GEMINI.md)
- 📝 [Development workflow](../TASK_LOGGING_GUIDE.md)
