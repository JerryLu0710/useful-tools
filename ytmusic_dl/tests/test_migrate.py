import json
from pathlib import Path

from ytmusic_dl.commands.migrate import _read_ids_from_jsonl


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
