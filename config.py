"""
Shared configuration for all utility scripts.
Loads settings from .env file and provides centralized configuration.
"""

import logging
import os
from enum import Enum
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


class LogLevel(Enum):
    """Logging levels."""

    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


class Config:
    """Centralized configuration class."""

    # Project paths
    PROJECT_ROOT = Path(__file__).parent
    LOG_DIRECTORY = PROJECT_ROOT / os.getenv("LOG_DIRECTORY", "logs")
    TEMP_DIRECTORY = PROJECT_ROOT / os.getenv("TEMP_DIRECTORY", "temp")

    # Logging configuration
    LOG_LEVEL = getattr(LogLevel, os.getenv("LOG_LEVEL", "INFO").upper()).value
    LOG_TO_FILE = os.getenv("LOG_TO_FILE", "true").lower() == "true"
    LOG_TO_CONSOLE = os.getenv("LOG_TO_CONSOLE", "true").lower() == "true"
    LOG_MAX_FILE_SIZE = int(os.getenv("LOG_MAX_FILE_SIZE", 10485760))  # 10MB
    LOG_BACKUP_COUNT = int(os.getenv("LOG_BACKUP_COUNT", 5))
    LOG_FORMAT_CONSOLE = os.getenv(
        "LOG_FORMAT_CONSOLE",
        "[%(asctime)s.%(msecs)03d] [%(levelname)s] [%(name)s] %(message)s",
    )
    LOG_FORMAT_FILE = os.getenv(
        "LOG_FORMAT_FILE",
        "[%(asctime)s.%(msecs)03d] [%(levelname)s] [%(name)s:%(lineno)d] [%(funcName)s] %(message)s",
    )
    LOG_DATE_FORMAT = os.getenv("LOG_DATE_FORMAT", "%Y-%m-%d %H:%M:%S")

    # File operations
    DEFAULT_ENCODING = os.getenv("DEFAULT_ENCODING", "utf-8")
    TEMP_DIR_PREFIX = os.getenv("TEMP_DIR_PREFIX", "utility_temp_")
    BACKUP_SUFFIX = os.getenv("BACKUP_SUFFIX", ".backup")

    # Performance settings
    MAX_WORKERS = int(os.getenv("MAX_WORKERS", 4))
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 8192))

    @classmethod
    def ensure_directories(cls):
        """Create necessary directories if they don't exist."""
        cls.LOG_DIRECTORY.mkdir(exist_ok=True)
        cls.TEMP_DIRECTORY.mkdir(exist_ok=True)

    @classmethod
    def get_log_file_path(cls, script_name: str) -> Path:
        """
        Get log file path for a specific script.
        Args:
            script_name: Name of the script (without .py extension)
        Returns:
            Path to log file
        """
        cls.ensure_directories()
        return cls.LOG_DIRECTORY / f"{script_name}.log"
