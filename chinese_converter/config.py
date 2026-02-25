"""EPUB converter specific configuration."""

import os

from dotenv import load_dotenv

load_dotenv()


class EPUBConfig:
    """EPUB converter specific configuration."""

    # Conversion settings
    DEFAULT_CONVERSION = os.getenv("EPUB_DEFAULT_CONVERSION", "s2t")
    CREATE_BACKUP = os.getenv("EPUB_CREATE_BACKUP", "true").lower() == "true"
    CONVERSION_TYPES = ["s2t", "s2tw", "s2hk", "t2s"]

    # File processing
    TRANSLATABLE_EXTENSIONS = {
        ".opf",
        ".ncx",
        ".xhtml",
        ".html",
        ".htm",
        ".xml",
        ".css",
    }

    # EPUB structure constants
    MIMETYPE_FILE = "mimetype"
    META_INF_DIR = "META-INF"
    CONTAINER_XML = "META-INF/container.xml"
