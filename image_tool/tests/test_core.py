from pathlib import Path

import pytest

from image_tool import cli, core


class FakeVideoCapture:
    def __init__(self, *, opened: bool = True, read_result: tuple[bool, object] = (True, "frame")):
        self.opened = opened
        self.read_result = read_result
        self.released = False
        self.position = None

    def isOpened(self) -> bool:
        return self.opened

    def get(self, property_id: int) -> float:
        if property_id == core.cv2.CAP_PROP_FPS:
            return 30.0
        return 120.0

    def set(self, property_id: int, value: int) -> None:
        self.position = (property_id, value)

    def read(self) -> tuple[bool, object]:
        return self.read_result

    def release(self) -> None:
        self.released = True


def test_extract_frame_writes_requested_frame(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    video = FakeVideoCapture()
    monkeypatch.setattr(core.cv2, "VideoCapture", lambda _path: video)
    monkeypatch.setattr(core.cv2, "imwrite", lambda _path, _frame: True)

    output_path = core.extract_frame("video.mp4", 2, tmp_path)

    assert output_path == str(tmp_path / "frame_at_2s.jpg")
    assert video.position == (core.cv2.CAP_PROP_POS_FRAMES, 60)
    assert video.released


def test_extract_frame_releases_unopenable_video(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    video = FakeVideoCapture(opened=False)
    monkeypatch.setattr(core.cv2, "VideoCapture", lambda _path: video)

    with pytest.raises(OSError, match="Could not open video"):
        core.extract_frame("missing.mp4", 2, tmp_path)

    assert video.released


def test_extract_frame_rejects_timestamp_after_end(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    video = FakeVideoCapture()
    monkeypatch.setattr(core.cv2, "VideoCapture", lambda _path: video)

    with pytest.raises(ValueError, match="shorter"):
        core.extract_frame("video.mp4", 4, tmp_path)

    assert video.released


def test_frame_cli_returns_failure_for_extraction_error(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(core, "extract_frame", lambda *_args: (_ for _ in ()).throw(OSError("bad")))

    assert (
        cli.main(["frame", "--video", "video.mp4", "--time", "1", "--output", str(tmp_path)]) == 1
    )


def test_frame_cli_returns_success_for_extracted_frame(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(core, "extract_frame", lambda *_args: str(tmp_path / "frame.jpg"))

    assert (
        cli.main(["frame", "--video", "video.mp4", "--time", "1", "--output", str(tmp_path)]) == 0
    )
