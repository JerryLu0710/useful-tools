"""
Centralized logging setup for all utility scripts.
Provides consistent logging configuration across the project.
"""

import logging
import sys
from logging.handlers import RotatingFileHandler

from config import Config


class LoggerSetup:
    """Centralized logger setup class."""

    _loggers: dict[str, logging.Logger] = {}

    @classmethod
    def get_logger(cls, name: str, script_name: str | None = None) -> logging.Logger:
        """
        Get or create a logger with consistent configuration.

        Args:
            name: Logger name (usually __name__)
            script_name: Script name for log file (if None, extracted from name)

        Returns:
            Configured logger instance
        """
        # Use existing logger if already created
        if name in cls._loggers:
            return cls._loggers[name]

        # Extract script name if not provided
        if script_name is None:
            script_name = name.split(".")[-1] if "." in name else name

        logger = logging.getLogger(name)
        logger.setLevel(Config.LOG_LEVEL)

        # Prevent duplicate handlers
        if logger.handlers:
            return logger

        # Create formatters
        console_formatter = logging.Formatter(
            Config.LOG_FORMAT_CONSOLE, datefmt=Config.LOG_DATE_FORMAT
        )

        file_formatter = logging.Formatter(Config.LOG_FORMAT_FILE, datefmt=Config.LOG_DATE_FORMAT)

        # Console handler
        if Config.LOG_TO_CONSOLE:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(Config.LOG_LEVEL)
            console_handler.setFormatter(console_formatter)
            logger.addHandler(console_handler)

        # File handler
        if Config.LOG_TO_FILE:
            log_file_path = Config.get_log_file_path(script_name)
            file_handler = RotatingFileHandler(
                log_file_path,
                maxBytes=Config.LOG_MAX_FILE_SIZE,
                backupCount=Config.LOG_BACKUP_COUNT,
                encoding=Config.DEFAULT_ENCODING,
            )
            file_handler.setLevel(logging.DEBUG)  # File gets all messages
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)

        # Store logger reference
        cls._loggers[name] = logger

        return logger

    @classmethod
    def configure_root_logger(cls):
        """Configure the root logger with project settings."""
        root_logger = logging.getLogger()
        root_logger.setLevel(Config.LOG_LEVEL)

        # Remove existing handlers
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        # Add our handlers
        if not root_logger.handlers:
            cls.get_logger("root", "application")


# Convenience function for easy import
def get_logger(name: str, script_name: str | None = None) -> logging.Logger:
    """
    Convenience function to get a logger.

    Args:
        name: Logger name (usually __name__)
        script_name: Script name for log file

    Returns:
        Configured logger instance
    """
    return LoggerSetup.get_logger(name, script_name)
