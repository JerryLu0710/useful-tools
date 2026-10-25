import logging
import shutil
import subprocess
from argparse import Namespace
from pathlib import Path

import pytest

from ytmusic_dl.commands import verify as verify_module
from ytmusic_dl.commands.verify import extract_id_from_file, verify_command
from ytmusic_dl.config import YTMusicDLConfig


def test_verify_scans_every_format_a_download_can_produce(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """verify must see the containers --format writes, not only mp3/m4a/opus/webm."""
    history_path = tmp_path / "history.jsonl"
    history_path.write_text('{"id": "video-id", "title": "Song"}\n', encoding="utf-8")
    (tmp_path / "Song.flac").write_bytes(b"not really a flac file")

    with caplog.at_level(logging.INFO):
        verify_command(
            Namespace(
                backup_dir=tmp_path,
                history=history_path,
                scan_all=False,
                download_missing=False,
            )
        )

    assert "Could not find a YouTube ID in the metadata of 1 files" in caplog.text


def test_download_missing_songs_args_match_the_cli_defaults(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A hard-coded format ID hard-fails without Premium, so reuse the CLI default."""
    captured = {}
    monkeypatch.setattr(
        "ytmusic_dl.commands.download.download_command",
        lambda args: captured.update(vars(args)),
    )

    verify_module.download_missing_songs(["video-id"])

    assert captured["quality"] == YTMusicDLConfig.DEFAULT_QUALITY
    assert captured["prompt_on_duplicate"] is False


@pytest.mark.skipif(shutil.which("ffmpeg") is None, reason="ffmpeg is required")
def test_extract_id_from_file_scans_the_tags_an_opus_file_has(tmp_path: Path) -> None:
    """mutagen raises for keys a container lacks, which used to abort the whole scan."""
    audio = tmp_path / "Song.opus"
    subprocess.run(
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-f",
            "lavfi",
            "-i",
            "anullsrc=r=8000:cl=mono",
            "-t",
            "0.05",
            "-metadata",
            "artist=Thom Yorke",
            "-metadata",
            "comment=https://music.youtube.com/watch?v=dQw4w9WgXcQ",
            str(audio),
        ],
        check=True,
    )

    assert extract_id_from_file(audio, scan_all=True) == "dQw4w9WgXcQ"


def test_verify_returns_failure_for_a_missing_backup_dir(tmp_path: Path) -> None:
    """A command failure must come back as an exit code, not a swallowed None."""
    assert (
        verify_command(
            Namespace(
                backup_dir=tmp_path / "absent",
                history=tmp_path / "history.jsonl",
                scan_all=False,
                download_missing=False,
            )
        )
        == 1
    )
