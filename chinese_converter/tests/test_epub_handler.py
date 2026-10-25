import zipfile
from pathlib import Path

from chinese_converter.cli import ChineseTextConverter

CONTAINER_XML = (
    '<?xml version="1.0"?><container version="1.0" '
    'xmlns="urn:oasis:names:tc:opendocument:xmlns:container"><rootfiles>'
    '<rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>'
    "</rootfiles></container>"
)
CONTENT_OPF = (
    '<?xml version="1.0" encoding="utf-8"?><package xmlns="http://www.idpf.org/2007/opf" '
    'version="3.0" unique-identifier="id"><metadata xmlns:dc="http://purl.org/dc/elements/1.1/">'
    "<dc:title>汉语标题</dc:title></metadata><manifest>"
    '<item id="ch1" href="ch1.xhtml" media-type="application/xhtml+xml"/></manifest>'
    '<spine><itemref idref="ch1"/></spine></package>'
)
CHAPTER = (
    '<?xml version="1.0" encoding="utf-8"?><html xmlns="http://www.w3.org/1999/xhtml">'
    "<head><title>章</title></head><body><p>简体中文内容</p></body></html>"
)


def _write_epub(path: Path) -> Path:
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("mimetype", "application/epub+zip", compress_type=zipfile.ZIP_STORED)
        archive.writestr("META-INF/container.xml", CONTAINER_XML)
        archive.writestr("OEBPS/content.opf", CONTENT_OPF)
        archive.writestr("OEBPS/ch1.xhtml", CHAPTER)
    return path


def test_epub_conversion_keeps_the_book_readable_and_converts_text(tmp_path: Path) -> None:
    """The EPUB is rebuilt from scratch, so its required layout must survive."""
    input_path = _write_epub(tmp_path / "book.epub")
    output_path = tmp_path / "out.epub"

    converter = ChineseTextConverter("s2t")

    assert converter.convert_file(str(input_path), str(output_path))

    with zipfile.ZipFile(output_path) as archive:
        assert archive.namelist()[0] == "mimetype"
        assert archive.getinfo("mimetype").compress_type == zipfile.ZIP_STORED
        assert set(archive.namelist()) == {
            "mimetype",
            "META-INF/container.xml",
            "OEBPS/content.opf",
            "OEBPS/ch1.xhtml",
        }
        assert "漢語標題" in archive.read("OEBPS/content.opf").decode("utf-8")
        assert "簡體中文內容" in archive.read("OEBPS/ch1.xhtml").decode("utf-8")
