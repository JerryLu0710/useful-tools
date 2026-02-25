"""Multi-format Chinese text converter."""

import argparse
import sys
import time
from pathlib import Path

from chinese_converter.formats.epub_handler import EPUBHandler
from chinese_converter.formats.txt_handler import TXTHandler
from chinese_converter.text_converter import ChineseConverter
from config import Config
from logger_setup import get_logger

from .config import EPUBConfig

logger = get_logger(__name__, "chinese_converter")


def get_handler(file_path: str, converter):
    """Get appropriate handler based on file extension."""
    path = Path(file_path)

    if path.suffix.lower() == ".epub":
        return EPUBHandler(path, converter)
    elif path.suffix.lower() == ".txt":
        return TXTHandler(path, converter)
    else:
        raise ValueError(f"Unsupported format: {path.suffix}")


class ChineseTextConverter:
    """Multi-format Chinese text converter."""

    def __init__(self, conversion_type: str = "s2t"):
        self.conversion_type = conversion_type
        self.converter = ChineseConverter(conversion_type)

    def convert_file(self, input_path: str, output_path: str, create_backup: bool = True) -> bool:
        """Convert a single file."""
        logger.info(f"Converting: {input_path} -> {output_path}")
        start_time = time.time()

        # Create backup
        if create_backup:
            backup_path = Path(input_path).with_suffix(
                Path(input_path).suffix + Config.BACKUP_SUFFIX
            )
            backup_path.write_bytes(Path(input_path).read_bytes())
            logger.info(f"Backup created: {backup_path}")

        try:
            handler = get_handler(input_path, self.converter)

            # Validate file first
            valid, errors = handler.validate_file(Path(input_path))
            if not valid:
                logger.error(f"Invalid file: {'; '.join(errors)}")
                return False

            # Process the file
            success = handler.process_file(Path(input_path), Path(output_path))

            if success:
                stats = handler.stats
                elapsed = time.time() - start_time
                logger.info(f"✓ Conversion completed in {elapsed:.2f}s")
                logger.info(
                    f"  Files: {stats['files_processed']}, "
                    f"Texts: {stats['texts_converted']}, "
                    f"Errors: {stats['errors']}"
                )
                return True
            else:
                logger.error("Conversion failed")
                return False

        except Exception as e:
            logger.error(f"Conversion failed: {e}")
            return False

    def convert_batch(self, input_dir: str, output_dir: str) -> dict:
        """Convert all supported files in a directory."""
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Find all supported files
        supported_files = []
        for pattern in ["*.epub", "*.txt"]:
            supported_files.extend(input_path.glob(pattern))

        logger.info(f"Found {len(supported_files)} supported files")

        results = {}
        for file_path in supported_files:
            output_file = output_path / file_path.name
            success = self.convert_file(str(file_path), str(output_file))
            results[str(file_path)] = success

        successful = sum(1 for success in results.values() if success)
        logger.info(f"Batch completed: {successful}/{len(results)} successful")
        return results


def _generate_default_output(input_path: str, is_batch: bool) -> str:
    """Generate default output path based on input."""
    input_path = Path(input_path)

    if is_batch or input_path.is_dir():
        # For directories: aaa/bbb -> aaa/bbb_trad
        return str(input_path.parent / f"{input_path.name}_trad")
    else:
        # For files: aaa/bbb/xxx.epub -> aaa/bbb/xxx_trad.epub
        stem = input_path.stem  # xxx
        suffix = input_path.suffix  # .epub
        parent = input_path.parent  # aaa/bbb
        return str(parent / f"{stem}_trad{suffix}")


def main():
    parser = argparse.ArgumentParser(description="Convert Chinese text in various file formats")
    parser.add_argument("input", help="Input file or directory (.epub, .txt)")
    parser.add_argument("output", nargs="?", help="Output file or directory (optional)")
    parser.add_argument(
        "--type",
        "-t",
        choices=list(EPUBConfig.CONVERSION_TYPES),
        default=EPUBConfig.DEFAULT_CONVERSION,
        help="Conversion type",
    )
    parser.add_argument("--batch", "-b", action="store_true", help="Batch mode")
    parser.add_argument("--no-backup", action="store_true", help="Skip backup")

    args = parser.parse_args()

    # Generate default output if not provided
    if not args.output:
        args.output = _generate_default_output(args.input, args.batch)
        logger.info(f"Auto-generated output path: {args.output}")

    converter = ChineseTextConverter(args.type)

    try:
        if args.batch:
            converter.convert_batch(args.input, args.output)
        else:
            success = converter.convert_file(args.input, args.output, not args.no_backup)
            if not success:
                sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        sys.exit(1)


if __name__ == "__main__":
    main()
