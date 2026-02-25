# edited from: https://github.com/SodaWithoutSparkles/anime1.me-dl
import argparse
import concurrent.futures
import json
import logging
import os
from pathlib import Path

import requests
from bs4 import BeautifulSoup

from logger_setup import get_logger

from .config import AnimeDownloaderConfig
from .history import append_to_history, create_history_entry, load_history

# Setup project-wide logger
logger = get_logger(__name__, "anime1_downloader")


class Anime1Downloader:
    """A class to download videos from anime1.me."""

    def __init__(self, args):
        """Initialize the downloader with command-line arguments."""
        self.args = args
        self.downloaded_titles: set[str] = set()
        self.history_path = Path(args.history) if args.history else None

    def _merge_lists(self, list1, list2):
        """
        Merges elements of two lists into a list of tuples in order.
        For example: [a, b], [1, 2] -> [(a, 1), (b, 2)]
        """
        return list(map(lambda x, y: (x, y), list1, list2))

    def _extract_api_path(self):
        """
        Extracts video titles and corresponding API request data (data-apireq)
        from a given anime1.me URL.
        """
        video_class = "video-js"
        title_class = "entry-title"

        headers = {"User-Agent": self.args.user_agent} if self.args.user_agent else {}
        cookies = {"cf_clearance": self.args.cloudflare} if self.args.cloudflare else {}

        session = requests.Session()

        if self.args.user_agent and self.args.cloudflare:
            resp = session.get(self.args.url, headers=headers, cookies=cookies)
        elif self.args.user_agent or self.args.cloudflare:
            logger.error("Cloudflare detection requires both User-Agent and cf_clearance")
            logger.error("Using only one may not bypass detection")
            return None
        else:
            logger.warning(
                "User-Agent and cf_clearance are missing, Cloudflare may block the request"
            )
            resp = session.get(self.args.url)

        if resp.status_code == 403:
            logger.error("Fatal: Blocked by Cloudflare")
            return None

        soup = BeautifulSoup(resp.text, "lxml")

        list_of_titles = soup.find_all(attrs={"class": title_class})
        list_of_videos = soup.find_all(attrs={"class": video_class})

        titles = [title_tag.get_text() for title_tag in list_of_titles]
        videos = [
            video_tag.get("data-apireq")
            for video_tag in list_of_videos
            if video_tag.get("data-apireq")
        ]

        if not videos:
            logger.error("Fatal: Could not find data-apireq, aborting")
            return None

        if not titles:
            logger.error("Fatal: Could not find title, aborting")
            return None

        if len(titles) != len(videos):
            logger.error("Fatal: Mismatch between number of videos and titles")
            return None

        merged = self._merge_lists(titles, videos)

        for item in merged:
            logger.info("Title: %s", item[0])
            logger.debug("- data-apireq: %s", item[1])

        return merged

    def _get_source(self, video_data_apireq):
        """
        Fetches the actual video stream URL and associated cookies from the
        anime1.me API based on data-apireq.
        """
        data_raw = "d=" + video_data_apireq
        session = requests.Session()

        response = session.post(
            "https://v.anime1.me/api",
            data=data_raw,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        try:
            response.raise_for_status()
        except requests.HTTPError:
            logger.error(
                "API request failed, status code: %s, content: %s",
                response.status_code,
                response.text,
            )
            raise

        result = json.loads(response.content.decode("utf-8"))

        try:
            logger.debug("Source: https:%s", str(result["s"][0]["src"]))
        except Exception:
            logger.debug("Source unknown, raw API response: %s", response.content.decode("utf-8"))
        logger.debug("cookie: %s", session.cookies.get_dict())
        logger.debug("raw API response: %s", response.content.decode("utf-8"))

        try:
            src = result["s"][0]["src"]
        except (KeyError, IndexError, TypeError) as e:
            logger.error("Failed to parse source: %s; response: %s", e, result)
            raise

        return src, session.cookies.get_dict()

    def _download_video(self, src, cookie, title, anime_series_name):
        """Downloads a video using the yt-dlp library."""
        import yt_dlp

        src = "https:" + src

        dict_cookie = cookie or {}
        try:
            e = dict_cookie["e"]
            h = dict_cookie["h"]
            p = dict_cookie["p"]
        except KeyError as ke:
            logger.error("Missing required cookie field: %s, cookies=%s", ke, dict_cookie)
            raise

        all_cookies_str = f"e={e};h={h};p={p}"
        yt_dlp_cookie_dict = {"cookie": all_cookies_str}

        final_output_dir = os.path.join(self.args.output_dir, anime_series_name)
        os.makedirs(final_output_dir, exist_ok=True)

        ydl_opts = {
            "concurrent_fragment_downloads": 32,
            "http_headers": yt_dlp_cookie_dict,
            "verbose": logger.isEnabledFor(logging.DEBUG),
            "outtmpl": title + ".%(ext)s",
            "paths": {"home": final_output_dir},
        }

        logger.debug("yt-dlp options: %s", ydl_opts)
        logger.info("Passing info for '%s' to yt-dlp for download...", title)

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([src])

    def _process_single_episode(self, video_tuple, anime_series_name):
        """
        Processes a single video entry (gets source and potentially downloads),
        runs in a thread pool.
        """
        title, data_apireq = video_tuple

        # Check if already downloaded (skip unless --force)
        if self.history_path and not self.args.force and title in self.downloaded_titles:
            logger.info("[%-20s] Already downloaded, skipping", title)
            return

        try:
            logger.info("[%-20s] Start processing", title)
            src, cookie = self._get_source(data_apireq)
            if not self.args.extract:
                self._download_video(src, cookie, title, anime_series_name)
                logger.info("[%-20s] Download complete", title)

                # Record to history
                if self.history_path:
                    output_path = os.path.join(self.args.output_dir, anime_series_name, title)
                    entry = create_history_entry(
                        title=title,
                        anime_series=anime_series_name,
                        url=self.args.url,
                        output_path=output_path,
                    )
                    append_to_history(self.history_path, entry)
                    self.downloaded_titles.add(title)
                    logger.debug("[%-20s] Added to history", title)
            else:
                logger.info("[%-20s] Information extracted", title)
                logger.info(" - Source URL: https:%s", src)
                logger.info(" - Cookie: %s", cookie)
                expected_full_path = os.path.join(
                    self.args.output_dir, anime_series_name, title + "."
                )
                logger.info(" - Expected output path: %s", expected_full_path)
        except Exception:
            logger.exception("Failed to process '%s'", title)

    def run(self):
        """Main execution method for the downloader."""
        logger.info("Extracting information from %s", self.args.url)

        # Load history if enabled
        if self.history_path:
            logger.info("Loading download history from %s", self.history_path)
            self.downloaded_titles = load_history(self.history_path)
            if self.downloaded_titles:
                logger.info("Found %d previously downloaded episodes", len(self.downloaded_titles))

        videos = self._extract_api_path()
        if not videos:
            logger.error("No videos found on the page. Cannot continue.")
            return

        first_video_title = videos[0][0]
        anime_series_name_parts = first_video_title.split(" [")
        if len(anime_series_name_parts) > 1:
            anime_series_name = anime_series_name_parts[0].strip()
        else:
            anime_series_name = first_video_title.strip()

        logger.info("Detected anime series name: '%s'", anime_series_name)
        logger.info(
            "Using output directory: '%s'", os.path.join(self.args.output_dir, anime_series_name)
        )
        logger.info("Max concurrent downloads: %d", self.args.max_concurrent_downloads)
        if self.history_path:
            logger.info("History file: %s", self.history_path)
        logger.info("_")

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=self.args.max_concurrent_downloads, thread_name_prefix="dl"
        ) as executor:
            futures = [
                executor.submit(self._process_single_episode, video, anime_series_name)
                for video in videos
            ]

            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                except Exception:
                    logger.exception("An unhandled exception occurred in a video processing task")


def create_parser():
    """Creates and configures the argument parser."""
    parser = argparse.ArgumentParser(
        "anime1_downloader",
        formatter_class=argparse.RawTextHelpFormatter,
        description="Downloads videos from anime1.me using a static parser with requests and beautifulsoup.",
    )
    parser.add_argument(
        "url",
        help="A direct URL to an anime1.me page, e.g., https://anime1.me/18305\nYou may need to wrap this in quotes",
    )
    parser.add_argument(
        "-x", "--extract", action="store_true", help="Only extract URLs, do not download"
    )
    parser.add_argument(
        "-cf",
        "--cloudflare",
        help="Set cf_clearance cookie to bypass Cloudflare detection\nThis cookie is valid for one hour\nYou may need to wrap this in quotes",
        metavar="COOKIE",
    )
    parser.add_argument("-ua", "--user-agent", help="Set user-agent to bypass detection")
    parser.add_argument(
        "-o",
        "--output-dir",
        help=f"Set the base output directory for downloaded videos. Final path will be <DIR>/<anime_series_name>/. Default: {AnimeDownloaderConfig.DOWNLOAD_DIR}",
        default=AnimeDownloaderConfig.DOWNLOAD_DIR,
        metavar="DIR",
    )
    parser.add_argument(
        "-j",
        "--max-concurrent-downloads",
        type=int,
        default=AnimeDownloaderConfig.MAX_CONCURRENT_DOWNLOADS,
        help=f"Maximum number of concurrent video downloads. Default is {AnimeDownloaderConfig.MAX_CONCURRENT_DOWNLOADS}.",
    )
    parser.add_argument(
        "--history",
        help=f"Path to JSONL history file for tracking downloads. Default: {AnimeDownloaderConfig.DEFAULT_HISTORY_FILE}",
        default=AnimeDownloaderConfig.DEFAULT_HISTORY_FILE,
        metavar="FILE",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Download even if already in history",
    )
    return parser


def main():
    """Main entry point for the script."""
    parser = create_parser()
    args = parser.parse_args()
    try:
        downloader = Anime1Downloader(args)
        downloader.run()
    except Exception:
        logger.exception("---- UNHANDLED ERROR ----")
    finally:
        logger.info("Complete")


if __name__ == "__main__":
    main()
