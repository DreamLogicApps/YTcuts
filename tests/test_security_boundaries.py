import unittest

from pydantic import ValidationError

from backend.downloader import DownloadTask
from backend.metadata import validate_youtube_url
from backend.routes.download import DownloadRequest


class SecurityBoundaryTests(unittest.TestCase):
    def test_accepts_supported_youtube_urls(self):
        self.assertEqual(
            validate_youtube_url("https://youtu.be/dQw4w9WgXcQ"),
            "https://youtu.be/dQw4w9WgXcQ",
        )
        self.assertEqual(
            validate_youtube_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ"),
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        )

    def test_rejects_non_youtube_targets(self):
        for url in (
            "http://127.0.0.1:8000/secret",
            "https://example.com/video",
            "file:///etc/passwd",
        ):
            with self.assertRaises(ValueError):
                validate_youtube_url(url)

    def test_download_request_rejects_invalid_ranges(self):
        with self.assertRaises(ValidationError):
            DownloadRequest(
                url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                start_time="00:01:00",
                end_time="00:00:30",
            )

    def test_time_parser_rejects_malformed_clock_values(self):
        with self.assertRaises(ValueError):
            DownloadTask.parse_time("01:60")
        self.assertEqual(DownloadTask.parse_time("01:02:03"), 3723)


if __name__ == "__main__":
    unittest.main()
