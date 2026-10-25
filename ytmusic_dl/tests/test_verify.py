import pytest

from ytmusic_dl.commands import verify as verify_module
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
