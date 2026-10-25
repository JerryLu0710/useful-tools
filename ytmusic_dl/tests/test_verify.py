import shutil
import subprocess
from pathlib import Path

import pytest

from ytmusic_dl.commands import verify as verify_module
from ytmusic_dl.commands.verify import extract_id_from_file
from ytmusic_dl.config import YTMusicDLConfig


def test_download_missing_songs_uses_the_cli_quality_default(
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
