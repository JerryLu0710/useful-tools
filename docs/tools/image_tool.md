# Image Tool

Inspect images, extract video frames, and capture camera images.

## Install

```bash
uv sync --group image_tool
```

## Configuration

| Variable | Default | Purpose |
| --- | --- | --- |
| `IMAGE_TOOL_DEFAULT_OUTPUT_DIR` | `.` | Default frame-output directory. |
| `IMAGE_TOOL_DEFAULT_SAVE_DIR` | `images` | Default camera-capture directory. |
| `IMAGE_TOOL_DEFAULT_CAMERA_INDEX` | `0` | Default camera index. |
| `IMAGE_TOOL_DEFAULT_RESIZE_RATIO` | `0.5` | Default display scaling for coordinate marking. |

## Commands

```bash
uv run python -m image_tool coords IMAGE [--ratio RATIO]
uv run python -m image_tool frame --video VIDEO --time SECONDS [--output DIRECTORY]
uv run python -m image_tool capture [--camera INDEX] [--save_dir DIRECTORY]
```

`coords` displays an image and records clicked coordinates on screen.
Press `s` to save a marked image as `<input-stem>_marked.jpg` in the current working directory.
Press `q` to close the window.

`frame` accepts an integer number of seconds and writes `frame_at_<seconds>s.jpg` to the selected output directory.

```bash
uv run python -m image_tool coords "screenshot.png" --ratio 0.5
uv run python -m image_tool frame --video "video.mp4" --time 90 --output "frames"
uv run python -m image_tool capture --camera 0 --save_dir "captures"
```

The image and camera commands require an interactive display and a camera for capture.
