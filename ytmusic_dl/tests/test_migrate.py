import json
from argparse import Namespace
from pathlib import Path

import pytest

from ytmusic_dl.commands.migrate import _read_ids_from_jsonl, migrate_command


def test_read_ids_from_jsonl_keeps_one_id_per_song(tmp_path: Path) -> None:
    """A rename appends a second history line for the same video ID."""
    history_path = tmp_path / "history.jsonl"
    history_path.write_text(
        "\n".join(
            json.dumps(entry)
            for entry in (
                {"id": "a", "file_path": "Song.mp3"},
                {"id": "a", "file_path": "Song - Artist.mp3"},
                {"id": "b"},
            )
        )
        + "\n"
    )

    assert _read_ids_from_jsonl(history_path) == ["a", "b"]


def test_migrate_command_passes_its_own_options_through(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """migrate never prompts, so it renames shared titles without waiting for input."""
    id_file = tmp_path / "ids.jsonl"
    id_file.write_text(json.dumps({"id": "video-id"}) + "\n")
    args = Namespace(
        file_path=id_file,
        output=tmp_path / "music",
        history=tmp_path / "history.jsonl",
        audio_format="best",
        quality="bestaudio",
        no_thumbnail=True,
        no_metadata=True,
        force=False,
        dry_run=False,
        browser=None,
        cookies=None,
    )
    captured = {}
    monkeypatch.setattr(
        "ytmusic_dl.commands.download.download_command",
        lambda download_args: captured.update(vars(download_args)),
    )

    migrate_command(args)

    assert captured["quality"] == "bestaudio"
    assert captured["output"] == args.output
    assert captured["prompt_on_duplicate"] is False


def test_migrate_returns_failure_for_a_missing_id_file(tmp_path: Path) -> None:
    assert migrate_command(Namespace(file_path=tmp_path / "absent.jsonl")) == 1
