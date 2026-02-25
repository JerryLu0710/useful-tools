"""Combined EPUB handling, processing, and validation."""

import shutil
import tempfile
import zipfile
from pathlib import Path

from bs4 import BeautifulSoup, NavigableString
from lxml import etree

from chinese_converter.formats.base_handler import BaseFormatHandler
from config import Config
from logger_setup import get_logger

from ..config import EPUBConfig

logger = get_logger(__name__, "chinese_converter")


class EPUBHandler(BaseFormatHandler):
    """Handles all EPUB operations: extraction, processing, validation, and creation."""

    def __init__(self, path: Path, converter):
        """Initialize with EPUB path and text converter."""
        super().__init__(path, converter)
        self.temp_dir = None

        if not self.path.exists():
            raise FileNotFoundError(f"EPUB not found: {path}")

    def process_file(self, input_path: Path, output_path: Path) -> bool:
        """Process EPUB file - implements BaseFormatHandler interface."""
        self.path = input_path

        if not self.path.exists():
            logger.error(f"EPUB not found: {input_path}")
            return False

        try:
            # Use existing process() method
            if self.process():
                # Use existing save_as() method
                return self.save_as(str(output_path))
            return False
        finally:
            self.cleanup()

    def validate_file(self, file_path: Path) -> tuple[bool, list]:
        """Validate EPUB file - implements BaseFormatHandler interface."""
        if file_path.suffix.lower() != ".epub":
            return False, ["Not an EPUB file"]

        self.path = file_path
        return self.validate()

    def validate(self) -> tuple[bool, list]:
        """Validate EPUB structure."""
        errors = []

        try:
            with zipfile.ZipFile(self.path, "r") as zf:
                files = zf.namelist()

                if "mimetype" not in files:
                    errors.append("Missing mimetype file")

                if "META-INF/container.xml" not in files:
                    errors.append("Missing container.xml")

                # Check mimetype content
                try:
                    mimetype = zf.read("mimetype").decode("utf-8").strip()
                    if mimetype != "application/epub+zip":
                        errors.append(f"Invalid mimetype: {mimetype}")
                except Exception:
                    errors.append("Could not read mimetype")

        except zipfile.BadZipFile:
            errors.append("Invalid ZIP file")
        except Exception as e:
            errors.append(f"Validation error: {e}")

        return len(errors) == 0, errors

    def process(self) -> bool:
        """Extract, process, and recreate EPUB."""
        try:
            # Validate first
            valid, errors = self.validate()
            if not valid:
                logger.error(f"Invalid EPUB: {'; '.join(errors)}")
                return False

            # Extract
            self._extract()

            # Process files
            self._process_files()

            return True

        except Exception as e:
            logger.error(f"Processing failed: {e}")
            return False

    def save_as(self, output_path: str) -> bool:
        """Save processed EPUB to new file."""
        if not self.temp_dir:
            logger.error("No processed content to save")
            return False

        try:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
                # Add mimetype first (uncompressed)
                mimetype_path = Path(self.temp_dir) / "mimetype"
                if mimetype_path.exists():
                    zf.write(mimetype_path, "mimetype", compress_type=zipfile.ZIP_STORED)

                # Add other files
                for file_path in Path(self.temp_dir).rglob("*"):
                    if file_path.is_file() and file_path.name != "mimetype":
                        archive_name = file_path.relative_to(self.temp_dir).as_posix()
                        zf.write(file_path, archive_name)

            logger.info(f"Saved EPUB: {output_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to save EPUB: {e}")
            return False

    def _extract(self):
        """Extract EPUB to temp directory."""
        self.temp_dir = tempfile.mkdtemp(prefix=Config.TEMP_DIR_PREFIX, dir=Config.TEMP_DIRECTORY)

        with zipfile.ZipFile(self.path, "r") as zf:
            zf.extractall(self.temp_dir)

        logger.info(f"Extracted to: {self.temp_dir}")

    def _process_files(self):
        """Process all translatable files."""
        for file_path in Path(self.temp_dir).rglob("*"):
            if (
                file_path.is_file()
                and file_path.suffix.lower() in EPUBConfig.TRANSLATABLE_EXTENSIONS
            ):
                self._process_file(file_path)

    def _process_file(self, file_path: Path):
        """Process a single file based on its type."""
        try:
            extension = file_path.suffix.lower()
            name = file_path.name.lower()

            if extension == ".opf" or "content.opf" in name:
                self._process_opf(file_path)
            elif extension == ".ncx":
                self._process_ncx(file_path)
            elif extension in {".xhtml", ".html", ".htm"}:
                self._process_html(file_path)
            elif extension in {".xml", ".css"}:
                self._process_text_file(file_path)

            self.stats["files_processed"] += 1

        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
            self.stats["errors"] += 1

    def _process_opf(self, file_path: Path):
        """Process OPF metadata file."""
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        root = etree.fromstring(content.encode("utf-8"))

        # Process metadata
        namespaces = {"dc": "http://purl.org/dc/elements/1.1/"}
        for xpath in [
            ".//dc:title",
            ".//dc:creator",
            ".//dc:description",
            ".//dc:subject",
        ]:
            for elem in root.xpath(xpath, namespaces=namespaces):
                if elem.text:
                    converted = self.converter.convert(elem.text)
                    if converted != elem.text:
                        elem.text = converted
                        self.stats["texts_converted"] += 1

        with open(file_path, "wb") as f:
            f.write(etree.tostring(root, encoding="utf-8", xml_declaration=True))

    def _process_ncx(self, file_path: Path):
        """Process NCX navigation file."""
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        root = etree.fromstring(content.encode("utf-8"))

        for elem in root.xpath(".//*[local-name()='text']"):
            if elem.text:
                converted = self.converter.convert(elem.text)
                if converted != elem.text:
                    elem.text = converted
                    self.stats["texts_converted"] += 1

        with open(file_path, "wb") as f:
            f.write(etree.tostring(root, encoding="utf-8", xml_declaration=True))

    def _process_html(self, file_path: Path):
        """Process HTML content files."""
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        soup = BeautifulSoup(content, "html.parser")

        # Process text nodes
        for text_node in soup.find_all(string=True):
            if isinstance(text_node, NavigableString) and text_node.strip():
                converted = self.converter.convert(str(text_node))
                if converted != str(text_node):
                    text_node.replace_with(converted)
                    self.stats["texts_converted"] += 1

        # Process attributes
        for tag in soup.find_all(attrs={"title": True}):
            converted = self.converter.convert(tag["title"])
            if converted != tag["title"]:
                tag["title"] = converted
                self.stats["texts_converted"] += 1

        for tag in soup.find_all(attrs={"alt": True}):
            converted = self.converter.convert(tag["alt"])
            if converted != tag["alt"]:
                tag["alt"] = converted
                self.stats["texts_converted"] += 1

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(str(soup))

    def _process_text_file(self, file_path: Path):
        """Process generic text files (CSS, XML)."""
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        # Simple text conversion (works for CSS comments and XML text)
        converted_content = self.converter.convert(content)
        if converted_content != content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(converted_content)
            self.stats["texts_converted"] += 1

    def cleanup(self):
        """Clean up temp directory."""
        if self.temp_dir and Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)
            self.temp_dir = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()
