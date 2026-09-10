"""Main entrypoint for the anime1_downloader module."""

import sys

from .cli import main

if __name__ == "__main__":
    sys.exit(main())
