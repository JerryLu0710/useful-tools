import json
import shutil
import subprocess
from argparse import Namespace
from pathlib import Path

import pytest
import yt_dlp

from ytmusic_dl import cli
from ytmusic_dl.commands import download as download_module
from ytmusic_dl.commands.download import (
    build_duplicate_output_template,
    confirm_duplicate_download,
    find_existing_audio_files,
    find_same_title_files,
    rename_title_only_files,
    render_filename_stem,
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

    assert template == str(tmp_path / "%(title)s - %(artist,channel,uploader)s [video-id].%(ext)s")


def test_duplicate_output_template_uses_artist_field_without_collision(tmp_path: Path) -> None:
    template = build_duplicate_output_template(tmp_path, "Song", "Artist", "video-id")

    assert template == str(tmp_path / "%(title)s - %(artist,channel,uploader)s.%(ext)s")


@pytest.mark.parametrize(
    "title", ["Song [Live]", "Rock/Roll", "Don't: Cry Now", "..trailing dots.."]
)
def test_render_filename_stem_matches_the_name_yt_dlp_writes(title: str) -> None:
    """Disk lookups must compare against the sanitised name, not the raw title."""
    with yt_dlp.YoutubeDL(
        {"outtmpl": {"default": "%(title)s.%(ext)s"}, "quiet": True, "skip_download": True}
    ) as ydl:
        written = Path(ydl.prepare_filename({"id": "a", "title": title, "ext": "m4a"})).stem

    assert render_filename_stem(title) == written
    assert render_filename_stem(title, "AC/DC") == f"{written} - AC⧸DC"


def test_find_same_title_files_finds_bare_and_artist_suffixed_names(tmp_path: Path) -> None:
    bare = tmp_path / "Rock⧸Roll.mp3"
    suffixed = tmp_path / "Rock⧸Roll - The Beatles.m4a"
    bare.touch()
    suffixed.touch()
    (tmp_path / "Rock⧸Roll.info.json").touch()
    (tmp_path / "Rock Roll.mp3").touch()

    assert find_same_title_files(tmp_path, "Rock/Roll") == [bare, suffixed]


def _history_entry(id_: str, title: str, artist: str, file_path: Path) -> dict:
    return {"id": id_, "title": title, "artist": artist, "file_path": str(file_path)}


def test_rename_title_only_files_renames_sidecars_and_records_the_move(tmp_path: Path) -> None:
    audio = tmp_path / "Song [Live].mp3"
    sidecar = tmp_path / "Song [Live].info.json"
    audio.touch()
    sidecar.touch()
    history_path = tmp_path / "history.jsonl"
    entry = _history_entry("old-id", "Song [Live]", "The Beatles", audio)
    history_path.write_text(json.dumps(entry) + "\n")

    rename_title_only_files(tmp_path, "Song [Live]", {str(audio): entry}, history_path)

    assert not audio.exists()
    assert (tmp_path / "Song [Live] - The Beatles.mp3").exists()
    assert (tmp_path / "Song [Live] - The Beatles.info.json").exists()
    recorded = [json.loads(line) for line in history_path.read_text().splitlines()]
    assert len(recorded) == 2
    assert recorded[0] == entry
    assert recorded[-1]["id"] == "old-id"
    assert recorded[-1]["file_path"] == str(tmp_path / "Song [Live] - The Beatles.mp3")


@pytest.mark.skipif(shutil.which("ffmpeg") is None, reason="ffmpeg is required")
@pytest.mark.parametrize(
    "suffix,artist", [(".mp3", "Daft Punk"), (".m4a", "AC/DC"), (".opus", "Thom Yorke")]
)
def test_rename_title_only_files_falls_back_to_the_file_artist_tag(
    tmp_path: Path, suffix: str, artist: str
) -> None:
    audio = tmp_path / f"Song{suffix}"
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
            f"artist={artist}",
            str(audio),
        ],
        check=True,
    )

    rename_title_only_files(tmp_path, "Song", {}, tmp_path / "history.jsonl")

    assert not audio.exists()
    assert (tmp_path / f"Song - {render_filename_stem('', artist)}{suffix}").exists()


def test_rename_title_only_files_leaves_file_alone_when_artist_is_unknown(tmp_path: Path) -> None:
    audio = tmp_path / "Song.mp3"
    audio.write_bytes(b"not audio")

    rename_title_only_files(tmp_path, "Song", {}, tmp_path / "history.jsonl")

    assert audio.exists()


def test_rename_title_only_files_leaves_file_alone_when_target_exists(tmp_path: Path) -> None:
    audio = tmp_path / "Song.mp3"
    audio.touch()
    (tmp_path / "Song - The Beatles.mp3").touch()
    entry = _history_entry("old-id", "Song", "The Beatles", audio)

    rename_title_only_files(tmp_path, "Song", {str(audio): entry}, tmp_path / "history.jsonl")

    assert audio.exists()
    assert not (tmp_path / "history.jsonl").exists()


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


def test_download_command_renames_the_bare_file_before_downloading(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """The existing title-only file is renamed before yt-dlp chooses its filename."""
    output_path = tmp_path / "music"
    output_path.mkdir()
    bare_file = output_path / "Song.mp3"
    bare_file.touch()
    history_path = tmp_path / "history.jsonl"
    entry = _history_entry("old-id", "Song", "The Beatles", bare_file)
    history_path.write_text(json.dumps(entry) + "\n")

    downloaded_name = "Song - Other Artist.mp3"
    seen = []

    class FakeYoutubeDL:
        def __init__(self, options: dict) -> None:
            self.params = options

        def __enter__(self):
            return self

        def __exit__(self, *_args) -> None:
            return None

        def extract_info(self, *_args, **_kwargs):
            seen.append(
                {
                    "outtmpl": self.params["outtmpl"]["default"],
                    "renamed_first": (output_path / "Song - The Beatles.mp3").exists(),
                }
            )
            (output_path / downloaded_name).touch()
            return {
                "duration": 100,
                "requested_downloads": [{"filepath": str(output_path / downloaded_name)}],
            }

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
    video = {"id": "new-id", "title": "Song", "artist": "Other Artist"}
    monkeypatch.setattr(download_module, "get_video_info", lambda *_args: ([video], False))
    monkeypatch.setattr(download_module, "confirm_duplicate_download", lambda *_args: True)
    monkeypatch.setattr(download_module.yt_dlp, "YoutubeDL", FakeYoutubeDL)

    download_module.download_command(args)

    assert seen == [
        {
            "outtmpl": str(output_path / "%(title)s - %(artist,channel,uploader)s.%(ext)s"),
            "renamed_first": True,
        }
    ]
    assert not bare_file.exists()
    assert (output_path / "Song - The Beatles.mp3").exists()

    recorded = [json.loads(line) for line in history_path.read_text().splitlines()]
    assert [item["id"] for item in recorded] == ["old-id", "old-id", "new-id"]
    assert recorded[1]["file_path"] == str(output_path / "Song - The Beatles.mp3")
    assert recorded[2]["file_path"] == str(output_path / downloaded_name)
