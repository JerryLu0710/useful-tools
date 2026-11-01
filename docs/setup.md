# Setup

How to get the tools running from a clean checkout.
Settings and their defaults are reference material: see [Configuration Reference](configuration.md).
Why the project uses `uv` groups and `uv run`: see [Architecture](architecture.md#dependencies).

## Prerequisites

- **Python**: version 3.10 or higher
- **uv**: package and environment manager ([installation guide](https://github.com/astral-sh/uv))

## Initial setup

### 1. Clone the repository

```bash
git clone <repository-url>
cd useful_tools
```

### 2. Create the local configuration

```bash
cp .env.example .env
```

Edit `.env` afterwards to change any setting.
The file is optional: every setting has a default.

### 3. Install the base project

`uv` creates and manages the virtual environment:

```bash
uv sync
```

This creates `.venv` if it is missing, installs the core dependencies from `pyproject.toml`, and
updates `uv.lock`. There is no virtual environment to create or activate by hand.

### 4. Install the dependencies of the tools you use

```bash
# one tool
uv sync --group chinese_converter

# several tools
uv sync --group chinese_converter --group ytmusic_dl

# everything, including development tooling
uv sync --all-groups
```

### 5. Run a command

```bash
uv run python -m chinese_converter "file.epub"
uv run ruff check .
```

`uv run` uses the project environment without activation.

## Paths on WSL

To write to a Windows drive from WSL, give the path in WSL form:

```bash
YTMUSIC_DL_DOWNLOAD_DIR=/mnt/d/Music
```

The same directory is `D:\Music` on Windows, and recorded paths are not translated between the
two. Pick one host per library and keep its convention.

## Troubleshooting

### "Module not found"

The tool's dependency group is not installed:

```bash
uv sync --group chinese_converter
```

### Logs not appearing

Check `LOG_TO_FILE`, `LOG_TO_CONSOLE` and `LOG_LEVEL` in `.env`.
For more console detail set `LOG_LEVEL=DEBUG`; a tool's own log-level option cannot add detail
beyond what `LOG_LEVEL` allows.

### Permission denied when creating log files

Make the log directory writable:

```bash
mkdir -p logs
chmod 755 logs
```

### Environment variables not loading

1. Confirm `.env` exists in the project root, next to `config.py`.
2. Check the syntax: values need no quotes.
3. Start a new process. Settings are read at import, so a running command keeps the old values.

### `uv sync` fails

1. Check that `pyproject.toml` is valid TOML.
2. Update `uv` with its own self-update mechanism.
3. Delete only the local `.venv` and run `uv sync` again.

## Next steps

- 📚 [Available tools](../README.md)
- 🛠️ [Repository instructions](../AGENTS.md)
- 🏗️ [Architecture](architecture.md)
- ⚙️ [Configuration reference](configuration.md)
