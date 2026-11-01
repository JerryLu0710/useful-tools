import json
from argparse import Namespace
from pathlib import Path

import pytest

from ytmusic_dl import cli
from ytmusic_dl.commands.prune_history import prune_history_command
from ytmusic_dl.commands.rename import rename_command


def _entry(video_id: str, file_path: str) -> dict:
    return {"id": video_id, "title": "Song", "artist": "The Beatles", "file_path": file_path}


def _history(tmp_path: Path, entries: list[dict]) -> Path:
    path = tmp_path / "history.jsonl"
    path.write_text(
        "\n".join(json.dumps(entry) for entry in entries) + "\n",
        encoding="utf-8",
    )
    return path


def _args(history: Path, dry_run: bool = False) -> Namespace:
    return Namespace(history=history, dry_run=dry_run)


def _lines(history: Path) -> list[dict]:
    return [json.loads(line) for line in history.read_text(encoding="utf-8").splitlines()]


def test_prune_keeps_the_current_line_of_a_renamed_track(tmp_path: Path) -> None:
    history = _history(
        tmp_path,
        [
            _entry("id-1", "/music/Song.m4a"),
            _entry("id-2", "/music/Other.m4a"),
            _entry("id-1", "/music/Song - The Beatles.m4a"),
        ],
    )

    assert prune_history_command(_args(history)) == 0

    # The kept line is the newest one for the ID, and IDs stay in download order.
    assert _lines(history) == [
        _entry("id-1", "/music/Song - The Beatles.m4a"),
        _entry("id-2", "/music/Other.m4a"),
    ]


def test_prune_leaves_a_one_line_per_id_history_untouched(tmp_path: Path) -> None:
    history = _history(tmp_path, [_entry("id-1", "/a.m4a"), _entry("id-2", "/b.m4a")])
    before = history.read_text(encoding="utf-8")

    assert prune_history_command(_args(history)) == 0

    assert history.read_text(encoding="utf-8") == before


def test_prune_dry_run_writes_nothing(tmp_path: Path) -> None:
    history = _history(
        tmp_path,
        [_entry("id-1", "/music/Song.m4a"), _entry("id-1", "/music/Song - The Beatles.m4a")],
    )
    before = history.read_text(encoding="utf-8")

    assert prune_history_command(_args(history, dry_run=True)) == 0

    assert history.read_text(encoding="utf-8") == before
    assert not (tmp_path / "history.jsonl.pruning").exists()


def test_prune_refuses_a_history_file_it_cannot_fully_read(tmp_path: Path) -> None:
    """A dropped line would be lost for good, so a damaged file is left alone."""
    history = tmp_path / "history.jsonl"
    history.write_text(
        json.dumps(_entry("id-1", "/a.m4a")) + "\n" + "{ this line is not json\n",
        encoding="utf-8",
    )
    before = history.read_text(encoding="utf-8")

    assert prune_history_command(_args(history)) == 1

    assert history.read_text(encoding="utf-8") == before
    assert not (tmp_path / "history.jsonl.pruning").exists()


def test_prune_fails_when_the_history_file_is_missing(tmp_path: Path) -> None:
    assert prune_history_command(_args(tmp_path / "history.jsonl")) == 1


def test_prune_history_after_normalize_names_leaves_one_line_per_file(tmp_path: Path) -> None:
    """End to end: a rename appends a line, pruning collapses it back onto the file."""
    music = tmp_path / "music"
    music.mkdir()
    (music / "Song.m4a").touch()
    (music / "Song - Others.m4a").touch()
    history = _history(
        tmp_path,
        [
            _entry("id-1", str(music / "Song.m4a")),
            _entry("id-2", str(music / "Song - Others.m4a")),
        ],
    )
    rename_command(Namespace(output=music, history=history, dry_run=False))
    assert len(_lines(history)) == 3

    assert prune_history_command(_args(history)) == 0

    assert {Path(entry["file_path"]) for entry in _lines(history)} == {
        music / "Song - The Beatles.m4a",
        music / "Song - Others.m4a",
    }


def test_prune_history_defaults_to_applying_unless_dry_run_is_given(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured = {}
    monkeypatch.setattr("sys.argv", ["ytmusic_dl", "prune-history"])
    monkeypatch.setattr(cli, "prune_history_command", lambda args: captured.update(vars(args)))

    cli.main()

    assert captured["dry_run"] is False
