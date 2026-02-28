"""Image tool specific configuration."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


class ImageToolConfig:
    """Image tool specific configuration."""

    DEFAULT_OUTPUT_DIR = Path(os.getenv("IMAGE_TOOL_DEFAULT_OUTPUT_DIR", "."))
    DEFAULT_SAVE_DIR = Path(os.getenv("IMAGE_TOOL_DEFAULT_SAVE_DIR", "images"))
    DEFAULT_CAMERA_INDEX = int(os.getenv("IMAGE_TOOL_DEFAULT_CAMERA_INDEX", 0))
    DEFAULT_RESIZE_RATIO = float(os.getenv("IMAGE_TOOL_DEFAULT_RESIZE_RATIO", 0.5))
