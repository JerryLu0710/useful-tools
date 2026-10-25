"""Parser tests for anime1.me page and API responses.

The page fixture is a snapshot of https://anime1.me/18305 taken on 2026-10-25 with a
plain browser user agent and trimmed to the <article> the parser reads. The API
fixture is that page's real response from https://v.anime1.me/api. When these tests
start failing, the site's markup or payload changed: re-record the fixtures rather
than loosening the assertions.
"""

import json
from argparse import Namespace
from pathlib import Path

import pytest

from anime1_downloader import cli

FIXTURES = Path(__file__).parent / "fixtures"

# The data-apireq attribute of the recorded page, which is the whole request body.
APIREQ = (
    "%7B%22c%22%3A%221066%22%2C%22e%22%3A%229%22%2C%22t%22%3A1792931335%2C%22p%22%3A2"
    "%2C%22s%22%3A%223b0f3c9de3fbd741074b785a9bcd23cc%22%7D"
)


class FakeCookies:
    def __init__(self, values: dict) -> None:
        self._values = values

    def get_dict(self) -> dict:
        return dict(self._values)


class FakeResponse:
    def __init__(self, *, status_code: int = 200, text: str = "", cookies: dict | None = None):
        self.status_code = status_code
        self.text = text
        self.content = text.encode("utf-8")
        self.cookies = FakeCookies(cookies or {})

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise cli.requests.HTTPError(f"HTTP {self.status_code}", response=self, request=None)


class FakeSession:
    """Stands in for requests.Session so the parser is tested without the network."""

    def __init__(self, response: FakeResponse) -> None:
        self._response = response
        self.cookies = response.cookies
        self.calls: list[tuple] = []

    def get(self, *args, **kwargs) -> FakeResponse:
        self.calls.append(("get", args, kwargs))
        return self._response

    def post(self, *args, **kwargs) -> FakeResponse:
        self.calls.append(("post", args, kwargs))
        return self._response


@pytest.fixture
def sessions(monkeypatch: pytest.MonkeyPatch):
    """Install a fake session factory and hand back the responses it will serve."""

    def install(*responses: FakeResponse) -> list[FakeSession]:
        made: list[FakeSession] = []
        queue = list(responses)

        def factory() -> FakeSession:
            session = FakeSession(queue.pop(0) if queue else FakeResponse())
            made.append(session)
            return session

        monkeypatch.setattr(cli.requests, "Session", factory)
        return made

    return install


def _downloader(tmp_path: Path) -> cli.Anime1Downloader:
    return cli.Anime1Downloader(
        Namespace(
            url="https://anime1.me/18305",
            extract=True,
            cloudflare=None,
            user_agent=None,
            output_dir=tmp_path,
            max_concurrent_downloads=4,
            history=None,
            force=False,
        )
    )


def test_extract_api_path_pairs_the_title_with_its_request(sessions, tmp_path: Path) -> None:
    page = (FIXTURES / "anime1_page.html").read_text(encoding="utf-8")
    sessions(FakeResponse(text=page))

    merged = _downloader(tmp_path)._extract_api_path()

    assert merged == [("Lycoris Recoil 莉可麗絲 [09]", APIREQ)]


def test_extract_api_path_reports_a_cloudflare_block(sessions, tmp_path: Path) -> None:
    sessions(FakeResponse(status_code=403, text="<html>Just a moment</html>"))

    assert _downloader(tmp_path)._extract_api_path() is None


def test_extract_api_path_refuses_a_page_with_unpaired_nodes(sessions, tmp_path: Path) -> None:
    """One title per player is the only way episodes can be matched to files."""
    page = (
        '<h2 class="entry-title">A [01]</h2><h2 class="entry-title">A [02]</h2>'
        f'<video class="video-js" data-apireq="{APIREQ}"></video>'
    )
    sessions(FakeResponse(text=page))

    assert _downloader(tmp_path)._extract_api_path() is None


def test_extract_api_path_reports_a_page_without_a_player(sessions, tmp_path: Path) -> None:
    sessions(FakeResponse(text='<h2 class="entry-title">A [01]</h2>'))

    assert _downloader(tmp_path)._extract_api_path() is None


def test_get_source_asks_the_api_with_the_page_attribute(sessions, tmp_path: Path) -> None:
    """The API returns the HLS playlist first and the plain file second."""
    payload = (FIXTURES / "anime1_api.json").read_text(encoding="utf-8")
    session_cookies = {"e": "1792960135", "p": "placeholder", "h": "placeholder"}
    made = sessions(FakeResponse(text=payload, cookies=session_cookies))

    src, cookies = _downloader(tmp_path)._get_source(APIREQ)

    assert src == "//suisei.v.anime1.me/1066/9/playlist.m3u8"
    assert set(cookies) == {"e", "p", "h"}
    assert made[0].calls[0][:2] == ("post", ("https://v.anime1.me/api",))
    assert made[0].calls[0][2]["data"] == "d=" + APIREQ


def test_get_source_raises_when_the_api_returns_no_source(sessions, tmp_path: Path) -> None:
    sessions(FakeResponse(text=json.dumps({"s": []})))

    with pytest.raises(IndexError):
        _downloader(tmp_path)._get_source(APIREQ)


def test_get_source_raises_on_an_api_http_error(sessions, tmp_path: Path) -> None:
    sessions(FakeResponse(status_code=500, text="server error"))

    with pytest.raises(cli.requests.HTTPError):
        _downloader(tmp_path)._get_source(APIREQ)
