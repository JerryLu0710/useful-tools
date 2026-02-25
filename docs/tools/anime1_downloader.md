# Anime1 Downloader

A command-line tool to download videos from anime1.me with Cloudflare bypass support.

## Features

- ✅ Download single episodes or entire series
- ✅ Multi-threaded downloading for faster performance
- ✅ Bypass Cloudflare protection with cookies
- ✅ Extract video URLs without downloading
- ✅ Automatic organization by series name

## Installation

Install the Anime1 Downloader with its specific dependencies:

```bash
uv sync --group anime1_downloader
```

## Configuration

Add these settings to your `.env` file:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ANIME1_DOWNLOAD_DIR` | ✅ | `/path/to/target/directory` | Base directory for downloaded videos |
| `ANIME1_MAX_CONCURRENT_DOWNLOADS` | ❌ | `4` | Maximum concurrent downloads |

Videos are saved to: `<ANIME1_DOWNLOAD_DIR>/<anime_series_name>/`

## Usage

Run from the project root:

```bash
python -m anime1_downloader <url> [options]
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `url` | ✅ | Direct URL to an anime1.me page (e.g., `https://anime1.me/18305`) |
| `-x`, `--extract` | ❌ | Only extract video URLs without downloading |
| `-cf`, `--cloudflare` | ❌ | `cf_clearance` cookie to bypass Cloudflare (valid for ~1 hour) |
| `-ua`, `--user-agent` | ❌ | Custom user-agent string |
| `-o`, `--output-dir` | ❌ | Override the base output directory |
| `-j`, `--max-concurrent-downloads` | ❌ | Override max concurrent downloads |

> [!TIP]
> Wrap URLs and cookie values in quotes to avoid shell parsing issues:
> ```bash
> python -m anime1_downloader "https://anime1.me/18305"
> ```

## Examples

### Download a Series

```bash
python -m anime1_downloader "https://anime1.me/18305"
```

### Extract URLs Only (No Download)

Useful for inspecting what would be downloaded:

```bash
python -m anime1_downloader "https://anime1.me/18305" --extract
```

### Bypass Cloudflare Protection

If you encounter Cloudflare challenges, extract the `cf_clearance` cookie from your browser:

```bash
python -m anime1_downloader "https://anime1.me/18305" \
  --cloudflare "your_cf_clearance_cookie_value"
```

### Custom Output Directory

```bash
python -m anime1_downloader "https://anime1.me/18305" \
  --output-dir "/custom/path" \
  --max-concurrent-downloads 8
```

## How to Get the Cloudflare Cookie

1. Open anime1.me in your browser (Chrome/Firefox)
2. Open Developer Tools (F12)
3. Go to: **Application** (Chrome) or **Storage** (Firefox) → **Cookies**
4. Find the `cf_clearance` cookie and copy its value
5. Use it with the `--cloudflare` option

> [!WARNING]
> The `cf_clearance` cookie typically expires after **1 hour**. You'll need to refresh it periodically if downloads fail.

## Troubleshooting

### Issue: "Cloudflare protection detected"

**Solution**: 
1. Get a fresh `cf_clearance` cookie from your browser
2. Use the `--cloudflare` option with the cookie value
3. Optionally add `--user-agent` matching your browser

### Issue: Downloads are slow

**Solution**: Increase concurrent downloads:
```bash
python -m anime1_downloader "URL" -j 8
```

> [!CAUTION]
> Setting `-j` too high may cause:
> - Rate limiting from the server
> - Network congestion
> - Incomplete downloads

**Recommended values:**
- Fast connection: `-j 8`
- Moderate connection: `-j 4` (default)
- Slow connection: `-j 2`

### Issue: "Permission denied" when saving

**Solution**: 
1. Check `ANIME1_DOWNLOAD_DIR` in `.env` exists and is writable
2. Verify you have write permissions
3. Try using `--output-dir` with a different path

### Issue: Videos are incomplete or corrupted

**Solution**:
1. Reduce concurrent downloads to `-j 2`
2. Check your internet connection stability
3. Re-run the command (it will skip already-downloaded files)

## Next Steps

- 📖 [Setup Guide](../setup.md) - Configure download directory and logging
- 🏠 [Back to Main README](../../README.md)
