# Image Tool

A multi-functional toolkit for image and video manipulation.

## Features

- ✅ **Coordinate Marking**: Click on images to mark coordinates
- ✅ **Frame Extraction**: Extract specific frames from videos
- ✅ **Image Capture**: Capture images from camera devices

## Installation

Install the Image Tool with its specific dependencies:

```bash
uv sync --group image_tool
```

## Configuration

Add these settings to your `.env` file (all optional):

| Variable | Default | Description |
|----------|---------|-------------|
| `IMAGE_TOOL_DEFAULT_OUTPUT_DIR` | `.` | Default output directory for extracted frames |
| `IMAGE_TOOL_DEFAULT_SAVE_DIR` | `./images` | Default directory for captured images |
| `IMAGE_TOOL_DEFAULT_CAMERA_INDEX` | `0` | Default camera device index |
| `IMAGE_TOOL_DEFAULT_RESIZE_RATIO` | `0.5` | Default resize ratio for coordinate marking |

## Usage

The tool provides three subcommands:

```bash
python -m image_tool <subcommand> [options]
```

---

## Subcommand: `coords`

View an image and mark coordinates by clicking.

### Usage

```bash
python -m image_tool coords <image_path> [--ratio RATIO]
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `image_path` | ✅ | Path to the image file |
| `--ratio` | ❌ | Resize ratio for display (e.g., `0.5` for 50% size) |

### How It Works

1. The image opens in a window
2. Click on points of interest
3. Coordinates are displayed and saved to a new image with markers
4. Press any key to close the window

### Example

```bash
python -m image_tool coords "screenshot.png" --ratio 0.5
```

**Use cases:**
- UI/UX testing: Mark clickable regions
- Computer vision: Label training data
- Documentation: Highlight areas in screenshots

---

## Subcommand: `frame`

Extract a specific frame from a video file.

### Usage

```bash
python -m image_tool frame -v <video> -t <time> [-o <output>]
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `-v`, `--video` | ✅ | Path to the input video file |
| `-t`, `--time` | ✅ | Time in seconds at which to extract the frame |
| `-o`, `--output` | ❌ | Directory to save the extracted frame (default from config) |

### Example

Extract a frame at 1 minute 30 seconds:

```bash
python -m image_tool frame \
  -v "my_video.mp4" \
  -t 90 \
  -o "frames/"
```

**Output:** `frames/my_video_frame_90s.jpg`

**Use cases:**
- Create video thumbnails
- Extract specific scenes
- Generate reference images for editing

---

## Subcommand: `capture`

Capture images from a camera device.

### Usage

```bash
python -m image_tool capture [-c CAMERA] [-s SAVE_DIR]
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `-c`, `--camera` | ❌ | Camera index (0 for default, 1 for external, etc.) |
| `-s`, `--save_dir` | ❌ | Directory to save captured images |

### Example

Capture from an external camera:

```bash
python -m image_tool capture -c 1 -s "captures/"
```

**Use cases:**
- Quick photo capture without opening camera apps
- Scripted image acquisition
- Security/monitoring snapshots

---

## Troubleshooting

### Issue: "Cannot open image file"

**Solution**: 
- Verify the file path is correct
- Ensure the image format is supported (JPG, PNG, BMP, etc.)
- Check file permissions

### Issue: Coordinate marking window doesn't appear

**Solution**:
- Ensure you have a display (X11/Wayland on Linux, not headless SSH)
- Try reducing `--ratio` if the image is very large
- Check that OpenCV is properly installed

### Issue: "Cannot open video file"

**Solution**:
- Verify video codecs are supported
- On Linux, you may need: `sudo apt install ffmpeg`
- Try converting the video to MP4 format

### Issue: Camera not found (capture command)

**Solution**:
- List available cameras:
  ```bash
  ls /dev/video*  # Linux
  ```
- Try different camera indices: `-c 0`, `-c 1`, etc.
- Ensure camera permissions (Linux users may need to be in `video` group)

### Issue: Frame extraction at wrong time

**Solution**:
- Time is in **seconds**, not `MM:SS` format
- Use decimal values for precision: `-t 90.5` for 1:30.5
- Note: Some video formats may have keyframe limitations

## Next Steps

- 📖 [Setup Guide](../setup.md) - Configure defaults and output directories
- 🏠 [Back to Main README](../../README.md)
