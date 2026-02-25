"""Combined TXT handling, processing, and validation."""

from pathlib import Path

from chinese_converter.formats.base_handler import BaseFormatHandler
from logger_setup import get_logger

logger = get_logger(__name__, "chinese_converter")


class TXTHandler(BaseFormatHandler):
    """Handles TXT file processing."""

    def __init__(self, path, converter):
        super().__init__(path, converter)

    def process_file(self, input_path: Path, output_path: Path) -> bool:
        """Process TXT file with Chinese conversion."""
        try:
            with open(input_path, encoding="utf-8") as f:
                content = f.read()

            converted_content = self.converter.convert(content)

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(converted_content)

            if converted_content != content:
                self.stats["texts_converted"] += 1

            self.stats["files_processed"] += 1
            return True

        except Exception as e:
            logger.error(f"Error processing {input_path}: {e}")
            self.stats["errors"] += 1
            return False

    def validate_file(self, file_path: Path) -> tuple[bool, list]:
        """Validate TXT file."""
        if file_path.suffix.lower() != ".txt":
            return False, ["Not a TXT file"]
        return True, []
