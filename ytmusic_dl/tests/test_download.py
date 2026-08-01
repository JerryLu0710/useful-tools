from argparse import Namespace
from pathlib import Path

import pytest

from ytmusic_dl import cli
from ytmusic_dl.commands import download as download_module
from ytmusic_dl.commands.download import (
    build_duplicate_output_template,
    confirm_duplicate_download,
    find_existing_audio_files,
)


def test_download_prompt_on_duplicate_defaults_to_enabled(monkeypatch: pytest.MonkeyPatch) -> None:
    captured_args = {}
    monkeypatch.setattr("sys.argv", ["ytmusic_dl", "download", "https://example.com/video"])
    monkeypatch.setattr(cli, "download_command", lambda args: captured_args.update(vars(args)))

    cli.main()

    assert captured_args["prompt_on_duplicate"] is True


def test_download_no_prompt_on_duplicate_disables_prompt(monkeypatch: pytest.MonkeyPatch) -> None:
    captured_args = {}
    monkeypatch.setattr(
        "sys.argv",
        ["ytmusic_dl", "download", "https://example.com/video", "--no-prompt-on-duplicate"],
    )
    monkeypatch.setattr(cli, "download_command", lambda args: captured_args.update(vars(args)))

    cli.main()

    assert captured_args["prompt_on_duplicate"] is False


def test_find_existing_audio_files_escapes_title_and_ignores_sidecars(tmp_path: Path) -> None:
    title = "Song [Live]"
    matching_audio = tmp_path / "Song [Live].mp3"
    matching_sidecar = tmp_path / "Song [Live].info.json"
    glob_lookalike = tmp_path / "Song L.mp3"
    matching_audio.touch()
    matching_sidecar.touch()
    glob_lookalike.touch()

    assert find_existing_audio_files(tmp_path, title) == [matching_audio]


def test_duplicate_output_template_appends_video_id_after_artist_collision(tmp_path: Path) -> None:
    (tmp_path / "Song - Artist.mp3").touch()

    template = build_duplicate_output_template(tmp_path, "Song", "Artist", "video-id")

    assert template == str(tmp_path / "%(title)s - Artist [video-id].%(ext)s")


@pytest.mark.parametrize("response", ["y", "YES"])
def test_confirm_duplicate_download_accepts_yes(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, response: str
) -> None:
    monkeypatch.setattr("builtins.input", lambda _prompt: response)

    assert confirm_duplicate_download("Song", [tmp_path / "Song.mp3"])


@pytest.mark.parametrize("response", ["", "n", "anything else"])
def test_confirm_duplicate_download_declines_nonaffirmative_responses(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, response: str
) -> None:
    monkeypatch.setattr("builtins.input", lambda _prompt: response)

    assert not confirm_duplicate_download("Song", [tmp_path / "Song.mp3"])


def test_confirm_duplicate_download_declines_when_standard_input_is_unavailable(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    def raise_eof(_prompt: str) -> str:
        raise EOFError

    monkeypatch.setattr("builtins.input", raise_eof)

    assert not confirm_duplicate_download("Song", [tmp_path / "Song.mp3"])


def test_confirm_duplicate_download_declines_when_standard_input_errors(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    def raise_os_error(_prompt: str) -> str:
        raise OSError("standard input unavailable")

    monkeypatch.setattr("builtins.input", raise_os_error)

    assert not confirm_duplicate_download("Song", [tmp_path / "Song.mp3"])


def test_download_command_skips_declined_duplicate_without_writing_history(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    class FakeYoutubeDL:
        instances = []

        def __init__(self, options: dict) -> None:
            self.params = options
            self.extract_calls = []
            self.instances.append(self)

        def __enter__(self):
            return self

        def __exit__(self, *_args) -> None:
            return None

        def extract_info(self, *_args, **_kwargs):
            self.extract_calls.append((_args, _kwargs))
            return None

    output_path = tmp_path / "music"
    output_path.mkdir()
    (output_path / "Song.mp3").touch()
    history_path = tmp_path / "history.jsonl"
    args = Namespace(
        urls=["https://example.com/video"],
        output=output_path,
        history=history_path,
        audio_format="best",
        quality="bestaudio",
        no_thumbnail=True,
        no_metadata=True,
        force=False,
        dry_run=False,
        browser=None,
        cookies=None,
        prompt_on_duplicate=True,
    )
    video = {"id": "video-id", "title": "Song", "artist": "Artist"}
    monkeypatch.setattr(download_module, "get_video_info", lambda *_args: ([video], False))
    monkeypatch.setattr(download_module, "confirm_duplicate_download", lambda *_args: False)
    monkeypatch.setattr(download_module.yt_dlp, "YoutubeDL", FakeYoutubeDL)

    download_module.download_command(args)

    assert not history_path.exists()
    assert all(not instance.extract_calls for instance in FakeYoutubeDL.instances)


def test_download_command_dry_run_does_not_prompt_for_duplicate(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    class FakeYoutubeDL:
        def __init__(self, options: dict) -> None:
            self.params = options

        def __enter__(self):
            return self

        def __exit__(self, *_args) -> None:
            return None

    output_path = tmp_path / "music"
    output_path.mkdir()
    (output_path / "Song.mp3").touch()
    args = Namespace(
        urls=["https://example.com/video"],
        output=output_path,
        history=tmp_path / "history.jsonl",
        audio_format="best",
        quality="bestaudio",
        no_thumbnail=True,
        no_metadata=True,
        force=False,
        dry_run=True,
        browser=None,
        cookies=None,
        prompt_on_duplicate=True,
    )
    video = {"id": "video-id", "title": "Song", "artist": "Artist"}
    monkeypatch.setattr(download_module, "get_video_info", lambda *_args: ([video], False))
    monkeypatch.setattr(download_module.yt_dlp, "YoutubeDL", FakeYoutubeDL)
    monkeypatch.setattr(
        download_module,
        "confirm_duplicate_download",
        lambda *_args: pytest.fail("Dry runs must not prompt for duplicates"),
    )

    download_module.download_command(args)
