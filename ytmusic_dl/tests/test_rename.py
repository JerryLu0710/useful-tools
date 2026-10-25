import json
from argparse import Namespace
from pathlib import Path

import pytest

from ytmusic_dl import cli
from ytmusic_dl.commands.rename import rename_command


def _entry(video_id: str, title: str, artist: str, file_path: Path) -> dict:
    return {"id": video_id, "title": title, "artist": artist, "file_path": str(file_path)}


def _args(tmp_path: Path, dry_run: bool = False) -> Namespace:
    return Namespace(output=tmp_path / "music", history=tmp_path / "history.jsonl", dry_run=dry_run)


def _mixed_library(tmp_path: Path) -> Path:
    """One folder holding the same title as 'Song.m4a' and 'Song - Others.m4a'."""
    music = tmp_path / "music"
    music.mkdir()
    (music / "Song.m4a").touch()
    (music / "Song - Others.m4a").touch()
    history = tmp_path / "history.jsonl"
    history.write_text(
        "\n".join(
            json.dumps(entry)
            for entry in (
                _entry("id-1", "Song", "The Beatles", music / "Song.m4a"),
                _entry("id-2", "Song", "Others", music / "Song - Others.m4a"),
            )
        )
        + "\n"
    )
    return music


def test_normalize_names_renames_the_title_only_file(tmp_path: Path) -> None:
    music = _mixed_library(tmp_path)

    rename_command(_args(tmp_path))

    assert not (music / "Song.m4a").exists()
    assert (music / "Song - The Beatles.m4a").exists()
    assert (music / "Song - Others.m4a").exists()

    recorded = [json.loads(line) for line in (tmp_path / "history.jsonl").read_text().splitlines()]
    assert len(recorded) == 3
    assert recorded[-1]["id"] == "id-1"
    assert recorded[-1]["file_path"] == str(music / "Song - The Beatles.m4a")


def test_normalize_names_renames_nothing_on_a_second_run(tmp_path: Path) -> None:
    music = _mixed_library(tmp_path)
    args = _args(tmp_path)

    rename_command(args)
    rename_command(args)

    assert sorted(path.name for path in music.iterdir()) == [
        "Song - Others.m4a",
        "Song - The Beatles.m4a",
    ]
    assert len((tmp_path / "history.jsonl").read_text().splitlines()) == 3


def test_normalize_names_dry_run_renames_nothing(tmp_path: Path) -> None:
    music = _mixed_library(tmp_path)

    rename_command(_args(tmp_path, dry_run=True))

    assert (music / "Song.m4a").exists()
    assert not (music / "Song - The Beatles.m4a").exists()
    assert len((tmp_path / "history.jsonl").read_text().splitlines()) == 2


def test_normalize_names_leaves_files_missing_from_history_alone(tmp_path: Path) -> None:
    music = _mixed_library(tmp_path)
    history = tmp_path / "history.jsonl"
    history.write_text(
        json.dumps(_entry("id-2", "Song", "Others", music / "Song - Others.m4a")) + "\n"
    )

    rename_command(_args(tmp_path))

    assert (music / "Song.m4a").exists()
    assert not (music / "Song - The Beatles.m4a").exists()
    assert len(history.read_text().splitlines()) == 1


def test_normalize_names_fails_when_the_history_file_is_missing(tmp_path: Path) -> None:
    (tmp_path / "music").mkdir()

    assert rename_command(_args(tmp_path)) == 1


def test_main_returns_the_exit_code_of_its_command(monkeypatch: pytest.MonkeyPatch) -> None:
    """A command that returns 1 must reach the shell, not be swallowed by main."""
    monkeypatch.setattr("sys.argv", ["ytmusic_dl", "normalize-names"])
    monkeypatch.setattr(cli, "rename_command", lambda args: 1)

    assert cli.main() == 1


def test_normalize_names_applies_unless_dry_run_is_given(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    captured = {}
    monkeypatch.setattr("sys.argv", ["ytmusic_dl", "normalize-names"])
    monkeypatch.setattr(cli, "rename_command", lambda args: captured.update(vars(args)))

    cli.main()

    assert captured["dry_run"] is False
