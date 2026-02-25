"""Simple OpenCC Chinese text converter."""

import re

import opencc

from logger_setup import get_logger

logger = get_logger(__name__, "chinese_converter")


class ChineseConverter:
    """Simple Chinese text converter using OpenCC."""

    def __init__(self, conversion_type: str = "s2t"):
        """
        Initialize converter.

        Args:
            conversion_type: Conversion type ('s2t', 's2tw', 's2hk', 't2s')
        """
        self.conversion_type = conversion_type

        try:
            self.converter = opencc.OpenCC(self.conversion_type)
            logger.info(f"Initialized converter: {conversion_type}")
        except Exception as e:
            logger.error(f"Failed to initialize converter: {e}")
            raise

    def convert(self, text: str) -> str:
        """Convert Chinese text if it contains Chinese characters."""
        if not text or not self._has_chinese(text):
            return text

        try:
            return self.converter.convert(text)
        except Exception as e:
            logger.error(f"Conversion error: {e}")
            return text

    def _has_chinese(self, text: str) -> bool:
        """Check if text contains Chinese characters."""
        return bool(re.search(r"[\u4e00-\u9fff]+", text))
