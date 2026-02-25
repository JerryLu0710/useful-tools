"""CLI for image tools."""

import argparse
import os

from image_tool import core
from logger_setup import get_logger

from .config import ImageToolConfig

logger = get_logger(__name__, "image_tool")


def main():
    parser = argparse.ArgumentParser(description="A collection of image tools.")
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

    args = parser.parse_args()

    if args.command == "coords":
        core.mark_coordinates(args.image_path, args.ratio)
    elif args.command == "frame":
        if not os.path.exists(args.output):
            os.makedirs(args.output)
        try:
            output_path = core.extract_frame(args.video, args.time, args.output)
            logger.info(f"Frame at {args.time} seconds saved as {output_path}")
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
    elif args.command == "capture":
        try:
            core.capture_and_save_images(args.camera, args.save_dir)
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
