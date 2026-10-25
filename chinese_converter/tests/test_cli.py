from pathlib import Path

import pytest

from chinese_converter.cli import ChineseTextConverter, _generate_default_output, get_handler, main
from chinese_converter.formats.txt_handler import TXTHandler


def test_convert_file_converts_text_and_creates_backup(tmp_path: Path) -> None:
    input_path = tmp_path / "source.txt"
    output_path = tmp_path / "converted.txt"
    input_path.write_text("汉语", encoding="utf-8")

    converter = ChineseTextConverter("s2t")

    assert converter.convert_file(str(input_path), str(output_path))
    assert output_path.read_text(encoding="utf-8") == "漢語"
    assert input_path.with_suffix(".txt.backup").read_text(encoding="utf-8") == "汉语"


def test_get_handler_rejects_unsupported_format() -> None:
    converter = ChineseTextConverter("s2t")

    with pytest.raises(ValueError, match="Unsupported format"):
        get_handler("source.md", converter.converter)


def test_get_handler_returns_txt_handler() -> None:
    converter = ChineseTextConverter("s2t")

    assert isinstance(get_handler("source.txt", converter.converter), TXTHandler)


def test_generate_default_output_for_file_and_directory(tmp_path: Path) -> None:
    file_path = tmp_path / "source.txt"
    directory_path = tmp_path / "source"

    assert _generate_default_output(str(file_path), False) == str(tmp_path / "source_trad.txt")
    assert _generate_default_output(str(directory_path), True) == str(tmp_path / "source_trad")


def test_main_returns_success_for_a_valid_text_conversion(tmp_path: Path) -> None:
    input_path = tmp_path / "source.txt"
    output_path = tmp_path / "converted.txt"
    input_path.write_text("汉语", encoding="utf-8")

    assert main([str(input_path), str(output_path), "--no-backup"]) == 0
    assert output_path.read_text(encoding="utf-8") == "漢語"
    assert not list(tmp_path.glob("*.backup"))


def test_main_batch_honours_no_backup(tmp_path: Path) -> None:
    """--no-backup used to be dropped in batch mode, copying every converted file."""
    input_dir = tmp_path / "books"
    input_dir.mkdir()
    (input_dir / "source.txt").write_text("汉语", encoding="utf-8")

    assert main([str(input_dir), str(tmp_path / "out"), "--batch", "--no-backup"]) == 0
    assert not list(input_dir.glob("*.backup"))


def test_convert_file_leaves_no_backup_for_an_input_it_cannot_convert(
    tmp_path: Path,
) -> None:
    input_path = tmp_path / "notes.pdf"
    input_path.write_bytes(b"%PDF-1.4")

    converter = ChineseTextConverter("s2t")

    assert not converter.convert_file(str(input_path), str(tmp_path / "notes_out.pdf"))
    assert not list(tmp_path.glob("*.backup"))


def test_convert_file_fails_when_the_converter_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Swallowing the error wrote an unconverted file and reported success."""
    input_path = tmp_path / "source.txt"
    input_path.write_text("汉语", encoding="utf-8")

    converter = ChineseTextConverter("s2t")

    def boom(text: str) -> str:
        raise RuntimeError("converter unavailable")

    monkeypatch.setattr(converter.converter, "convert", boom)

    assert not converter.convert_file(str(input_path), str(tmp_path / "converted.txt"))
