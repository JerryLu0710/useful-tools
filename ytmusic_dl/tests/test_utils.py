import json
from pathlib import Path

from ytmusic_dl.common.utils import load_history_entries


def test_load_history_entries_keeps_entries_after_a_damaged_line(tmp_path: Path) -> None:
    """One half-written line must not hide the songs recorded after it."""
    history_path = tmp_path / "history.jsonl"
    history_path.write_text(
        json.dumps({"id": "a", "title": "First"})
        + "\n"
        + "cut off mid writ\n"
        + json.dumps({"id": "b", "title": "Second"})
        + "\n"
    )

    assert [entry["id"] for entry in load_history_entries(history_path)] == ["a", "b"]


def test_load_history_entries_skips_entries_without_an_id(tmp_path: Path) -> None:
    history_path = tmp_path / "history.jsonl"
    history_path.write_text(json.dumps({"title": "No id"}) + "\n")

    assert load_history_entries(history_path) == []


def test_load_history_entries_returns_nothing_for_a_missing_file(tmp_path: Path) -> None:
    assert load_history_entries(tmp_path / "absent.jsonl") == []
