from abc import ABC, abstractmethod
from pathlib import Path


class BaseFormatHandler(ABC):
    """Abstract base class for format handlers."""

    def __init__(self, path: Path, converter):
        self.path = path
        self.converter = converter
        self.stats = {"files_processed": 0, "texts_converted": 0, "errors": 0}

    @abstractmethod
    def process_file(self, input_path: Path, output_path: Path) -> bool:
        """Process a single file."""
        pass

    @abstractmethod
    def validate_file(self, file_path: Path) -> tuple[bool, list]:
        """Validate file format."""
        pass
