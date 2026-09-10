"""CLI for image tools."""

import argparse
from pathlib import Path

from image_tool import core
from logger_setup import get_logger

from .config import ImageToolConfig

logger = get_logger(__name__, "image_tool")


def main(args: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="uv run python -m image_tool",
        description="A collection of image tools.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Coords command
    parser_coords = subparsers.add_parser("coords", help="Image viewer and coordinate marker.")
    parser_coords.add_argument("image_path", help="Path to the image file")
    parser_coords.add_argument(
        "--ratio", type=float, default=ImageToolConfig.DEFAULT_RESIZE_RATIO, help="Resize ratio"
    )

    # Frame command
    parser_frame = subparsers.add_parser("frame", help="Video frame extractor.")
    parser_frame.add_argument("-v", "--video", required=True, help="Path to the input video file")
    parser_frame.add_argument(
        "-t",
        "--time",
        type=int,
        required=True,
        help="Time in seconds at which to extract the frame",
    )
    parser_frame.add_argument(
        "-o",
        "--output",
        default=ImageToolConfig.DEFAULT_OUTPUT_DIR,
        help="Directory to save the extracted frame (default: current directory)",
    )

    # Capture command
    parser_capture = subparsers.add_parser("capture", help="Camera capture and image saver.")
    parser_capture.add_argument(
        "-c",
        "--camera",
        type=int,
        default=ImageToolConfig.DEFAULT_CAMERA_INDEX,
        help="Camera index to use (default: 0)",
    )
    parser_capture.add_argument(
        "-s",
        "--save_dir",
        type=str,
        default=ImageToolConfig.DEFAULT_SAVE_DIR,
        help="Directory to save captured images (default: 'images')",
    )

    parsed_args = parser.parse_args(args)

    try:
        if parsed_args.command == "coords":
            core.mark_coordinates(parsed_args.image_path, parsed_args.ratio)
            return 0
        elif parsed_args.command == "frame":
            output_dir = Path(parsed_args.output)
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = core.extract_frame(
                parsed_args.video, parsed_args.time, parsed_args.output
            )
            logger.info(f"Frame at {parsed_args.time} seconds saved as {output_path}")
            return 0
        elif parsed_args.command == "capture":
            core.capture_and_save_images(parsed_args.camera, parsed_args.save_dir)
            return 0
        return 0
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        return 1
