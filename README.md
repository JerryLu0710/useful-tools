# Useful Tools

A curated collection of command-line utilities for everyday automation tasks.

## 🚀 Quick Start

1. **Clone and set up environment:**
   ```bash
   git clone <repository-url>
   cd useful_tools
   ```

2. **Configure the project:**
   ```bash
   cp .env.example .env
   # Edit .env to customize settings
   ```

3. **Install base package:**
   ```bash
   uv sync
   ```

4. **Install a specific tool:**
   ```bash
   # Example: Install Chinese Converter
   uv sync --group chinese_converter
   ```

> [!TIP]
> Install all tools at once: `uv sync --all-groups`
> 
> This installs dependencies for all tools and development checks.

📖 **Detailed setup guide:** [docs/setup.md](docs/setup.md)

---

## 📦 Available Tools

| Tool | Description | Docs | Install Command |
|------|-------------|------|-----------------|
| **Chinese Converter** | Convert text between Simplified/Traditional Chinese (`.epub`, `.txt`) | [📘 Guide](docs/tools/chinese_converter.md) | `uv sync --group chinese_converter` |
| **Anime1 Downloader** | Download anime from anime1.me with Cloudflare bypass | [📘 Guide](docs/tools/anime1_downloader.md) | `uv sync --group anime1_downloader` |
| **Image Tool** | Mark coordinates, extract video frames, capture from camera | [📘 Guide](docs/tools/image_tool.md) | `uv sync --group image_tool` |
| **YouTube Music DL** | Download & manage music from YouTube with verification | [📘 Guide](docs/tools/ytmusic_dl.md) | `uv sync --group ytmusic_dl` |

---

## 🎯 Quick Usage Examples

### Chinese Converter
```bash
# Convert EPUB from Simplified to Traditional Chinese
uv run python -m chinese_converter "book.epub"
```

### Anime1 Downloader
```bash
# Download an anime series
uv run python -m anime1_downloader "https://anime1.me/18305"
```

### Image Tool
```bash
# Extract frame from video at 90 seconds
uv run python -m image_tool frame -v "video.mp4" -t 90
```

### YouTube Music Downloader
```bash
# Download a playlist
uv run python -m ytmusic_dl download "https://music.youtube.com/playlist?list=..."
```

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [Setup & Configuration](docs/setup.md) | Installation, `.env`, and troubleshooting |
| [Architecture](docs/architecture.md) | Package boundaries and shared conventions |
| [Repository Instructions](AGENTS.md) | Commands and contributor guidance |
| [Documentation Index](docs/README.md) | All maintained documentation |

---

## 🏗️ Project Structure

```
useful_tools/
├── docs/                    # Setup, architecture, and tool guides
│   ├── tools/              # Tool-specific documentation
│   └── standards/          # Repository standards
├── chinese_converter/       # Chinese text conversion
├── anime1_downloader/       # Anime1.me downloader
├── image_tool/             # Image/video utilities
├── ytmusic_dl/             # YouTube music downloader
├── config.py               # Centralized configuration
├── logger_setup.py         # Logging setup
└── pyproject.toml          # Project dependencies
```

---

## 🛠️ Development

### Adding a New Tool

1. Create a new directory: `my_tool/`
2. Add dependencies to `pyproject.toml`:
   ```toml
   [dependency-groups]
   my_tool = ["dependency1", "dependency2"]
   ```
3. Create documentation: `docs/tools/my_tool.md`
4. Update this README to include your tool

### Validation

```bash
# Install all tool and development dependencies
uv sync --all-groups

# Run linting, formatting, and tests
uv run ruff check .
uv run ruff format --check .
uv run pytest
```

### Coding Standards

- Follow **SRP** (Single Responsibility Principle)
- Use **type hints** for all functions
- Add **docstrings** (Google style)
- See [AGENTS.md](AGENTS.md) for repository instructions

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Follow the coding standards in [AGENTS.md](AGENTS.md)
2. Update documentation for any new features
3. Run linting before committing
4. Follow the Open/Closed Principle for extensibility

---

## 📄 License

This project is licensed under the MIT License.

---

## 🔗 Links

- **Setup Guide**: [docs/setup.md](docs/setup.md)
- **Architecture**: [docs/architecture.md](docs/architecture.md)
- **Tool Documentation**: [docs/tools/](docs/tools/)
- **Repository Instructions**: [AGENTS.md](AGENTS.md)

---

Built with ❤️ for automation enthusiasts
