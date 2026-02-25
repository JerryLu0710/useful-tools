# Novel Scraper

A web scraping tool for downloading novels from online sources and converting them to EPUB format.

## Features

- ✅ Web scraping with configurable user-agent
- ✅ EPUB generation from scraped content
- ✅ Chapter organization and metadata

## Installation

Install the Novel Scraper with its specific dependencies:

```bash
uv sync --group novel_scraper
```

## Configuration

Add these settings to your `.env` file (all optional):

| Variable | Default | Description |
|----------|---------|-------------|
| `NOVEL_SCRAPER_OUTPUT_DIR` | `./novels` | Directory for saved EPUB files |
| `NOVEL_SCRAPER_USER_AGENT` | `Mozilla/5.0...` | User-agent string for web requests |
| `NOVEL_SCRAPER_REQUEST_TIMEOUT` | `10` | Request timeout in seconds |

## Usage

> [!NOTE]
> This tool is under development. Usage documentation will be added as scrapers are implemented.

Run from the project root:

```bash
python -m novel_scraper <subcommand> [options]
```

## Architecture

The novel scraper uses a modular architecture:

- **`core.py`**: Core scraping logic and EPUB generation
- **`scrapers/`**: Site-specific scraper implementations
- **`cli.py`**: Command-line interface

To add support for a new website, implement a new scraper in the `scrapers/` directory.

## Troubleshooting

### Issue: "Connection timeout"

**Solution**:
- Increase `NOVEL_SCRAPER_REQUEST_TIMEOUT` in `.env`
- Check your internet connection
- Verify the website is accessible

### Issue: "403 Forbidden" or "blocked"

**Solution**:
- Some sites block automated access
- Try updating `NOVEL_SCRAPER_USER_AGENT` to a recent browser string
- Respect website terms of service and robots.txt

### Issue: Generated EPUB is corrupted

**Solution**:
- Check that all chapters were scraped successfully
- Verify output directory has write permissions
- Try opening with different EPUB readers (some are more forgiving)

## Next Steps

- 📖 [Setup Guide](../setup.md) - Configure output directory and request settings
- 🏠 [Back to Main README](../../README.md)
