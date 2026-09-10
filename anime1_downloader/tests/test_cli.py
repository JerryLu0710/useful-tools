"""Tests for Anime1 Downloader command outcomes."""

import pytest

from anime1_downloader import cli


def test_main_propagates_downloader_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    class FailingDownloader:
        def __init__(self, _args) -> None:
            pass

        def run(self) -> int:
            return 1

    monkeypatch.setattr(cli, "Anime1Downloader", FailingDownloader)

    assert cli.main(["https://anime1.me/18305"]) == 1


def test_main_returns_failure_for_unhandled_error(monkeypatch: pytest.MonkeyPatch) -> None:
    class BrokenDownloader:
        def __init__(self, _args) -> None:
            raise RuntimeError("unexpected")

    monkeypatch.setattr(cli, "Anime1Downloader", BrokenDownloader)

    assert cli.main(["https://anime1.me/18305"]) == 1
